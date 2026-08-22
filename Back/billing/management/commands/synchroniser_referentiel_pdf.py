"""Crée les contrats et lignes absents détectés dans un bloc SOM."""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from billing.models import Company, CycleFacturation, Line, TraitementPDF
from billing.services.pdf_processor import PDFProcessor


class Command(BaseCommand):
    help = (
        "Analyse les erreurs d'un traitement SOM et crée les contrats/lignes "
        "manquants à partir des comptes et MSISDN lus dans le PDF. "
        "Aucun compte utilisateur de connexion n'est créé."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--treatment",
            metavar="UUID",
            help="Identifiant du TraitementPDF SOM à analyser. Par défaut : le dernier traitement SOM terminé.",
        )
        parser.add_argument(
            "--cycle",
            choices=[CycleFacturation.OP, CycleFacturation.HYB],
            help="Cycle à attribuer aux lignes créées. Détecté depuis le nom du fichier si absent.",
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Exécute réellement les créations. Sans cette option, seule une simulation est affichée.",
        )

    @staticmethod
    def _cycle_par_defaut(traitement):
        nom = Path(traitement.fichier_source.name).name.upper()
        if traitement.cycle in {CycleFacturation.OP, CycleFacturation.HYB}:
            return traitement.cycle
        return CycleFacturation.OP if ('OPN' in nom or 'OPEN' in nom) else CycleFacturation.HYB

    def handle(self, *args, **options):
        traitements = TraitementPDF.objects.filter(type_facture='SOM').order_by('-date_creation')
        if options['treatment']:
            try:
                traitement = traitements.get(pk=options['treatment'])
            except TraitementPDF.DoesNotExist as error:
                raise CommandError("Traitement SOM introuvable.") from error
        else:
            traitement = traitements.filter(statut=TraitementPDF.Statut.TERMINE).first()
            if not traitement:
                raise CommandError("Aucun traitement SOM terminé n'a été trouvé.")

        errors = traitement.resultat.get('matching', {}).get('details', {}).get('errors', [])
        pairs = {
            (item.get('identifiers', {}).get('compte'), item.get('identifiers', {}).get('msisdn'))
            for item in errors
            if item.get('identifiers', {}).get('compte') and item.get('identifiers', {}).get('msisdn')
        }
        pairs.discard((None, None))
        if not pairs:
            raise CommandError("Aucun couple compte/MSISDN exploitable n'a été trouvé dans les erreurs du traitement.")

        cycle = options['cycle'] or self._cycle_par_defaut(traitement)
        references = {}
        try:
            with traitement.fichier_source.open('rb') as fichier:
                from PyPDF2 import PdfReader
                for page in PdfReader(fichier).pages:
                    identifiers = PDFProcessor.find_identifiers(PDFProcessor.extract_text_from_page(page))
                    key = (identifiers.get('compte'), identifiers.get('msisdn'))
                    if key in pairs and key not in references:
                        references[key] = identifiers
        except Exception as error:
            raise CommandError(f"Lecture du PDF source impossible : {error}") from error

        companies = {company.compte: company for company in Company.objects.filter(compte__in={key[0] for key in pairs})}
        lines = {line.msisdn: line for line in Line.objects.filter(msisdn__in={key[1] for key in pairs}).select_related('company')}
        contracts_to_create = {compte for compte, _ in pairs if compte not in companies}
        lines_to_create = []
        conflicts = []

        for compte, msisdn in sorted(pairs):
            existing_line = lines.get(msisdn)
            if existing_line and existing_line.company.compte != compte:
                conflicts.append({
                    'msisdn': msisdn,
                    'compte_pdf': compte,
                    'compte_existant': existing_line.company.compte,
                })
            elif not existing_line:
                lines_to_create.append((compte, msisdn))

        self.stdout.write(self.style.WARNING(f"Traitement : {traitement.id} — {Path(traitement.fichier_source.name).name}"))
        self.stdout.write(
            f"{len(pairs)} ligne(s) uniques détectées ; {len(contracts_to_create)} contrat(s) à créer ; "
            f"{len(lines_to_create)} ligne(s) à créer ; {len(conflicts)} conflit(s) de MSISDN ; cycle : {cycle}."
        )
        for compte, msisdn in sorted(pairs)[:10]:
            details = references.get((compte, msisdn), {})
            self.stdout.write(f"- {compte} | {msisdn} | {details.get('raison_sociale', 'Raison sociale à compléter')}")

        if not options['confirm']:
            self.stdout.write(self.style.WARNING("Simulation uniquement : aucune donnée n'a été créée. Ajoutez --confirm."))
            return

        created_companies = 0
        created_lines = 0
        with transaction.atomic():
            for compte in sorted(contracts_to_create):
                first_details = next(
                    (references.get((pair_compte, msisdn), {}) for pair_compte, msisdn in pairs if pair_compte == compte),
                    {},
                )
                raison_sociale = first_details.get('raison_sociale') or f"Client importé {compte}"
                companies[compte] = Company.objects.create(
                    compte=compte,
                    raison_sociale=raison_sociale,
                    statut='ACTIF',
                    statut_factures='EN_ATTENTE',
                    observation=(
                        "Contrat créé automatiquement depuis un bloc PDF SOM. "
                        "Les informations contractuelles doivent être complétées et validées."
                    ),
                )
                created_companies += 1

            for compte, msisdn in lines_to_create:
                Line.objects.create(
                    company=companies[compte],
                    msisdn=msisdn,
                    cycle=cycle,
                    statut='ACTIF',
                    utilisateur='',
                )
                created_lines += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Référentiel mis à jour : {created_companies} contrat(s) et {created_lines} ligne(s) créés. "
                f"{len(conflicts)} conflit(s) restent à corriger manuellement."
            )
        )
