from datetime import datetime

from django.core.management.base import BaseCommand
from PyPDF2 import PdfReader

from billing.models import Invoice
from billing.services.pdf_processor import PDFProcessor


class Command(BaseCommand):
    help = 'Synchronise numéro et date d’édition affichés avec les PDF déjà associés.'

    def handle(self, *args, **options):
        updated = 0
        skipped = 0
        for invoice in Invoice.objects.exclude(fichier_pdf='').exclude(fichier_pdf__isnull=True):
            try:
                reader = PdfReader(invoice.fichier_pdf.path)
                text = PDFProcessor.extract_text_from_page(reader.pages[0])
                identifiers = PDFProcessor.find_identifiers(text)
                changed = []
                if identifiers.get('numero_facture') and invoice.numero_facture_pdf != identifiers['numero_facture']:
                    invoice.numero_facture_pdf = identifiers['numero_facture']
                    changed.append('numéro')
                if identifiers.get('date_emission_pdf'):
                    date_pdf = datetime.strptime(identifiers['date_emission_pdf'], '%d/%m/%Y').date()
                    if invoice.date_emission_pdf != date_pdf:
                        invoice.date_emission_pdf = date_pdf
                        changed.append('date')
                if changed:
                    invoice.save(update_fields=['numero_facture_pdf', 'date_emission_pdf', 'date_modification'])
                    updated += 1
                else:
                    skipped += 1
            except Exception as exc:
                self.stderr.write(f'{invoice.numero_facture}: {exc}')

        self.stdout.write(self.style.SUCCESS(f'{updated} facture(s) synchronisée(s), {skipped} inchangée(s).'))
