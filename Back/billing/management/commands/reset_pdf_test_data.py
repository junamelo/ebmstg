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
    TraitementPDF,
)


class Command(BaseCommand):
    help = (
        "Réinitialise les données transactionnelles de facturation pour rejouer "
        "des imports PDF SOM et GLO. Les comptes, contrats, entreprises, lignes, "
        "forfaits et services ne sont jamais supprimés."
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
        parser.add_argument(
            "--delete-invoices",
            action="store_true",
            help=(
                "Supprime réellement les factures ciblées au lieu de les remettre "
                "à EN_COURS. Utiliser ce mode pour repartir d'une base de factures vide."
            ),
        )
        parser.add_argument(
            "--clear-imports",
            action="store_true",
            help=(
                "Supprime aussi l'historique des imports TraitementPDF et leurs "
                "fichiers sources. Les blocs PDF générés dans « Mode démonstration » "
                "sont conservés."
            ),
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
        traitements = TraitementPDF.objects.all()
        if options["period"]:
            traitements = traitements.filter(
                periode_debut__year=period.year,
                periode_debut__month=period.month,
            )
        traitement_ids = list(traitements.values_list("pk", flat=True))

        traitements_en_cours = traitements.filter(
            statut__in=[TraitementPDF.Statut.EN_ATTENTE, TraitementPDF.Statut.EN_COURS]
        ).count()
        if options["confirm"] and traitements_en_cours:
            raise CommandError(
                "Réinitialisation annulée : un traitement PDF est encore EN_ATTENTE ou EN_COURS. "
                "Attendez sa fin ou arrêtez Celery avant de relancer la commande."
            )
        invoice_files = [
            invoice.fichier_pdf
            for invoice in invoices.exclude(fichier_pdf__isnull=True).exclude(fichier_pdf="")
        ]
        publication_files = [
            publication.fichier_pdf
            for publication in publications.exclude(fichier_pdf__isnull=True).exclude(fichier_pdf="")
        ]
        import_files = [
            traitement.fichier_source
            for traitement in traitements.exclude(fichier_source__isnull=True).exclude(fichier_source="")
        ]
        histories_count = HistoriqueFacturation.objects.filter(invoice_id__in=invoice_ids).count()
        notifications_count = NotificationFacture.objects.filter(invoice_id__in=invoice_ids).count()

        self.stdout.write(self.style.WARNING(f"Cible : {label}."))
        self.stdout.write(
            "Factures : {invoices} ({invoice_files} PDF), publications : {publications} "
            "({publication_files} PDF), historiques : {histories}, notifications : {notifications}, "
            "imports PDF : {imports} ({import_files} fichiers source).".format(
                invoices=len(invoice_ids),
                invoice_files=len(invoice_files),
                publications=len(publication_ids),
                publication_files=len(publication_files),
                histories=histories_count,
                notifications=notifications_count,
                imports=len(traitement_ids),
                import_files=len(import_files),
            )
        )
        mode = "suppression complète des factures" if options["delete_invoices"] else "remise des factures à EN_COURS"
        self.stdout.write(f"Mode sélectionné : {mode}.")
        if options["clear_imports"]:
            self.stdout.write("Les imports PDF et leurs fichiers sources seront aussi supprimés.")

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
        files_to_delete = [*invoice_files, *publication_files]
        if options["clear_imports"]:
            files_to_delete.extend(import_files)

        for file_field in files_to_delete:
            try:
                file_field.delete(save=False)
            except Exception:
                failed_deletions += 1

        with transaction.atomic():
            NotificationFacture.objects.filter(invoice_id__in=invoice_ids).delete()
            HistoriqueFacturation.objects.filter(invoice_id__in=invoice_ids).delete()
            Publication.objects.filter(pk__in=publication_ids).delete()
            if options["delete_invoices"]:
                Invoice.objects.filter(pk__in=invoice_ids).delete()
            else:
                Invoice.objects.filter(pk__in=invoice_ids).update(
                    fichier_pdf=None,
                    numero_facture_pdf="",
                    date_emission_pdf=None,
                    montant_ht=0,
                    montant_tva=0,
                    montant_ttc=0,
                    statut=StatutFacture.EN_COURS,
                )
            if options["clear_imports"]:
                TraitementPDF.objects.filter(pk__in=traitement_ids).delete()

        self.stdout.write(
            self.style.SUCCESS(
                "Réinitialisation terminée : "
                + (
                    "les factures ont été supprimées et peuvent être recréées par le prochain import PDF."
                    if options["delete_invoices"]
                    else "les factures sont de nouveau EN_COURS et prêtes à recevoir un PDF."
                )
            )
        )
        if failed_deletions:
            self.stdout.write(
                self.style.WARNING(
                    f"{failed_deletions} fichier(s) absent(s) ou non supprimé(s) du stockage ; "
                    "la base a tout de même été réinitialisée."
                )
            )
