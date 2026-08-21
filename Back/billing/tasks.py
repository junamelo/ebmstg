"""Tâches asynchrones de facturation.

Les traitements PDF seront déplacés ici progressivement afin que les requêtes
HTTP ne restent pas bloquées pendant le découpage.
"""

import json
from decimal import Decimal
from uuid import uuid4

from celery import shared_task
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum
from django.utils import timezone

from .models import HistoriqueFacturation, Invoice, Publication, TraitementPDF


@shared_task(name='billing.verifier_garnet')
def verifier_garnet():
    """Tâche non métier servant à valider Garnet + Celery de bout en bout."""
    key = f'celery-health:{uuid4()}'
    cache.set(key, 'ok', timeout=60)
    return {
        'broker': 'Garnet',
        'cache_roundtrip': cache.get(key) == 'ok',
    }


@shared_task(name='billing.envoyer_notifications_factures')
def envoyer_notifications_factures(invoice_ids):
    """Envoie les e-mails de disponibilitÃ© hors de la requÃªte de publication.

    Le canal SMS est volontairement dÃ©sactivÃ© : seule la notification e-mail
    reste disponible dans l'application.
    """
    from .services.notification_service import notifier_facture

    notifications = []
    for invoice in Invoice.objects.filter(id__in=invoice_ids).select_related('company', 'line', 'line__employe'):
        notifications.extend(notifier_facture(invoice, ['EMAIL']))

    return {
        'demandee': True,
        'envoyees': sum(item.statut == 'ENVOYEE' for item in notifications),
        'non_configurees': sum(item.statut == 'NON_CONFIGUREE' for item in notifications),
        'echecs': sum(item.statut == 'ECHEC' for item in notifications),
    }


def _json_safe(value):
    """Garantit qu'un résultat de traitement peut être stocké en JSON."""
    return json.loads(json.dumps(value, cls=DjangoJSONEncoder))


