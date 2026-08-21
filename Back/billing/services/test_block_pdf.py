"""Génération de blocs PDF de test compatibles avec le découpage Moov e-Factures."""

from io import BytesIO


class TestBlockPDFUnavailable(RuntimeError):
    """Levée lorsque ReportLab n'est pas disponible sur le serveur."""


def _format_fcfa(amount):
    return f"{amount:,.0f}".replace(",", " ") + " FCFA"


def _format_date(value):
    return value.strftime("%d/%m/%Y")


def generate_test_invoice_block(invoices, invoice_type, libelle):
    """Retourne un PDF multi-pages : une facture test par page.

    Les libellés ``N° Facture``, ``Compte client`` et ``MSISDN`` sont écrits
    en texte dans le PDF. Ils correspondent aux identifiants lus par
    ``PDFProcessor`` lors du découpage automatique.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.pdfgen import canvas
    except ImportError as exc:  # pragma: no cover - dépendance contrôlée au déploiement
        raise TestBlockPDFUnavailable(
            "ReportLab est requis pour générer les blocs PDF de test."
        ) from exc

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    is_summary = invoice_type == "SOM"

    for index, invoice in enumerate(invoices, start=1):
        company = invoice.company
        line = invoice.line

        # En-tête volontairement simple et lisible par l'extracteur PDF.
        pdf.setFillColor(colors.HexColor("#002A7A"))
        pdf.rect(0, height - 3.2 * cm, width, 3.2 * cm, fill=1, stroke=0)
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(2 * cm, height - 1.45 * cm, "MOOV AFRICA - FACTURE POSTPAYEE")
        pdf.setFont("Helvetica", 9)
        pdf.drawString(2 * cm, height - 2.15 * cm, "BLOC DE TEST - NON VALABLE POUR LA FACTURATION REELLE")

        pdf.setFillColor(colors.HexColor("#C2410C"))
        pdf.roundRect(width - 7.1 * cm, height - 2.55 * cm, 5.2 * cm, 0.8 * cm, 4, fill=1, stroke=0)
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawCentredString(width - 4.5 * cm, height - 2.25 * cm, "FACTURE DE TEST")

        pdf.setFillColor(colors.HexColor("#111827"))
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(2 * cm, height - 4.45 * cm, "Facture sommaire" if is_summary else "Facture globale")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(2 * cm, height - 5.1 * cm, f"N° Facture : {invoice.numero_facture}")
        pdf.drawString(2 * cm, height - 5.7 * cm, f"Compte client : {company.compte}")
        pdf.drawString(2 * cm, height - 6.3 * cm, f"Raison sociale : {company.raison_sociale}")
        if is_summary and line:
            pdf.drawString(2 * cm, height - 6.9 * cm, f"MSISDN : {line.msisdn}")
            titulaire = line.utilisateur or "Employé non renseigné"
            pdf.drawString(2 * cm, height - 7.5 * cm, f"Utilisateur : {titulaire}")

        info_top = height - (9.1 * cm if is_summary else 8.3 * cm)
        pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
        pdf.setFillColor(colors.HexColor("#F8FAFC"))
        pdf.roundRect(2 * cm, info_top - 2.4 * cm, width - 4 * cm, 2.4 * cm, 6, fill=1, stroke=1)
        pdf.setFillColor(colors.HexColor("#111827"))
        pdf.setFont("Helvetica", 10)
        pdf.drawString(2.5 * cm, info_top - 0.55 * cm, f"Période début : {_format_date(invoice.periode_debut)}")
        pdf.drawString(10.2 * cm, info_top - 0.55 * cm, f"Période fin : {_format_date(invoice.periode_fin)}")
        # La troisième date est volontairement la date d'émission ; elle est
        # également reconnue par PDFProcessor.
        pdf.drawString(2.5 * cm, info_top - 1.25 * cm, f"Date émission : {_format_date(invoice.date_emission_pdf)}")
        pdf.drawString(10.2 * cm, info_top - 1.25 * cm, f"Date échéance : {_format_date(invoice.date_echeance)}")
        pdf.drawString(2.5 * cm, info_top - 1.95 * cm, f"Objet : {libelle}")

        table_top = info_top - 3.4 * cm
        x = 2 * cm
        widths = [8.7 * cm, 3.0 * cm, 3.7 * cm]
        pdf.setFillColor(colors.HexColor("#002A7A"))
        pdf.rect(x, table_top, sum(widths), 0.7 * cm, fill=1, stroke=0)
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(x + 0.2 * cm, table_top + 0.25 * cm, "Désignation")
        pdf.drawString(x + widths[0] + 0.2 * cm, table_top + 0.25 * cm, "Montant HT")
        pdf.drawString(x + widths[0] + widths[1] + 0.2 * cm, table_top + 0.25 * cm, "Montant TTC")
        pdf.setFillColor(colors.white)
        pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
        pdf.rect(x, table_top - 1.15 * cm, sum(widths), 1.15 * cm, fill=1, stroke=1)
        pdf.line(x + widths[0], table_top - 1.15 * cm, x + widths[0], table_top)
        pdf.line(x + widths[0] + widths[1], table_top - 1.15 * cm, x + widths[0] + widths[1], table_top)
        pdf.setFillColor(colors.HexColor("#111827"))
        pdf.setFont("Helvetica", 9)
        pdf.drawString(x + 0.2 * cm, table_top - 0.55 * cm, libelle)
        pdf.drawRightString(x + widths[0] + widths[1] - 0.2 * cm, table_top - 0.55 * cm, _format_fcfa(invoice.montant_ht))
        pdf.drawRightString(x + sum(widths) - 0.2 * cm, table_top - 0.55 * cm, _format_fcfa(invoice.montant_ttc))

        total_top = table_top - 2.3 * cm
        pdf.setFillColor(colors.HexColor("#FFF7ED"))
        pdf.roundRect(width - 8.1 * cm, total_top, 6.1 * cm, 1.65 * cm, 6, fill=1, stroke=0)
        pdf.setFillColor(colors.HexColor("#9A3412"))
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(width - 7.6 * cm, total_top + 1.05 * cm, "TOTAL TTC")
        pdf.setFont("Helvetica-Bold", 15)
        pdf.drawRightString(width - 2.45 * cm, total_top + 0.45 * cm, _format_fcfa(invoice.montant_ttc))

        pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
        pdf.line(2 * cm, 2.5 * cm, width - 2 * cm, 2.5 * cm)
        pdf.setFillColor(colors.HexColor("#475569"))
        pdf.setFont("Helvetica", 8)
        pdf.drawString(2 * cm, 2.05 * cm, "Document généré par Moov e-Factures pour les tests et démonstrations.")
        pdf.drawRightString(width - 2 * cm, 2.05 * cm, f"Page {index} / {len(invoices)}")
        pdf.showPage()

    pdf.save()
    buffer.seek(0)
    return buffer
