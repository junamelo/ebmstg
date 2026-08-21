"""Génération du PDF de synthèse d'un contrat sous forme de tableaux."""

from html import escape
from io import BytesIO
from pathlib import Path

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    Image,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BLUE = colors.HexColor('#002a7a')
ORANGE = colors.HexColor('#f58220')
LIGHT_BLUE = colors.HexColor('#eaf2ff')
LIGHT_GREY = colors.HexColor('#f7f7f7')


def _logo_moov():
    """Retourne le logo partage avec le frontend, lorsqu'il est disponible."""
    logo_path = Path(settings.BASE_DIR).parent / 'Front' / 'src' / 'assets' / 'logo-moov.png'
    if not logo_path.is_file():
        return None
    return Image(str(logo_path), width=3.55 * cm, height=1.55 * cm, kind='proportional')


def _text(value):
    return escape(str(value or '-')).replace('\n', '<br/>')


def _services_ligne(line):
    services = []
    if line.facture_detaillee:
        services.append('Facturation detaillee')
    if line.option_nolimit:
        services.append(f'No Limit {line.option_nolimit}')
    if line.option_blackberry:
        services.append(f'BlackBerry {line.option_blackberry}')
    if line.est_incognito:
        services.append('Incognito')
    if line.est_roaming:
        services.append('Roaming')
    if line.est_internet:
        services.append('Internet')
    if line.est_international:
        services.append('International')
    if line.est_non_revenu:
        services.append('Non revenu')
    return ', '.join(services) if services else 'Aucun service optionnel'


def generer_pdf_contrat(company):
    """Retourne un BytesIO contenant le contrat sous forme de tableaux."""
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.1 * cm,
        bottomMargin=1.1 * cm,
        title=f'Contrat {company.compte}',
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        'ContratTitle', parent=styles['Title'], alignment=TA_CENTER,
        textColor=BLUE, fontSize=18, leading=22, spaceAfter=4,
    )
    header_title = ParagraphStyle(
        'ContratHeaderTitle', parent=styles['Title'], alignment=TA_CENTER,
        textColor=colors.white, fontSize=17, leading=20, spaceAfter=2,
    )
    header_subtitle = ParagraphStyle(
        'ContratHeaderSubtitle', parent=styles['Normal'], alignment=TA_CENTER,
        textColor=colors.HexColor('#dbeafe'), fontSize=9.5, leading=12,
    )
    subtitle = ParagraphStyle(
        'ContratSubtitle', parent=styles['Normal'], alignment=TA_CENTER,
        textColor=colors.HexColor('#555555'), fontSize=10, spaceAfter=14,
    )
    section = ParagraphStyle(
        'ContratSection', parent=styles['Heading2'], textColor=BLUE,
        fontSize=12, leading=16, spaceBefore=8, spaceAfter=6,
    )
    cell = ParagraphStyle('ContratCell', parent=styles['Normal'], fontSize=8.5, leading=10.5)
    label = ParagraphStyle('ContratLabel', parent=cell, fontName='Helvetica-Bold', textColor=BLUE)
    header_cell = ParagraphStyle('ContratHeaderCell', parent=cell, fontName='Helvetica-Bold', textColor=colors.white)

    logo = _logo_moov()
    logo_cell = logo if logo else Paragraph('', cell)
    entete = Table(
        [[
            logo_cell,
            Paragraph('CONTRAT CLIENT', header_title),
            Paragraph(f'Code contrat<br/><b>{_text(company.compte)}</b>', header_subtitle),
        ]],
        colWidths=[4.5 * cm, 16.2 * cm, 6.3 * cm],
        hAlign='LEFT',
    )
    entete.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BLUE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (0, 0), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('LINEBELOW', (0, 0), (-1, 0), 3, ORANGE),
    ]))

    elements = [entete, Spacer(1, 0.35 * cm)]

    def info_table(rows):
        data = [[Paragraph(_text(key), label), Paragraph(_text(value), cell)] for key, value in rows]
        table = Table(data, colWidths=[4.3 * cm, 20.7 * cm], hAlign='LEFT', repeatRows=0)
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#d1d5db')),
            ('BACKGROUND', (0, 0), (0, -1), LIGHT_BLUE),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 7),
            ('RIGHTPADDING', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        return table

    elements += [
        Paragraph('Informations du contrat', section),
        info_table([
            ('Raison sociale', company.raison_sociale),
            ('Categorie', company.get_categorie_display()),
            ('Statut contrat', company.statut),
            ('Statut factures', company.statut_factures),
            ('Date effet', company.date_effet),
            ('Date fin', company.date_fin),
            ('Mode de reglement', company.get_mode_reglement_display()),
            ('Exonere de TVA', 'Oui' if company.est_exonere else 'Non'),
            ('Adresse 1', company.adresse),
            ('Adresse 2', company.adresse_ligne2),
            ('Type de revenu', company.type_revenu),
            ('Observation', company.observation),
        ]),
        Spacer(1, 0.35 * cm),
    ]

    payeur = '-'
    if company.payeur:
        payeur = f'{company.payeur.first_name} {company.payeur.last_name} - {company.payeur.email}'
    commercial = '-'
    if company.commercial:
        commercial = f'{company.commercial.prenom} {company.commercial.nom} ({company.commercial.matricule})'
    elements += [
        Paragraph('Interlocuteurs', section),
        info_table([('Payeur', payeur), ('Commercial', commercial)]),
    ]

    if company.est_resilie:
        elements += [
            Paragraph('Resiliation', section),
            info_table([
                ('Statut', 'RESILIE'),
                ('Date de resiliation', company.date_resiliation),
                ('Motif', company.motif_resiliation),
                ('Observation', company.observation_resiliation),
            ]),
        ]

    elements += [Spacer(1, 0.35 * cm), Paragraph(f'Lignes telephoniques ({company.lines.count()})', section)]
    rows = [[
        Paragraph('N°', header_cell),
        Paragraph('Numero', header_cell),
        Paragraph('Employe', header_cell),
        Paragraph('Statut', header_cell),
        Paragraph('Cycle', header_cell),
        Paragraph('Services appliques', header_cell),
    ]]
    for index, line in enumerate(company.lines.select_related('employe').order_by('msisdn'), start=1):
        employe = '-'
        if line.employe:
            employe = f'{line.employe.first_name} {line.employe.last_name}'.strip() or line.employe.username
        rows.append([
            Paragraph(str(index), cell),
            Paragraph(_text(line.msisdn), cell),
            Paragraph(_text(employe), cell),
            Paragraph(_text(line.statut), cell),
            Paragraph(_text(line.cycle), cell),
            Paragraph(_text(_services_ligne(line)), cell),
        ])

    lines_table = Table(
        rows,
        colWidths=[0.7 * cm, 2.5 * cm, 4.2 * cm, 2.3 * cm, 1.8 * cm, 14 * cm],
        repeatRows=1,
        hAlign='LEFT',
    )
    lines_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(lines_table)
    elements += [
        Spacer(1, 0.3 * cm),
        Paragraph('Document genere par le Portail Moov Africa.', subtitle),
    ]
    document.build(elements)
    buffer.seek(0)
    return buffer
