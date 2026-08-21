"""Tests du rapprochement PDF lorsque les factures provisoires sont absentes."""

import os
import tempfile
from decimal import Decimal

from django.test import TestCase, override_settings
from PyPDF2 import PdfWriter

from billing.models import Company, Invoice, Line
from billing.services.pdf_processor import PDFMatcher, PDFProcessor


class PDFIdentifierAndAutoCreationTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            compte='A0000009',
            raison_sociale='Café Informatique et Télécom',
        )
        self.line = Line.objects.create(
            company=self.company,
            msisdn='99475555',
            utilisateur='Marie Noagbodzi',
            cycle='OP',
            forfait=Decimal('7000'),
        )

    def test_identifiants_facture_moov_collee_au_nom(self):
        texte = '''
            UTILISATEUR: FACTURE N°:
            NOAGBODJI MARIEA20260601041
            A0000009
            99475555
            01/06/2026-30/06/2026
            09/07/2026
            30/07/2026
            TOTAL : 9 998 1 800 11 798
        '''

        identifiers = PDFProcessor.find_identifiers(texte)

        self.assertEqual(identifiers['numero_facture'], 'A20260601041')
        self.assertEqual(identifiers['compte'], 'A0000009')
        self.assertEqual(identifiers['msisdn'], '99475555')
        self.assertEqual(identifiers['periode_debut'], '01/06/2026')
        self.assertEqual(identifiers['periode_fin'], '30/06/2026')
        self.assertEqual(identifiers['montant_ttc'], '11798')

    def test_cree_et_attache_une_facture_absente_si_la_ligne_existe(self):
        identifiers = {
            'numero_facture': 'A20260601041',
            'compte': 'A0000009',
            'msisdn': '99475555',
            'periode_debut': '01/06/2026',
            'periode_fin': '30/06/2026',
            'date_emission_pdf': '09/07/2026',
            'date_echeance': '30/07/2026',
            'montant_ht': '9998',
            'montant_tva': '1800',
            'montant_ttc': '11798',
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            source_pdf = os.path.join(temporary_directory, 'facture.pdf')
            writer = PdfWriter()
            writer.add_blank_page(width=100, height=100)
            with open(source_pdf, 'wb') as file_handle:
                writer.write(file_handle)

            with override_settings(MEDIA_ROOT=temporary_directory):
                result = PDFMatcher.auto_attach_pdfs(
                    [{'filename': 'A20260601041.pdf', 'path': source_pdf, 'identifiers': identifiers}],
                    Invoice.objects.none(),
                    invoice_type='SOM',
                    creer_factures_absentes=True,
                )

        self.assertEqual(result['matched'], 1)
        self.assertEqual(result['not_matched'], 0)
        self.assertEqual(len(result['created']), 1)
        facture = Invoice.objects.get(numero_facture='A20260601041-99475555')
        self.assertEqual(facture.company, self.company)
        self.assertEqual(facture.line, self.line)
        self.assertEqual(facture.numero_facture_pdf, 'A20260601041')
        self.assertEqual(facture.statut, 'VALIDEE')
        self.assertEqual(facture.montant_ttc, Decimal('11798'))

    def test_ne_cree_rien_si_la_ligne_est_inconnue(self):
        result = PDFMatcher.auto_attach_pdfs(
            [{
                'filename': 'inconnue.pdf',
                'path': __file__,
                'identifiers': {
                    'numero_facture': 'A20260609999',
                    'compte': 'A0000009',
                    'msisdn': '99999999',
                    'periode_debut': '01/06/2026',
                    'periode_fin': '30/06/2026',
                    'date_echeance': '30/07/2026',
                },
            }],
            Invoice.objects.none(),
            invoice_type='SOM',
            creer_factures_absentes=True,
        )

        self.assertEqual(result['matched'], 0)
        self.assertEqual(result['not_matched'], 1)
        self.assertEqual(Invoice.objects.count(), 0)
        self.assertIn('Aucune ligne active', result['errors'][0]['error'])
