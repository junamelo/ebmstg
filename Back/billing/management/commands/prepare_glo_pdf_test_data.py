from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import User
from billing.models import Company, Invoice
from billing.services.pdf_processor import PDFProcessor


class Command(BaseCommand):
    help = 'Cree les factures globales EN_COURS correspondant au PDF GLO de juin 2026.'

    def handle(self, *args, **options):
        path = Path(settings.BASE_DIR).parent / 'Contexte' / 'testPDF' / 'PHYS.OPN.202606.GLO-1-70.pdf'
        if not path.is_file():
            raise CommandError(f'PDF introuvable : {path}')
        with path.open('rb') as pdf_file:
            result = PDFProcessor.analyze_global_pdf_structure(pdf_file)
        if not result['success']:
            raise CommandError(result.get('error', 'Analyse GLO impossible'))

        created_companies = created_invoices = 0
        with transaction.atomic():
            for block in result['blocks']:
                identifiers = block['identifiers']
                account = identifiers['compte']
                payer, payer_created = User.objects.get_or_create(
                    username=f'glo_payeur_{account.lower()}',
                    defaults={'email': f'glo.payeur.{account.lower()}@test.moov.local', 'role': 'PAYEUR',
                              'first_name': 'Payeur', 'last_name': account, 'status': 'ACTIF', 'est_actif': True}
                )
                if payer_created:
                    payer.set_password('TestGlo2026!')
                    payer.save(update_fields=['password'])
                company, company_created = Company.objects.get_or_create(
                    compte=account,
                    defaults={'raison_sociale': f'Entreprise GLO {account}', 'categorie': 'PE',
                              'statut': 'ACTIF', 'payeur': payer}
                )
                if company_created:
                    created_companies += 1
                number = identifiers.get('numero_facture') or f'GLO-202606-{account}'
                _, invoice_created = Invoice.objects.update_or_create(
                    numero_facture=number,
                    defaults={'company': company, 'line': None, 'periode_debut': date(2026, 6, 1),
                              'periode_fin': date(2026, 6, 30), 'date_echeance': date(2026, 7, 30),
                              'montant_ht': 0, 'montant_tva': 0, 'montant_ttc': 0, 'statut': 'EN_COURS',
                              'fichier_pdf': None, 'commentaire': '[TEST GLO 202606] Facture globale de test.'}
                )
                created_invoices += int(invoice_created)
        self.stdout.write(self.style.SUCCESS(
            f'Jeu GLO pret : {len(result["blocks"])} factures globales, {created_companies} entreprises creees, {created_invoices} factures creees.\n'
            'Payeur des nouvelles entreprises : glo_payeur_<compte> / TestGlo2026!'
        ))
