"""Réinitialise les résultats de traitement PDF sans supprimer les contrats."""

from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from billing.models import (
    HistoriqueFacturation,
    Invoice,
    NotificationFacture,
    Publication,
    StatutFacture,
)


class Command(BaseCommand):
    help = (
        "Supprime les fichiers et traces de publication, puis remet les factures "
        "à EN_COURS pour pouvoir rejouer un import PDF. Les comptes, contrats, "
        "entreprises et lignes ne sont jamais supprimés."
    )

    def add_arguments(self, parser):
        scope = parser.add_mutually_exclusive_group(required=True)
        scope.add_argument(
            "--period",
            metavar="AAAA-MM",
            help="Réinitialise uniquement les factures et publications de cette période.",
        )
        scope.add_argument(
            "--all",
            action="store_true",
            help="Réinitialise toutes les factures de la base. À utiliser uniquement pour les tests.",
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirme l'exécution réelle. Sans cette option, la commande est une simulation.",
        )

    def handle(self, *args, **options):
        invoices = Invoice.objects.all()
        publications = Publication.objects.all()
        label = "toute la base de facturation"

        if options["period"]:
            try:
                period = datetime.strptime(options["period"], "%Y-%m")
            except ValueError as error:
                raise CommandError("La période doit respecter le format AAAA-MM (ex. 2026-06).") from error

            invoices = invoices.filter(
                periode_debut__year=period.year,
                periode_debut__month=period.month,
            )
            publications = publications.filter(
                periode_debut__year=period.year,
                periode_debut__month=period.month,
            )
            label = f"la période {period.strftime('%m/%Y')}"

        invoice_ids = list(invoices.values_list("pk", flat=True))
        publication_ids = list(publications.values_list("pk", flat=True))
        invoice_files = [
            invoice.fichier_pdf
            for invoice in invoices.exclude(fichier_pdf__isnull=True).exclude(fichier_pdf="")
        ]
        publication_files = [
            publication.fichier_pdf
            for publication in publications.exclude(fichier_pdf__isnull=True).exclude(fichier_pdf="")
        ]
        histories_count = HistoriqueFacturation.objects.filter(invoice_id__in=invoice_ids).count()
        notifications_count = NotificationFacture.objects.filter(invoice_id__in=invoice_ids).count()

        self.stdout.write(self.style.WARNING(f"Cible : {label}."))
        self.stdout.write(
            "Factures : {invoices} ({invoice_files} PDF), publications : {publications} "
            "({publication_files} PDF), historiques : {histories}, notifications : {notifications}.".format(
                invoices=len(invoice_ids),
                invoice_files=len(invoice_files),
                publications=len(publication_ids),
                publication_files=len(publication_files),
                histories=histories_count,
                notifications=notifications_count,
            )
        )

        if not options["confirm"]:
            self.stdout.write(
                self.style.WARNING(
                    "Simulation uniquement : aucune donnée n'a été modifiée. "
                    "Ajoutez --confirm pour exécuter la réinitialisation."
                )
            )
            return

        # Les fichiers sont retirés du stockage avant la mise à jour des champs.
        # Une absence physique du fichier n'empêche pas la remise à zéro de la base.
        failed_deletions = 0
        for file_field in [*invoice_files, *publication_files]:
            try:
                file_field.delete(save=False)
            except Exception:
                failed_deletions += 1

        with transaction.atomic():
            NotificationFacture.objects.filter(invoice_id__in=invoice_ids).delete()
            HistoriqueFacturation.objects.filter(invoice_id__in=invoice_ids).delete()
            Publication.objects.filter(pk__in=publication_ids).delete()
            Invoice.objects.filter(pk__in=invoice_ids).update(
                fichier_pdf=None,
                numero_facture_pdf="",
                date_emission_pdf=None,
                montant_ht=0,
                montant_tva=0,
                montant_ttc=0,
                statut=StatutFacture.EN_COURS,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Réinitialisation terminée : les factures sont de nouveau EN_COURS et prêtes à recevoir un PDF."
            )
        )
        if failed_deletions:
            self.stdout.write(
                self.style.WARNING(
                    f"{failed_deletions} fichier(s) absent(s) ou non supprimé(s) du stockage ; "
                    "la base a tout de même été réinitialisée."
                )
            )