@shared_task(bind=True, name='billing.traiter_import_pdf')
def traiter_import_pdf(self, traitement_id):
    """Découpe un PDF puis rattache les factures hors du cycle HTTP."""
    try:
        traitement = TraitementPDF.objects.select_related('agent').get(id=traitement_id)
    except TraitementPDF.DoesNotExist:
        return {'error': 'Traitement PDF introuvable.'}

    if traitement.statut == TraitementPDF.Statut.TERMINE:
        return traitement.resultat

    traitement.statut = TraitementPDF.Statut.EN_COURS
    traitement.progression = 5
    traitement.date_debut = timezone.now()
    traitement.erreur = ''
    traitement.save(update_fields=['statut', 'progression', 'date_debut', 'erreur'])

    try:
        from .services.pdf_processor import PDFMatcher, PDFProcessor

        PDFProcessor.check_dependencies()
        traitement.progression = 15
        traitement.save(update_fields=['progression'])

        # Le FileField est rouvert dans le worker : le fichier reste donc disponible
        # même après la fin de la requête HTTP d'upload.
        with traitement.fichier_source.open('rb') as fichier:
            result = (
                PDFProcessor.process_global_pdf(fichier)
                if traitement.type_facture == 'GLO'
                else PDFProcessor.process_bulk_pdf(fichier)
            )

        if not result.get('success'):
            erreur = result.get('error', 'Erreur lors du traitement du PDF')
            payload = {
                'error': erreur,
                'warnings': result.get('warnings', []),
                'errors_per_page': result.get('errors_per_page', []),
                'split_errors': result.get('split_errors', []),
            }
            traitement.statut = TraitementPDF.Statut.ECHEC
            traitement.progression = 100
            traitement.erreur = erreur
            traitement.resultat = _json_safe(payload)
            traitement.date_fin = timezone.now()
            traitement.save(update_fields=['statut', 'progression', 'erreur', 'resultat', 'date_fin'])
            return traitement.resultat

        traitement.progression = 65
        traitement.save(update_fields=['progression'])
        response_data = {
            'message': 'PDF traité avec succès',
            'summary': {
                'total_pages': result['total_pages'],
                'blocks_detected': result['total_blocks'],
                'files_created': result['files_created'],
            },
            'warnings': result.get('warnings', []),
            'errors_per_page': result.get('errors_per_page', []),
            'split_errors': result.get('split_errors', []),
        }

        if traitement.auto_match:
            invoices_query = Invoice.objects.filter(statut='EN_COURS')
            processed_invoices_query = Invoice.objects.exclude(statut='EN_COURS')
            if traitement.type_facture == 'GLO':
                invoices_query = invoices_query.filter(line__isnull=True)
                processed_invoices_query = processed_invoices_query.filter(line__isnull=True)

            # Les blocs de démonstration utilisent le cycle technique TEST :
            # il ne doit pas filtrer les lignes métier HYB/OP avant le matching.
            if traitement.cycle in {'HYB', 'OP'} and traitement.type_facture != 'GLO':
                invoices_query = invoices_query.filter(company__lines__cycle=traitement.cycle).distinct()
                processed_invoices_query = processed_invoices_query.filter(company__lines__cycle=traitement.cycle).distinct()

            if traitement.periode_debut and traitement.periode_fin:
                invoices_query = invoices_query.filter(
                    periode_debut=traitement.periode_debut,
                    periode_fin=traitement.periode_fin,
                )
                processed_invoices_query = processed_invoices_query.filter(
                    periode_debut=traitement.periode_debut,
                    periode_fin=traitement.periode_fin,
                )

            match_result = PDFMatcher.auto_attach_pdfs(
                result['files'], invoices_query, processed_invoices_query,
                invoice_type=traitement.type_facture,
            )
            response_data['matching'] = {
                'total_files': match_result['total_files'],
                'successfully_matched': match_result['matched'],
                'not_matched': match_result['not_matched'],
                'skipped_already_processed': len(match_result.get('skipped', [])),
                'details': {
                    'attached': match_result['attached'],
                    'skipped': match_result['skipped'],
                    'errors': match_result['errors'],
                },
            }

            for attached in match_result['attached']:
                invoice = Invoice.objects.filter(id=attached['invoice_id']).first()
                if invoice:
                    HistoriqueFacturation.objects.create(
                        invoice=invoice,
                        utilisateur=traitement.agent,
                        type_action='MODIFICATION',
                        ancien_statut='EN_COURS',
                        nouveau_statut=invoice.statut,
                        commentaire=f'PDF attaché automatiquement : {attached["filename"]}',
                    )

            # La publication finale reste une action manuelle. Cette ligne est
            # seulement une trace de l'import dans l'historique des publications.
            if (
                traitement.cycle and traitement.periode_debut and traitement.periode_fin
                and match_result['matched'] > 0
            ):
                attached_ids = [item['invoice_id'] for item in match_result['attached']]
                montant_total = Invoice.objects.filter(id__in=attached_ids).aggregate(
                    total=Sum('montant_ttc')
                )['total'] or Decimal('0')
                publication = Publication.objects.create(
                    agent=traitement.agent,
                    cycle_facturation=traitement.cycle,
                    periode_debut=traitement.periode_debut,
                    periode_fin=traitement.periode_fin,
                    statut='VALIDEE',
                    nombre_lignes_traitees=match_result['matched'],
                    montant_total=montant_total,
                    commentaire=(
                        f"{'Bloc PDF de test' if traitement.cycle == 'TEST' else 'Import PDF'} : "
                        f"{result['files_created']} fichier(s) créé(s), "
                        f"{match_result['matched']} facture(s) associée(s), "
                        f"{match_result['not_matched']} sans correspondance."
                    ),
                )
                response_data['import_trace'] = {
                    'id': str(publication.id),
                    'note': "Cette trace documente l'import, PAS la publication finale",
                }
        else:
            response_data['files_without_matching'] = [
                {'filename': item['filename'], 'identifiers': item['identifiers'], 'pages': item['pages']}
                for item in result['files']
            ]
            response_data['message'] += ' (Matching automatique désactivé)'

        traitement.statut = TraitementPDF.Statut.TERMINE
        traitement.progression = 100
        traitement.resultat = _json_safe(response_data)
        traitement.date_fin = timezone.now()
        traitement.save(update_fields=['statut', 'progression', 'resultat', 'date_fin'])
        return traitement.resultat
    except Exception as exc:
        erreur = f'{type(exc).__name__} : {exc}'
        traitement.statut = TraitementPDF.Statut.ECHEC
        traitement.progression = 100
        traitement.erreur = erreur
        traitement.resultat = {'error': 'Erreur lors du traitement du PDF.'}
        traitement.date_fin = timezone.now()
        traitement.save(update_fields=['statut', 'progression', 'erreur', 'resultat', 'date_fin'])
        raise
