"""Prépare un jeu de données réinitialisable pour le PDF SOM de juin 2026."""
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import User
from billing.models import Company, Invoice, Line, Publication
from billing.services.pdf_processor import PDFProcessor


class Command(BaseCommand):
    help = (
        "Crée les entreprises, lignes, employés et factures EN_COURS "
        "correspondant au PDF SOM de juin 2026."
    )

    period_start = date(2026, 6, 1)
    period_end = date(2026, 6, 30)
    due_date = date(2026, 7, 30)
    password = "TestSom2026!"

    def add_arguments(self, parser):
        parser.add_argument(
            "--pdf-path",
            default=str(
                Path(settings.BASE_DIR).parent
                / "Contexte" / "testPDF" / "PHYS.OPN.202606.SOM-1-70.pdf"
            ),
            help="Chemin du PDF SOM à analyser.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Supprime les factures et traces d'import OP de juin 2026 avant la préparation.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Affiche les données détectées sans modifier la base.",
        )

    def handle(self, *args, **options):
        pdf_path = Path(options["pdf_path"])
        if not pdf_path.is_file():
            raise CommandError(f"PDF introuvable : {pdf_path}")

        with pdf_path.open("rb") as pdf_file:
            analysis = PDFProcessor.analyze_pdf_structure(pdf_file)
        if not analysis.get("success"):
            raise CommandError(analysis.get("error", "Analyse PDF impossible."))

        entries = []
        seen_msisdn = set()
        for block in analysis.get("blocks", []):
            identifiers = block.get("identifiers", {})
            msisdn = identifiers.get("msisdn")
            compte = identifiers.get("compte")
            if not msisdn or not compte:
                continue
            if msisdn not in seen_msisdn:
                entries.append({"msisdn": msisdn, "compte": compte})
                seen_msisdn.add(msisdn)

        if not entries:
            raise CommandError("Aucun couple MSISDN/compte n'a été détecté dans le PDF SOM.")

        accounts = {entry["compte"] for entry in entries}
        self.stdout.write(
            f"PDF analysé : {len(analysis['blocks'])} pages, "
            f"{len(entries)} lignes, {len(accounts)} entreprises."
        )

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Mode simulation : aucune donnée modifiée."))
            for account in sorted(accounts):
                count = sum(1 for entry in entries if entry["compte"] == account)
                self.stdout.write(f"- {account} : {count} ligne(s)")
            return

        with transaction.atomic():
            if options["reset"]:
                self._reset_previous_imports(accounts)

            stats = self._create_dataset(entries)

        self.stdout.write(self.style.SUCCESS("Jeu de test SOM prêt."))
        self.stdout.write(
            "Créés/mis à jour — entreprises : {companies}, payeurs : {payers}, "
            "employés : {employees}, lignes : {lines}, factures EN_COURS : {invoices}.".format(**stats)
        )
        self.stdout.write(
            "Comptes de test : som_payeur_<compte> et som_emp_<msisdn> ; "
            f"mot de passe : {self.password}"
        )
        self.stdout.write(
            "Importez ensuite PHYS.OPN.202606.SOM-1-70.pdf avec le cycle OP "
            "et la période du 01/06/2026 au 30/06/2026."
        )

    def _reset_previous_imports(self, accounts):
        invoices = Invoice.objects.filter(
            company__compte__in=accounts,
            periode_debut=self.period_start,
            periode_fin=self.period_end,
        )
        invoice_count = invoices.count()
        for invoice in invoices.exclude(fichier_pdf=""):
            if invoice.fichier_pdf:
                invoice.fichier_pdf.delete(save=False)
        invoices.delete()

        publications = Publication.objects.filter(
            cycle_facturation="OP",
            periode_debut=self.period_start,
            periode_fin=self.period_end,
        )
        publication_count = publications.count()
        for publication in publications.exclude(fichier_pdf=""):
            if publication.fichier_pdf:
                publication.fichier_pdf.delete(save=False)
        publications.delete()

        self.stdout.write(
            self.style.WARNING(
                f"Réinitialisation ciblée : {invoice_count} facture(s) et "
                f"{publication_count} trace(s) d'import supprimées."
            )
        )

    def _create_dataset(self, entries):
        stats = {"companies": 0, "payers": 0, "employees": 0, "lines": 0, "invoices": 0}
        companies = {}

        for account in sorted({entry["compte"] for entry in entries}):
            payer, payer_created = User.objects.get_or_create(
                username=f"som_payeur_{account.lower()}",
                defaults={
                    "email": f"som.payeur.{account.lower()}@test.moov.local",
                    "role": "PAYEUR",
                    "telephone": None,
                    "first_name": "Payeur",
                    "last_name": account,
                    "is_active": True,
                    "est_actif": True,
                    "status": "ACTIF",
                },
            )
            if payer_created:
                payer.set_password(self.password)
                payer.save(update_fields=["password"])
                stats["payers"] += 1

            company, company_created = Company.objects.get_or_create(
                compte=account,
                defaults={
                    "raison_sociale": f"Entreprise de test {account}",
                    "categorie": "PE",
                    "statut": "ACTIF",
                    "payeur": payer,
                },
            )
            if company_created:
                stats["companies"] += 1
            if company.payeur_id != payer.id:
                company.payeur = payer
                company.save(update_fields=["payeur", "date_modification"])
            companies[account] = company

        for entry in entries:
            msisdn = entry["msisdn"]
            employee, employee_created = User.objects.get_or_create(
                username=f"som_emp_{msisdn}",
                defaults={
                    "email": f"som.emp.{msisdn}@test.moov.local",
                    "role": "EMPLOYE",
                    "telephone": msisdn,
                    "first_name": "Employe",
                    "last_name": msisdn,
                    "is_active": True,
                    "est_actif": True,
                    "status": "ACTIF",
                },
            )
            if employee_created:
                employee.set_password(self.password)
                employee.save(update_fields=["password"])
                stats["employees"] += 1

            line, line_created = Line.objects.update_or_create(
                msisdn=msisdn,
                defaults={
                    "company": companies[entry["compte"]],
                    "utilisateur": f"Employe test {msisdn}",
                    "forfait": 0,
                    "cycle": "OP",
                    "statut": "ACTIF",
                    "employe": employee,
                },
            )
            if line_created:
                stats["lines"] += 1

            _, invoice_created = Invoice.objects.update_or_create(
                numero_facture=f"SOM-202606-{msisdn}",
                defaults={
                    "company": line.company,
                    "line": line,
                    "periode_debut": self.period_start,
                    "periode_fin": self.period_end,
                    "date_echeance": self.due_date,
                    "montant_ht": 0,
                    "montant_tva": 0,
                    "montant_ttc": 0,
                    "statut": "EN_COURS",
                    "fichier_pdf": None,
                    "commentaire": "[TEST SOM 202606] Facture individuelle générée pour le test de rapprochement PDF.",
                },
            )
            if invoice_created:
                stats["invoices"] += 1

        return stats
