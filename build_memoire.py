from pathlib import Path
from docx import Document
from docx.shared import Cm, Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
OUTPUT = DOCS / "Memoire_BANLEPO_Benoit_Moov_eFactures_version_canevas_inspiree_JeanLuc_Taoufik_logiciels_corriges.docx"
CLASS_DIAGRAM = ROOT / "Contexte" / "Diagramme de classe.png"
ILLUSTRATION_DASHBOARD = ROOT / "Front" / "src" / "assets" / "illustration-dashboard.png"
ILLUSTRATION_PAYEUR = ROOT / "Front" / "src" / "assets" / "illustration-payeur.png"
ILLUSTRATION_SIMULATION = ROOT / "Front" / "src" / "assets" / "illustration-simulation.png"

BLUE = RGBColor(0x00, 0x2A, 0x7A)
DARK_BLUE = RGBColor(0x00, 0x1F, 0x5B)
GRAY = RGBColor(0x55, 0x55, 0x55)
BLACK = RGBColor(0x00, 0x00, 0x00)
LIGHT_BLUE = "E8EEF8"
LIGHT_GRAY = "F2F4F7"


def set_run_font(run, name="Arial", size=12, bold=None, italic=None, color=BLACK):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    run.font.color.rgb = color
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=100, start=120, bottom=100, end=120):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, v in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def set_table_geometry(table, widths):
    """Apply fixed DXA geometry so tables remain stable in Word/LibreOffice."""
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(widths)))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), "0")
    tbl_ind.set(qn("w:type"), "dxa")
    grid = tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            cell.width = Inches(widths[idx] / 1440)
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(widths[idx]))
            tc_w.set(qn("w:type"), "dxa")
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_table_borders(table, color="B8C2D1", size="6"):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = qn(f"w:{edge}")
        element = borders.find(tag)
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def add_page_field(paragraph):
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_begin, instr, fld_sep, text, fld_end])
    set_run_font(run, size=10, color=GRAY)


def set_page_number_format(section, fmt="decimal", start=None):
    sect_pr = section._sectPr
    pg_num = sect_pr.find(qn("w:pgNumType"))
    if pg_num is None:
        pg_num = OxmlElement("w:pgNumType")
        sect_pr.append(pg_num)
    pg_num.set(qn("w:fmt"), fmt)
    if start is not None:
        pg_num.set(qn("w:start"), str(start))


def configure_section(section, header_text, fmt="decimal", start=None):
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.header_distance = Cm(1.25)
    section.footer_distance = Cm(1.25)
    set_page_number_format(section, fmt, start)
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.paragraph_format.space_after = Pt(0)
    hp.clear()
    hr = hp.add_run(header_text)
    set_run_font(hr, size=10, color=GRAY)
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.space_before = Pt(0)
    fp.paragraph_format.space_after = Pt(0)
    fp.clear()
    add_page_field(fp)


def configure_styles(doc):
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    normal.font.size = Pt(12)
    normal.font.color.rgb = BLACK
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(8)
    normal.paragraph_format.widow_control = True
    for name, size, color, before, after in [
        ("Heading 1", 16, BLUE, 18, 10),
        ("Heading 2", 14, BLUE, 14, 8),
        ("Heading 3", 12, DARK_BLUE, 10, 5),
    ]:
        style = styles[name]
        style.font.name = "Arial"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = color
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.line_spacing = 1.15
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.widow_control = True
    for name in ("List Bullet", "List Number"):
        style = styles[name]
        style.font.name = "Arial"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
        style.font.size = Pt(12)
        style.paragraph_format.line_spacing = 1.5
        style.paragraph_format.space_after = Pt(4)


def add_body(doc, text, bold_prefix=None, italic=False):
    p = doc.add_paragraph(style="Normal")
    if bold_prefix and text.startswith(bold_prefix):
        r = p.add_run(bold_prefix)
        set_run_font(r, bold=True)
        r2 = p.add_run(text[len(bold_prefix):])
        set_run_font(r2, italic=italic)
    else:
        r = p.add_run(text)
        set_run_font(r, italic=italic)
    return p


def add_code_block(doc, text):
    """Insert a short implementation excerpt with a restrained technical style."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.45)
    p.paragraph_format.right_indent = Cm(0.45)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.0
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F3F5F7")
    pPr.append(shd)
    r = p.add_run(text)
    set_run_font(r, name="Courier New", size=9.5, color=BLACK)
    return p


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Cm(0.95 + 0.45 * level)
    p.paragraph_format.first_line_indent = Cm(-0.45)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(text)
    set_run_font(r)
    return p


def add_number(doc, text):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.left_indent = Cm(0.95)
    p.paragraph_format.first_line_indent = Cm(-0.45)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(text)
    set_run_font(r)
    return p


def add_caption(doc, text, above=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text)
    set_run_font(r, size=11, italic=True, color=GRAY)
    return p


def add_table(doc, headers, rows, widths, caption=None):
    if caption:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(caption)
        set_run_font(r, size=11, bold=True, color=DARK_BLUE)
    table = doc.add_table(rows=1, cols=len(headers))
    set_table_geometry(table, widths)
    set_table_borders(table)
    hdr = table.rows[0]
    set_repeat_table_header(hdr)
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        set_cell_shading(cell, LIGHT_BLUE)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(str(h))
        set_run_font(r, size=10.5, bold=True, color=DARK_BLUE)
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            p = cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.1
            r = p.add_run(str(value))
            set_run_font(r, size=10.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def add_toc_field(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = ' TOC \\o "1-3" \\h \\z \\u '
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t")
    t.text = "Actualiser la table des matières dans Word (clic droit > Mettre à jour les champs)."
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, sep, t, end])
    set_run_font(run, size=12, color=GRAY)


def add_front_title(doc, text, size=14, color=BLUE, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run(text)
    set_run_font(r, size=size, bold=bold, color=color)
    return p


def add_page_break(doc):
    doc.add_page_break()


def add_part_heading(doc, text):
    doc.add_page_break()
    p = doc.add_paragraph(style="Heading 1")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(20)
    r = p.add_run(text)
    set_run_font(r, size=18, bold=True, color=BLUE)
    return p


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    r = p.add_run(text)
    set_run_font(r, size={1: 16, 2: 14, 3: 12}[level], bold=True, color={1: BLUE, 2: BLUE, 3: DARK_BLUE}[level])
    return p


def build():
    doc = Document()
    configure_styles(doc)
    section = doc.sections[0]
    configure_section(section, "Mémoire de fin de formation - Moov e-Factures", fmt="lowerRoman", start=1)
    # Prevent Word from displaying a blank initial header paragraph.
    section.different_first_page_header_footer = True

    # Page de garde
    cover = doc.add_paragraph()
    cover.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover.paragraph_format.space_before = Pt(12)
    for line, size, bold, color in [
        ("REPUBLIQUE TOGOLAISE", 14, True, BLACK),
        ("Travail - Liberté - Patrie", 12, False, BLACK),
        ("INSTITUT AFRICAIN D'INFORMATIQUE", 14, True, BLUE),
        ("Représentation du Togo (IAI-TOGO)", 12, False, BLACK),
        ("Cycle des Ingénieurs de Travaux Informatiques", 12, True, DARK_BLUE),
        ("Option : Génie Logiciel et Systèmes d'Information", 12, True, DARK_BLUE),
    ]:
        r = cover.add_run(line + "\n")
        set_run_font(r, size=size, bold=bold, color=color)
    doc.add_paragraph().paragraph_format.space_after = Pt(18)
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_before = Pt(24)
    title.paragraph_format.space_after = Pt(12)
    r = title.add_run("MÉMOIRE DE FIN DE FORMATION")
    set_run_font(r, size=18, bold=True, color=BLUE)
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_after = Pt(18)
    r = subtitle.add_run("Développement d'un portail web de publication de factures clients postpayés : cas de Moov Africa Togo")
    set_run_font(r, size=16, bold=True, color=DARK_BLUE)
    add_body(doc, "Projet réalisé au sein du service Production SI / département technique de Moov Africa Togo.")
    meta = [
        ["Rédigé et soutenu par", "BANLEPO Mintre Benoît"],
        ["Maître de stage", "M. SADZO-HETSU Kossivi, Chef Service Production SI"],
        ["Superviseur académique", "M. AZOTI Hodabalo, Enseignant à l'IAI-TOGO"],
        ["Période indicative", "11 mai - 8 août 2026"],
        ["Année académique", "2025-2026"],
    ]
    add_table(doc, ["Élément", "Information"], meta, [2800, 6560])
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    r = p.add_run("Lomé, 2026")
    set_run_font(r, size=12, bold=True, color=BLUE)

    # Front matter
    add_page_break(doc)
    add_front_title(doc, "DÉDICACE", 16)
    add_body(doc, "À mes chers parents, les mots me manquent pour témoigner ma reconnaissance et ma gratitude pour les sacrifices consentis à mon égard. Je vous dis simplement merci pour tout.")
    add_body(doc, "À toutes les personnes qui, de près ou de loin, ont contribué à la réalisation de ce projet, je dédie ce travail avec reconnaissance.")

    add_page_break(doc)
    add_front_title(doc, "REMERCIEMENTS", 16)
    add_body(doc, "Nous rendons grâce au Seigneur pour sa miséricorde et sa guidance constante tout au long de notre parcours.")
    add_body(doc, "Nos vifs remerciements s'adressent à l'Institut Africain d'Informatique (IAI-TOGO) et à l'ensemble de son corps professoral pour la qualité de l'enseignement, la rigueur de la formation et l'accompagnement apporté aux étudiants.")
    add_body(doc, "Nous exprimons notre profonde gratitude à Moov Africa Togo, en particulier au service Production SI et au département technique, pour nous avoir ouvert ses portes et offert un cadre propice à la mise en pratique de nos connaissances.")
    add_body(doc, "Nous remercions spécialement M. SADZO-HETSU Kossivi, notre maître de stage, pour ses orientations, sa disponibilité et son suivi professionnel, ainsi que M. AZOTI Hodabalo, notre superviseur académique, pour ses conseils et ses remarques constructives.")
    add_body(doc, "Enfin, nous adressons nos remerciements à notre famille, à nos camarades et à toutes les personnes qui nous ont soutenu durant cette période.")

    add_page_break(doc)
    add_front_title(doc, "SOMMAIRE", 16)
    add_toc_field(doc)

    add_page_break(doc)
    add_front_title(doc, "RÉSUMÉ", 16)
    add_body(doc, "Dans le cadre de l'obtention du diplôme d'Ingénieur des Travaux Informatiques de l'IAI-TOGO, nous avons réalisé un stage au sein de Moov Africa Togo. Le projet porte sur le développement d'un portail web de publication de factures clients postpayés. L'objectif est de permettre aux clients entreprises de consulter leurs factures globales et sommaires, leurs services souscrits et l'historique de leurs opérations, tout en donnant aux équipes de facturation un outil fiable pour importer, découper et publier des blocs PDF.")
    add_body(doc, "La solution distingue les profils super administrateur, chef de facturation, agent de facturation, commercial, payeur et employé. Elle propose aussi une simulation de facturation basée sur les forfaits et les tarifs paramétrables. La conception s'appuie sur UML et le processus 2TUP. La mise en œuvre associe Django REST Framework pour le backend, React avec Vite pour le frontend, PostgreSQL pour la persistance, et Celery avec un broker compatible Redis (Garnet dans l'environnement de développement) pour les traitements PDF longs.")
    add_body(doc, "Mots-clés : facturation postpayée, portail web, PDF, Django, React, PostgreSQL, UML, simulation, contrôle d'accès.")

    add_page_break(doc)
    add_front_title(doc, "ABSTRACT", 16)
    add_body(doc, "As part of the requirements for the Engineer of Computer Works degree at IAI-TOGO, we completed an internship at Moov Africa Togo. The project consists in developing a web portal for publishing postpaid customer invoices. The platform allows business customers to consult global and summary invoices, subscribed services and history, while providing billing teams with a reliable tool to import, split and publish PDF batches.")
    add_body(doc, "The solution differentiates super administrator, billing manager, billing agent, sales representative, payer and employee roles. It also provides a configurable billing simulation. The design relies on UML and the 2TUP process. The implementation combines Django REST Framework, React/Vite, PostgreSQL and Celery using a Redis-compatible broker (Garnet in the development environment).")

    add_page_break(doc)
    add_front_title(doc, "GLOSSAIRE ET ACRONYMES", 16)
    glossary = [
        ("API", "Application Programming Interface, interface permettant à des logiciels de communiquer."),
        ("Celery", "Système de tâches distribuées utilisé ici pour exécuter les traitements PDF en arrière-plan."),
        ("Garnet", "Serveur compatible avec le protocole Redis utilisé comme cache et comme broker de messages."),
        ("JWT", "JSON Web Token, jeton signé utilisé pour l'authentification des appels API."),
        ("MSISDN", "Numéro international associé à une ligne mobile ; dans le projet, il identifie la ligne de l'employé."),
        ("PDF global", "Document regroupant la facturation d'un contrat ou d'une entreprise."),
        ("PDF sommaire", "Document détaillant la consommation d'une ligne individuelle."),
        ("RBAC", "Role-Based Access Control, contrôle des accès par rôles."),
        ("SPA", "Single Page Application, application web dont la navigation est gérée côté client."),
        ("TOTP / OTP", "Mot de passe à usage unique basé sur le temps, utilisé pour le 2FA optionnel."),
        ("UML", "Unified Modeling Language, langage standard de modélisation des systèmes."),
        ("2TUP", "Two Tracks Unified Process, processus de développement séparant les branches fonctionnelle et technique."),
    ]
    add_table(doc, ["Terme", "Définition"], glossary, [2200, 7160])

    add_page_break(doc)
    add_front_title(doc, "LISTE DES FIGURES", 16)
    for line in [
        "Figure 1 : Diagramme de classes du portail Moov e-Factures (partie 2).",
        "Figure 2 : Illustration de l'espace de tableau de bord (partie 5).",
        "Figure 3 : Illustration de l'espace payeur et des factures (partie 5).",
        "Figure 4 : Illustration de l'espace de simulation (partie 5).",
    ]:
        add_body(doc, line)
    add_page_break(doc)
    add_front_title(doc, "LISTE DES TABLEAUX", 16)
    for line in [
        "Tableau 1 : Liste des participants au projet.",
        "Tableau 2 : Comparaison des solutions envisagées.",
        "Tableau 3 : Évaluation financière du développement sur mesure.",
        "Tableau 4 : Planning prévisionnel de réalisation.",
        "Tableau 5 : Acteurs et responsabilités.",
        "Tableau 6 : Exigences fonctionnelles principales.",
        "Tableau 7 : Description des états métier.",
        "Tableau 8 : Matériels et logiciels utilisés.",
        "Tableau 9 : Matrice de maintenance et résolution d'incidents.",
        "Tableau 10 : Scénarios de vérification fonctionnelle.",
        "Tableau 11 : Principaux risques et mesures de maîtrise.",
        "Tableau 12 : Dictionnaire synthétique des données métier.",
        "Tableau 13 : Principaux endpoints de l'API.",
        "Tableau 14 : Règles de tarification utilisées par la simulation.",
        "Tableau 15 : Contrôles d'exploitation recommandés.",
        "Tableau 16 : Exemple de lecture d'un rapport de publication.",
        "Tableau 17 : Profils de démonstration à remplacer par des comptes temporaires.",
        "Tableau 18 : Étapes du processus métier de facturation.",
        "Tableau 19 : Matrice synthétique des droits.",
        "Tableau 20 : Contrats d'échange API représentatifs.",
        "Tableau 21 : Messages et états visibles dans l'interface.",
        "Tableau 22 : Cahier de tests détaillé.",
        "Tableau 23 : Structure logique du rapport de traitement.",
        "Tableau 24 : Organisation logique du backend.",
        "Tableau 25 : Catalogue détaillé des classes métier.",
        "Tableau 26 : Estimation de la maintenance et des évolutions.",
        "Tableau 27 : Inventaire des cas d'utilisation par module.",
        "Tableau 28 : Fiches d'identification des cas d'utilisation critiques.",
        "Tableau 29 : Correspondance entre vues UML et livrables.",
        "Tableau 30 : Vérifications de déploiement et de mise en service.",
        "Tableau 31 : Modules et parcours du guide utilisateur.",
    ]:
        add_body(doc, line)
    add_page_break(doc)
    add_front_title(doc, "LISTE DES PARTICIPANTS AU PROJET", 16)
    add_table(doc, ["Nom", "Fonction", "Rôle"], [
        ["BANLEPO Mintre Benoît", "Étudiant en troisième année GLSI à l'IAI-TOGO", "Conception et réalisation"],
        ["M. SADZO-HETSU Kossivi", "Chef Service Production SI à Moov Africa Togo", "Maître de stage"],
        ["M. AZOTI Hodabalo", "Enseignant à l'IAI-TOGO", "Superviseur académique"],
    ], [2700, 3700, 2960], caption="Tableau 1 : Liste des participants au projet")

    # Main body starts with Arabic numbering.
    body = doc.add_section(WD_SECTION.NEW_PAGE)
    body.header.is_linked_to_previous = False
    body.footer.is_linked_to_previous = False
    configure_section(body, "Développement d'un portail web de publication de factures clients postpayés", fmt="decimal", start=1)

    add_heading(doc, "INTRODUCTION", 1)
    add_body(doc, "La transformation numérique modifie les attentes des clients des opérateurs de télécommunications. Les abonnés professionnels souhaitent pouvoir consulter leurs données de facturation sans attendre l'envoi mensuel d'un fichier par courrier électronique et sans solliciter systématiquement le service client. Pour une entreprise disposant de plusieurs lignes, la question est encore plus sensible : le payeur doit disposer d'une vue globale tandis que chaque employé ne doit accéder qu'à sa propre facture sommaire.")
    add_body(doc, "Moov Africa Togo dispose d'une clientèle postpayée importante, notamment composée d'entreprises organisées en flottes. Le traitement des factures implique la réception de gros fichiers PDF, leur découpage en documents individuels, leur rattachement au bon contrat ou à la bonne ligne, puis leur publication. Ces étapes nécessitent un contrôle d'accès précis, une traçabilité des opérations et une interface simple pour les clients comme pour les agents de facturation.")
    add_body(doc, "Le présent mémoire décrit la démarche suivie pour concevoir et développer le portail Moov e-Factures. La première partie présente le cahier des charges et le choix de la solution. La deuxième partie expose l'analyse et la conception UML. La troisième partie détaille la réalisation et la mise en œuvre. La quatrième partie constitue le guide d'exploitation, tandis que la cinquième présente le guide d'utilisation. Une conclusion rappelle les résultats obtenus, les limites et les perspectives.")

    # PART 1
    add_part_heading(doc, "PARTIE 1 : CAHIER DES CHARGES")
    add_heading(doc, "1.1. PRÉSENTATIONS", 2)
    add_heading(doc, "1.1.1. Brève présentation de l'IAI-TOGO", 3)
    add_body(doc, "L'Institut Africain d'Informatique (IAI) est une école inter-États d'enseignement supérieur spécialisée dans les métiers de l'informatique. La représentation du Togo a ouvert ses portes en 2002 et forme notamment des ingénieurs des travaux informatiques dans les filières Génie Logiciel et Systèmes d'Information, Administration des Systèmes et Réseaux et Multimédia Technologies Web et Infographie. Elle est située à Lomé, derrière l'immeuble SUNU Assurances, dans les locaux du Centre National d'Étude et de Traitements Informatiques (CEII).")
    add_heading(doc, "1.1.2. Présentation du cadre de stage", 3)
    add_body(doc, "Moov Africa Togo est une société anonyme de droit togolais, filiale du groupe Maroc Telecom. Opérationnelle depuis 2007, elle fournit des services de téléphonie mobile, d'accès Internet, de paiement mobile Flooz, de services à valeur ajoutée et de solutions destinées aux entreprises. Depuis 2021, l'entreprise s'inscrit dans la marque commune Moov Africa qui regroupe les filiales africaines du groupe.")
    add_body(doc, "La mission de Moov Africa Togo est de connecter les particuliers, les professionnels et les entreprises au moyen de solutions de télécommunications adaptées. Ses activités couvrent les offres voix et data, la connectivité fixe et mobile, les services de paiement et les solutions professionnelles. Parmi ses réalisations figurent le déploiement de la 3G, le lancement de la marque Moov Africa et le développement de Flooz.")
    add_body(doc, "Le stage s'est déroulé au sein du service Production SI rattaché au département technique, situé à Télésou (« Moov antenne »). Ce service intervient dans la conception, le déploiement, la maintenance et l'optimisation des solutions et infrastructures techniques de l'opérateur. Le sujet du stage est directement lié à la publication des factures clients postpayés et à l'amélioration de l'autonomie des utilisateurs.")
    add_heading(doc, "1.1.3. Processus métier de facturation postpayée", 3)
    add_body(doc, "Un client postpayé souscrit un contrat auprès de l'opérateur. Pour une entreprise, le contrat est porté par un payeur principal et peut regrouper plusieurs lignes attribuées aux employés. Chaque ligne dispose d'un MSISDN, d'un forfait et d'options. La catégorie du contrat, son mode de règlement, ses dates d'effet et de fin et ses services par défaut influencent la manière dont les données doivent être administrées.")
    add_body(doc, "À la clôture d'une période, le système de facturation produit un document global pour l'entreprise et des documents sommaires pour les lignes. Le document global peut comporter plusieurs pages de consommation et de totaux. Le document sommaire présente les usages d'une ligne et peut contenir le nom de l'utilisateur, le MSISDN et le montant de la ligne. Les fichiers peuvent être volumineux, ce qui rend le découpage manuel peu fiable.")
    add_body(doc, "Le rôle de l'agent de facturation commence par la préparation des références. Les contrats et leurs lignes doivent être présents dans la base ; le numéro de facture, le compte entreprise ou le MSISDN doivent correspondre aux informations du PDF. L'agent sélectionne ensuite le type de bloc, la période et le fichier. L'application conserve le traitement et son rapport afin que l'opérateur puisse suivre la publication.")
    add_body(doc, "La publication ne doit pas être confondue avec la création du fichier. Le découpage produit un fichier individuel ; le rapprochement le rattache à une facture en base ; la publication rend la facture accessible au rôle autorisé. Cette séparation explique pourquoi un rapport peut indiquer plusieurs fichiers créés mais moins de factures mises à jour.")
    add_body(doc, "La facturation est également liée à la gestion des services. Les options telles que la facture détaillée, le roaming, l'international, l'incognito ou les options no limit peuvent être définies au contrat puis ajustées sur une ligne. La simulation doit tenir compte de la configuration active au moment du calcul, tandis que l'historique doit conserver le résultat produit.")
    add_table(doc, ["Étape", "Responsable", "Entrées", "Sorties"], [
        ["Préparer les références", "Agent / chef", "Contrats, lignes, comptes, périodes", "Factures candidates en base"],
        ["Produire les PDF", "Système de facturation", "Consommations et tarifs opérateur", "Bloc global ou sommaire"],
        ["Importer le bloc", "Agent", "Fichier PDF et métadonnées", "Traitement EN_ATTENTE"],
        ["Découper et rapprocher", "Celery / service PDF", "Pages et identifiants", "PDF individuels et associations"],
        ["Contrôler le rapport", "Agent / chef", "Résultats, warnings, erreurs", "Décision de correction ou publication"],
        ["Consulter", "Payeur / employé", "Factures publiées", "Aperçu, téléchargement, historique"],
    ], [2100, 2100, 2800, 2760], caption="Tableau 18 : Étapes du processus métier de facturation")
    add_heading(doc, "1.1.4. Organisation du service d'accueil", 3)
    add_body(doc, "Le service d'accueil constitue l'interface entre les besoins opérationnels et les contraintes techniques. Il reçoit les demandes de publication, vérifie la conformité des documents, suit les anomalies et transmet les corrections nécessaires. Le projet a donc été construit en privilégiant la visibilité du traitement et la possibilité de reprendre une opération sans perdre le résultat des blocs correctement traités.")
    add_body(doc, "L'équipe de facturation doit pouvoir travailler avec plusieurs périodes et plusieurs types de documents. La pagination des tableaux, les filtres par période, le statut explicite et la séparation entre historique d'import et publication finale répondent à cette exigence. La gestion des contrats, des commerciaux et des lignes est considérée comme une partie du même processus, car un matching ne peut être fiable que si les données de référence sont cohérentes.")

    add_heading(doc, "1.2. THÈME DU STAGE", 2)
    add_heading(doc, "1.2.1. Présentation du sujet", 3)
    add_body(doc, "Le projet a pour thème : « Développement d'un portail web de publication de factures clients postpayés : cas de Moov Africa Togo ». Une facture globale regroupe la consommation de l'ensemble des lignes rattachées à un contrat, tandis qu'une facture sommaire présente la consommation d'une ligne et est destinée à l'employé titulaire. Le portail doit donc prendre en charge ces deux niveaux de consultation ainsi que le processus interne d'importation et de publication.")
    add_heading(doc, "1.2.2. Problématique du sujet", 3)
    add_body(doc, "Avant le projet, les factures étaient principalement transmises par courrier électronique ou par voie postale à la fin de la période de facturation. Le client ne bénéficiait pas d'un espace centralisé pour consulter ses factures, ses services, son historique ou une estimation de sa consommation. De plus, la gestion des gros blocs PDF demandait des opérations manuelles et ne garantissait pas toujours une association fiable entre le document, le contrat et la ligne concernée.")
    add_body(doc, "La question centrale est donc la suivante : comment concevoir un portail web sécurisé qui automatise la publication des factures globales et sommaires, respecte les droits propres au payeur et à l'employé, et améliore la traçabilité du travail des équipes de facturation ?")
    add_heading(doc, "1.2.3. Intérêt du sujet", 3)
    add_body(doc, "L'intérêt opérationnel est de réduire les manipulations manuelles, d'accélérer la mise à disposition des documents et de diminuer les sollicitations adressées au service client. L'intérêt pour le client est de disposer d'une information accessible à tout moment. Enfin, l'intérêt pédagogique réside dans la mise en œuvre d'une application complète, depuis l'analyse UML jusqu'au déploiement et aux tests.")
    add_heading(doc, "1.2.3.1. Objectifs", 3)
    for item in [
        "Permettre au payeur de consulter la facture globale et les factures sommaires de sa flotte.",
        "Permettre à l'employé de consulter uniquement les données liées à sa ligne.",
        "Importer, analyser et découper des blocs PDF globaux ou sommaires.",
        "Rattacher les PDF aux factures à partir du numéro de facture, du compte ou du MSISDN.",
        "Paramétrer les forfaits et services utilisés par le moteur de simulation.",
        "Fournir un suivi persistant des traitements longs grâce à Celery et Garnet.",
        "Garantir l'authentification, le contrôle des rôles, la journalisation et la protection des données.",
        "Offrir une interface responsive et exploitable par les rôles administratifs, commerciaux et clients.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "1.2.3.2. Résultats attendus", 3)
    add_body(doc, "Le résultat attendu est une application web fonctionnelle composée d'une API sécurisée, d'une interface React et d'une base PostgreSQL. Elle doit permettre la gestion des contrats, commerciaux, payeurs, employés, lignes, forfaits, services, factures, simulations et historiques. Le traitement PDF doit produire un rapport distinguant les documents créés, associés, déjà traités et en erreur, sans bloquer l'interface pendant les opérations longues.")

    add_heading(doc, "1.3. ÉTUDE DE L'EXISTANT", 2)
    add_body(doc, "Le processus existant repose sur la production mensuelle de documents PDF par le système de facturation, puis leur transmission aux clients. Les entreprises reçoivent une facture globale destinée au payeur et des factures sommaires associées aux lignes. Les équipes doivent préparer les blocs, vérifier les correspondances et diffuser les documents. La consultation dépend ensuite du canal de transmission utilisé.")
    add_heading(doc, "1.4. CRITIQUE DE L'EXISTANT", 2)
    for item in [
        "Absence d'une consultation en ligne centralisée et disponible à tout moment.",
        "Difficulté pour le client de suivre sa consommation et d'anticiper le montant de sa facture.",
        "Gestion manuelle des gros fichiers PDF, avec risque d'erreur de découpage ou de rattachement.",
        "Absence d'un contrôle d'accès adapté à la structure d'une flotte.",
        "Manque de traçabilité centralisée des publications, des erreurs et des actions réalisées sur les contrats.",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "1.5. PROPOSITIONS ET CHOIX DE SOLUTIONS", 2)
    add_heading(doc, "1.5.1. Évaluations techniques des solutions", 3)
    add_body(doc, "Trois solutions ont été étudiées. La première consiste à utiliser un outil de visualisation existant. La deuxième consiste à acquérir un portail spécialisé clé en main. La troisième consiste à développer une application web sur mesure. La comparaison tient compte de la gestion des flottes, de la simulation, du traitement PDF et de l'intégration avec les règles métier de Moov Africa Togo.")
    add_table(doc, ["Solution", "Avantages", "Limites"], [
        ["Tableau de bord existant (Power BI / Looker Studio)", "Mise en œuvre rapide, visualisations modernes, coût initial modéré.", "Peu adapté à l'authentification métier, à la simulation et au découpage PDF."],
        ["Portail clé en main", "Fonctionnalités éprouvées, support éditeur, déploiement rapide.", "Coût élevé, personnalisation limitée, dépendance à l'éditeur."],
        ["Développement sur mesure", "Adaptation aux rôles, aux contrats, aux factures et aux règles de Moov Africa.", "Temps de conception, développement et maintenance à prévoir."],
    ], [2500, 3430, 3430], caption="Tableau 2 : Comparaison des solutions envisagées")
    add_heading(doc, "1.5.2. Évaluations financières des solutions proposées", 3)
    add_table(doc, ["Poste", "Description", "Montant estimatif (FCFA)"], [
        ["Matériel de développement", "Ordinateur de développement", "500 000"],
        ["Analyse et conception", "Besoins, UML, architecture", "800 000"],
        ["Backend Django", "API, règles métier, sécurité", "2 000 000"],
        ["Frontend React", "Interfaces et simulation", "2 000 000"],
        ["Base de données", "PostgreSQL", "0"],
        ["Hébergement", "Serveur pendant 12 mois", "360 000"],
        ["Tests et déploiement", "Validation et mise en service", "400 000"],
        ["Formation", "Prise en main des utilisateurs", "300 000"],
        ["Total", "Développement sur mesure", "6 360 000"],
    ], [3100, 4200, 2060], caption="Tableau 3 : Évaluation financière du développement sur mesure")
    add_heading(doc, "1.5.3. Choix de la solution", 3)
    add_body(doc, "Le développement sur mesure a été retenu. Il permet de modéliser précisément les contrats et les lignes, de différencier les droits du payeur et de l'employé, de contrôler le rapprochement des PDF et de faire évoluer les tarifs et services. Il permet également de conserver la maîtrise du code source et de déployer progressivement des fonctions comme les notifications et le traitement asynchrone.")
    add_heading(doc, "1.5.3.1. Évaluation de la maintenance et des évolutions", 3)
    add_body(doc, "Le choix d'une solution sur mesure ne s'arrête pas au coût du développement initial. Le portail doit rester exploitable pendant les périodes de facturation, lorsque les volumes de PDF et les demandes d'assistance augmentent. L'estimation ci-dessous distingue la maintenance corrective, la maintenance préventive et les évolutions fonctionnelles. Il s'agit d'une base de discussion et non d'un devis contractuel : les montants devront être validés par Moov Africa Togo selon ses procédures internes.")
    add_table(doc, ["Type d'intervention", "Contenu", "Fréquence indicative", "Charge relative"], [
        ["Corrective", "Correction d'une anomalie de matching, de permission ou d'affichage.", "Selon incident", "Moyenne"],
        ["Préventive", "Mise à jour des dépendances, sauvegarde, contrôle des journaux et tests de restauration.", "Mensuelle / trimestrielle", "Faible à moyenne"],
        ["Évolutive", "Nouveau format PDF, nouveau canal de notification, nouvelle règle tarifaire ou nouveau rôle.", "Selon besoin métier", "Élevée"],
        ["Support", "Accompagnement des agents, analyse d'un rapport et aide à la reprise d'un traitement.", "À chaque période", "Variable"],
    ], [2300, 4300, 1800, 1560], caption="Tableau 26 : Estimation de la maintenance et des évolutions")
    add_heading(doc, "1.5.4. Contraintes, hypothèses et risques", 3)
    add_body(doc, "L'étude a été menée avec des données de démonstration structurées à partir de la réalité métier communiquée par le service d'accueil. Les fichiers PDF utilisés pour les essais ne présentent pas tous la même organisation : certains blocs sont sommaires et identifiables par le MSISDN, tandis que les blocs globaux sont identifiables par le compte entreprise. Le moteur doit donc tolérer les pages de continuation et signaler les pages sans identifiant plutôt que de les attribuer arbitrairement.")
    add_table(doc, ["Risque", "Probabilité", "Impact", "Mesure préventive"], [
        ["Format PDF modifié", "Moyenne", "Élevé", "Centraliser les expressions de détection, conserver les erreurs par page et prévoir un contrôle manuel."],
        ["Donnée client absente", "Moyenne", "Élevé", "Valider les contrats, comptes et MSISDN avant publication."],
        ["Traitement trop long", "Élevée", "Moyen", "Exécuter le découpage dans Celery et persister la progression."],
        ["Accès indu à une facture", "Faible", "Très élevé", "Appliquer les permissions côté API, filtrer par contrat et tester chaque rôle."],
        ["Perte d'un fichier média", "Faible", "Élevé", "Mettre en place des sauvegardes, un stockage privé et une politique de rétention."],
        ["Tarif mal paramétré", "Moyenne", "Moyen", "Réserver la configuration aux rôles habilités et enregistrer les modifications."],
    ], [2200, 1400, 1400, 4760], caption="Tableau 11 : Principaux risques et mesures de maîtrise")
    add_heading(doc, "1.5.5. Règles métier retenues", 3)
    for item in [
        "Un numéro mobile est composé de huit chiffres dans les formulaires de gestion ; le MSISDN reste unique dans la base.",
        "Un contrat est rattaché à une entreprise, à un payeur et, lorsque l'information est connue, à un commercial.",
        "Une demande saisie par un commercial n'entraîne pas automatiquement la création du contrat : elle reste en attente jusqu'à validation.",
        "Les services sélectionnés au niveau du contrat sont hérités par les nouvelles lignes, avec possibilité de retirer un service sur une ligne particulière.",
        "Une facture globale est associée à l'entreprise ; une facture sommaire est associée à une ligne et donc à son employé éventuel.",
        "Une facture dont le PDF est déjà traité ne doit pas être republiée silencieusement : elle est signalée comme déjà traitée.",
        "Un rejet de demande doit comporter un motif consultable par le commercial qui a soumis la demande.",
        "Une simulation est informative et ne modifie pas la facture réelle ; son résultat est cependant conservé dans l'historique de l'utilisateur.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "1.5.6. Périmètre fonctionnel", 3)
    add_body(doc, "Le périmètre couvre le portail web, la gestion des comptes et des rôles, les contrats et lignes, le catalogue des forfaits et services, l'import et la publication des PDF, la consultation côté client, la simulation, la traçabilité et les tâches asynchrones. L'intégration directe avec le système de facturation central de l'opérateur, l'OCR de documents image et la mise en production sur une infrastructure haute disponibilité restent hors du périmètre de ce stage.")
    add_heading(doc, "1.6. PLANNING PRÉVISIONNEL DE RÉALISATION", 2)
    add_table(doc, ["N°", "Activité", "Période", "Statut"], [
        ["1", "Prise de contact et compréhension du thème", "11 - 17 mai 2026", "Réalisée"],
        ["2", "Analyse des besoins", "18 - 26 mai 2026", "Réalisée"],
        ["3", "Cahier des charges", "27 - 30 mai 2026", "Réalisée"],
        ["4", "Analyse, conception et UML", "30 mai - 7 juin 2026", "Réalisée"],
        ["5", "Développement backend et frontend", "8 juin - 7 juillet 2026", "Réalisée"],
        ["6", "Tests et corrections", "8 - 14 juillet 2026", "Réalisée"],
        ["7", "Déploiement et préparation de livraison", "15 - 17 juillet 2026", "Réalisée"],
        ["8", "Rédaction du mémoire", "18 juillet - 1 août 2026", "En cours"],
        ["9", "Préparation de la soutenance", "2 - 8 août 2026", "À finaliser"],
    ], [600, 4200, 2500, 2060], caption="Tableau 4 : Planning prévisionnel de réalisation")

    # PART 2
    add_part_heading(doc, "PARTIE 2 : ANALYSE ET CONCEPTION")
    add_body(doc, "Cette partie présente le passage des besoins métier vers une solution modélisée. La démarche suit une progression volontairement lisible : compréhension du domaine, identification des acteurs, formalisation des exigences, description des scénarios, représentation UML, puis préparation de la structure de données. Cette organisation reprend la logique des mémoires de référence tout en l'adaptant au portail Moov e-Factures.")
    add_heading(doc, "2.1. CHOIX DE LA MÉTHODE D'ANALYSE ET JUSTIFICATION", 2)
    add_body(doc, "Le projet a été conduit avec une approche orientée objet. Cette approche est adaptée à un domaine composé d'entités persistantes et liées, telles que l'utilisateur, le contrat, la ligne, le forfait, le service, la facture et la publication. Elle permet de représenter les responsabilités, les relations et les évolutions du système avant l'implémentation.")
    add_body(doc, "Le processus 2TUP a été retenu pour organiser le travail. Sa branche fonctionnelle clarifie les besoins, les acteurs et les scénarios métier. Sa branche technique étudie l'architecture, la sécurité, la persistance et le traitement des PDF. La branche de réalisation réunit ces deux analyses dans une solution progressive et testable.")
    add_heading(doc, "2.2. CHOIX DE L'OUTIL DE MODÉLISATION ET JUSTIFICATION", 2)
    add_body(doc, "UML a été choisi comme langage de modélisation, car il permet de documenter les vues fonctionnelles, statiques et dynamiques du système. Draw.io a servi à produire les diagrammes de contexte et de classes grâce à ses bibliothèques UML et à son export dans des formats intégrables au mémoire. PlantUML et Mermaid peuvent également être utilisés pour versionner les diagrammes sous forme textuelle et faciliter leurs mises à jour.")
    add_heading(doc, "2.3. ÉTUDE DÉTAILLÉE DE LA SOLUTION", 2)
    add_heading(doc, "2.3.0. Démarche d'étude préliminaire", 3)
    add_body(doc, "L'étude préliminaire a consisté à observer le circuit de facturation postpayée, à relever les informations présentes dans les contrats et les PDF, puis à confronter ces informations aux parcours attendus par chaque rôle. Cette étape a permis de distinguer les données de référence, qui doivent être fiables avant tout import, des données produites par le traitement, qui sont enregistrées dans l'historique. Elle a également conduit à séparer explicitement la facture globale de la facture sommaire, car les deux documents n'utilisent pas le même identifiant de rapprochement.")
    add_heading(doc, "2.3.1. Acteurs et responsabilités", 3)
    add_table(doc, ["Acteur", "Responsabilités principales"], [
        ["Super administrateur", "Administre les utilisateurs, les rôles, les contrats, les lignes, les services, les forfaits et la configuration globale."],
        ["Chef de facturation", "Valide ou rejette les demandes commerciales, supervise les agents, les publications, les tarifs et les historiques."],
        ["Agent de facturation", "Gère les clients et lignes autorisés, importe et publie les PDF, gère les services et suit les erreurs."],
        ["Commercial", "Saisit une demande de contrat ; le contrat n'est créé qu'après décision d'un agent habilité."],
        ["Payeur", "Consulte le contrat, la facture globale, les factures sommaires de sa flotte et les simulations."],
        ["Employé", "Consulte sa ligne, ses services, sa facture sommaire et son historique de simulations."],
        ["Service de messagerie", "Reçoit les demandes d'envoi d'e-mails lorsque le SMTP est configuré."],
    ], [2500, 6860], caption="Tableau 5 : Acteurs et responsabilités")
    add_heading(doc, "2.3.1.1. Description fonctionnelle des acteurs", 3)
    add_body(doc, "Dans Moov e-Factures, les acteurs principaux sont les utilisateurs humains authentifiés. Le système distingue six rôles : super administrateur, chef de facturation, agent de facturation, commercial, payeur et employé. Les droits sont contrôlés par l'API selon le rôle, l'état du compte et, pour les clients, le contrat ou la ligne auxquels ils sont rattachés.")
    add_body(doc, "Le super administrateur dispose de la vision la plus large. Il administre les comptes, les rôles, les statuts, les entreprises/contrats, les lignes, les forfaits et les services. Il peut consulter les factures et les historiques et intervenir sur la configuration générale. La publication quotidienne reste toutefois une opération de facturation : elle est principalement réalisée depuis les espaces chef ou agent.", bold_prefix="Le super administrateur")
    add_body(doc, "Le chef de facturation assure la supervision de l'activité. Il peut gérer les agents de son périmètre, consulter les demandes commerciales, les contrats, les commerciaux et les publications, administrer les tarifs et les services autorisés et valider ou rejeter une demande de contrat. En cas de rejet, le motif est obligatoire et est restitué au commercial.", bold_prefix="Le chef de facturation")
    add_body(doc, "L'agent de facturation réalise les opérations courantes : gestion des contrats et des lignes qui lui sont accessibles, association d'employés, gestion opérationnelle des forfaits et services selon ses droits, import et découpage des blocs PDF, rapprochement avec les factures, publication et analyse de l'historique. Il peut également traiter les demandes de contrat lorsque son rôle et ses permissions l'autorisent.", bold_prefix="L'agent de facturation")
    add_body(doc, "Le commercial ne crée pas directement un contrat actif. Il renseigne et soumet une demande de contrat contenant les informations du client, du payeur et du contrat proposé, puis suit son statut. La demande reste en attente jusqu'à la décision d'un agent habilité, du chef ou du super administrateur. Après validation, le contrat et le compte payeur sont créés par le processus de validation ; après rejet, le commercial consulte le motif enregistré.", bold_prefix="Le commercial")
    add_body(doc, "Le payeur est l'utilisateur représentant l'entreprise cliente. Il ne voit que les factures publiées rattachées à son contrat/entreprise : la facture globale et, lorsque les associations sont correctes, les factures sommaires des lignes de sa flotte. Il consulte ses lignes, les services souscrits, effectue des simulations et consulte son historique. Dans l'implémentation, il se connecte avec l'e-mail ou le nom d'utilisateur configuré pour son compte ; le numéro de contrat n'est un identifiant de connexion que s'il a été enregistré comme nom d'utilisateur.", bold_prefix="Le payeur")
    add_body(doc, "L'employé est rattaché à une ligne par son MSISDN. Il consulte uniquement les factures sommaires publiées de sa ligne, les services et le forfait qui lui sont associés, effectue une simulation individuelle et gère les éléments autorisés de son profil. La connexion accepte l'e-mail ou le nom d'utilisateur enregistré ; dans les données de test, le nom d'utilisateur peut correspondre au MSISDN.", bold_prefix="L'employé")
    add_body(doc, "Le worker Celery, Garnet et le service SMTP ne sont pas des rôles utilisateurs. Ce sont des composants techniques : Celery exécute les imports PDF longs, Garnet transporte les tâches et conserve les résultats/cache, tandis que SMTP peut envoyer un e-mail si la configuration est activée. Le SMS n'est pas retenu comme fonction active dans la version actuelle.")
    add_heading(doc, "2.3.1.2. Inventaire des cas d'utilisation par module", 3)
    add_body(doc, "L'inventaire suivant sert de passerelle entre les acteurs et les scénarios détaillés. Il reprend les modules réellement présents dans l'application et permet de vérifier qu'une fonction n'est pas décrite sans responsable ni résultat attendu.")
    add_table(doc, ["Module", "Cas d'utilisation principaux", "Acteurs concernés", "Résultat attendu"], [
        ["Accès et sécurité", "Se connecter, activer le 2FA, modifier le mot de passe", "Tous", "Session protégée et profil contrôlé"],
        ["Contrats", "Créer, consulter, modifier, valider, rejeter, résilier", "Administrateur, chef, agent, commercial", "Contrat ou demande tracé avec son statut"],
        ["Lignes et catalogue", "Associer une ligne, affecter un employé, gérer forfaits et services", "Administrateur, chef, agent", "Référentiel exploitable pour le matching et la simulation"],
        ["Publication", "Importer, découper, rapprocher, publier et suivre un PDF", "Chef, agent", "Fichiers individuels et rapport persistant"],
        ["Espace client", "Consulter facture globale/sommaire, télécharger, simuler", "Payeur, employé", "Accès limité aux données autorisées"],
    ], [1800, 3900, 2200, 1960], caption="Tableau 27 : Inventaire des cas d'utilisation par module")
    add_heading(doc, "2.3.2. Exigences fonctionnelles", 3)
    add_table(doc, ["Référence", "Exigence", "Acteurs"], [
        ["EF-01", "S'authentifier et être redirigé vers l'espace correspondant au rôle.", "Tous"],
        ["EF-02", "Créer, modifier, activer ou suspendre un utilisateur.", "Super administrateur, chef"],
        ["EF-03", "Créer un contrat ou soumettre une demande de contrat.", "Chef, agent, commercial"],
        ["EF-04", "Valider ou rejeter une demande avec motif traçable.", "Chef, agent habilité"],
        ["EF-05", "Associer des lignes à une entreprise et à un employé.", "Administrateurs, agents"],
        ["EF-06", "Importer et découper un bloc PDF global ou sommaire.", "Agent, chef"],
        ["EF-07", "Rattacher les PDF aux factures par identifiants fiables.", "Système"],
        ["EF-08", "Publier les factures et consulter l'historique des traitements.", "Agent, chef"],
        ["EF-09", "Gérer les forfaits, options et tarifs de simulation.", "Administrateurs, facturation"],
        ["EF-10", "Consulter et simuler une facturation, avec historique.", "Payeur, employé"],
        ["EF-11", "Exporter un contrat ou télécharger une facture PDF.", "Rôles autorisés"],
    ], [1200, 5700, 2460], caption="Tableau 6 : Exigences fonctionnelles principales")
    add_heading(doc, "2.3.3. Exigences non fonctionnelles", 3)
    for item in [
        "Sécurité : les mots de passe sont hachés ; les API sont protégées par JWT et les permissions par rôle.",
        "Confidentialité : un employé ne doit pas accéder aux factures des autres lignes ; un payeur est limité à son contrat.",
        "Traçabilité : les modifications importantes et les traitements de publication sont enregistrés.",
        "Performance : un gros PDF est confié à une tâche Celery afin que la requête HTTP ne reste pas bloquée.",
        "Maintenabilité : le frontend, l'API, les services PDF, les tâches et la persistance sont séparés.",
        "Ergonomie : l'interface utilise des tableaux paginés, des messages de succès, d'avertissement et d'erreur distincts.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "2.3.4. Scénarios fonctionnels principaux", 3)
    add_heading(doc, "a) Consulter une facture", 3)
    add_body(doc, "Le client authentifié ouvre la rubrique « Mes factures ». Le système filtre les documents auxquels son rôle lui donne accès. Le payeur peut consulter la facture globale et les factures sommaires de sa flotte ; l'employé ne reçoit que les factures associées à sa ligne. Le téléchargement n'est proposé que lorsque le fichier PDF existe et que l'autorisation est vérifiée.")
    add_heading(doc, "b) Publier un bloc PDF", 3)
    add_body(doc, "L'agent sélectionne le type de document, la période et le fichier. Le système crée un traitement persistant avec le statut EN_ATTENTE, puis Celery le prend en charge. Le processeur vérifie le PDF, extrait les identifiants, détecte les blocs, crée les fichiers individuels et tente le rapprochement. Le résultat distingue les correspondances réussies, les factures déjà traitées et les erreurs. L'agent peut quitter la page pendant le traitement et consulter l'état depuis l'historique.")
    add_heading(doc, "c) Simuler une facturation", 3)
    add_body(doc, "L'utilisateur choisit une ligne et saisit ses consommations voix, SMS et data ou sélectionne les services proposés. Le backend applique les forfaits et les paliers tarifaires configurés. Le résultat détaillé est enregistré dans l'historique afin de permettre une comparaison ultérieure.")
    add_heading(doc, "2.3.4.1. Fiches d'identification des cas critiques", 3)
    add_body(doc, "À la manière d'un sommaire d'identification, chaque fiche précise l'acteur principal, les préconditions, le déclencheur et la sortie observable. Cette formalisation facilite ensuite la rédaction des tests et la vérification des permissions.")
    add_table(doc, ["Cas", "Acteur principal", "Préconditions", "Déclencheur", "Postcondition"], [
        ["S'authentifier", "Utilisateur", "Compte actif et identifiants connus", "Valider le formulaire", "Jetons délivrés et espace du rôle affiché"],
        ["Soumettre une demande", "Commercial", "Informations contractuelles complètes", "Cliquer sur Soumettre", "Demande PENDING visible au valideur"],
        ["Publier un bloc PDF", "Agent", "Période, type et fichier valides", "Lancer le traitement", "Traitement terminé avec rapport et associations"],
        ["Consulter une facture", "Payeur / employé", "Facture publiée et droit vérifié", "Ouvrir Mes factures", "Métadonnées réelles et PDF disponible si attaché"],
        ["Simuler", "Payeur / employé", "Ligne et catalogue actifs", "Calculer", "Montant détaillé et historique mis à jour"],
    ], [1800, 1800, 2500, 1900, 1960], caption="Tableau 28 : Fiches d'identification des cas d'utilisation critiques")
    add_heading(doc, "2.3.5. Diagramme de classes", 3)
    add_body(doc, "Le modèle de classes est organisé autour de l'utilisateur et de ses rôles, de l'entreprise/contrat, des lignes et des factures. Les classes de configuration (Package, Service, Cycle), de suivi (Publication, TraitementPDF, HistoriqueFacturation, AuditContrat) et de simulation complètent le noyau métier. Le diagramme ci-dessous reprend la modélisation détaillée utilisée comme référence avant l'implémentation Django.")
    if CLASS_DIAGRAM.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        p.add_run().add_picture(str(CLASS_DIAGRAM), width=Inches(6.3))
        add_caption(doc, "Figure 1 : Diagramme de classes du portail Moov e-Factures.")
    add_body(doc, "Dans l'implémentation, Company représente le contrat ou l'entreprise facturée. Line porte le MSISDN et le lien éventuel vers User, tandis que Invoice référence le contrat, la ligne et le fichier PDF. ContractRequest permet de séparer la saisie commerciale de la validation. TraitementPDF conserve l'état d'un import long et Publication conserve la trace de la mise à disposition des documents.")
    add_heading(doc, "2.3.5.1. Diagrammes d'activité et de séquence", 3)
    add_body(doc, "Le diagramme d'activité du cas « Publier un bloc PDF » représente les décisions successives : contrôler le fichier, extraire le texte, détecter un identifiant, fermer un bloc, tenter le matching et enregistrer le résultat. Les branches d'erreur ne ferment pas nécessairement le traitement complet : un bloc non associé est signalé tandis que les blocs valides peuvent continuer.")
    add_body(doc, "Le diagramme de séquence met en relation l'agent, le frontend React, l'API Django, la base PostgreSQL, le broker Garnet et le worker Celery. La requête HTTP crée d'abord TraitementPDF et retourne un identifiant. Le worker met à jour les statuts, puis le frontend interroge l'état jusqu'à TERMINE ou ECHEC. Pour la consultation, la séquence est plus courte : l'utilisateur appelle l'API, la permission filtre la facture et la route PDF renvoie le fichier réel.")
    add_table(doc, ["Vue UML", "Question traitée", "Livrable du projet"], [
        ["Cas d'utilisation", "Qui fait quoi dans le portail ?", "Fichier PlantUML par acteur et matrice des droits"],
        ["Activité", "Quelles décisions et exceptions composent un traitement ?", "Flux de publication et de simulation"],
        ["Séquence", "Quels composants collaborent et dans quel ordre ?", "Échanges React, API, PostgreSQL, Celery et Garnet"],
        ["Classes", "Quelles entités et relations doivent être persistées ?", "Diagramme de classes et dictionnaire métier"],
    ], [1800, 3300, 4860], caption="Tableau 29 : Correspondance entre vues UML et livrables")
    add_heading(doc, "2.3.6. Description textuelle du cas « S'authentifier »", 3)
    add_body(doc, "Sommaire d'identification : l'acteur est tout utilisateur actif du portail ; le déclencheur est l'envoi du formulaire de connexion ; la précondition est l'existence d'un compte actif. Le système vérifie l'identifiant, le mot de passe et, si le 2FA est activé, le code TOTP. En cas de succès, il délivre les jetons d'accès et de renouvellement puis redirige l'utilisateur vers son espace.")
    add_body(doc, "Le scénario nominal est le suivant : l'utilisateur saisit ses informations, l'API recherche le compte, contrôle le statut ACTIF, vérifie le mot de passe, demande éventuellement l'OTP et renvoie les jetons JWT. Les alternatives sont un compte inactif, un mot de passe incorrect, un OTP expiré ou un compte inexistant. Dans tous les cas d'échec, le système ne révèle pas d'information sensible sur l'existence du compte.")
    add_heading(doc, "2.3.7. Description textuelle du cas « Créer et valider un contrat »", 3)
    add_body(doc, "Le commercial renseigne le compte proposé, la raison sociale, la catégorie, les adresses, le mode de règlement, les dates, les services par défaut et le payeur. À la validation du formulaire, le système contrôle les champs obligatoires et crée une ContractRequest au statut PENDING. Aucun contrat exploitable n'est créé à cette étape.")
    add_body(doc, "Le chef ou l'agent habilité ouvre le détail de la demande, vérifie les informations et choisit « Valider » ou « Rejeter ». La validation crée ou active l'entreprise et le contrat, conserve le commercial d'origine et journalise la décision. Le rejet exige un commentaire ; celui-ci est conservé dans decision_comment et devient visible dans l'espace du commercial. Une double validation ou une décision sur une demande déjà traitée est refusée.")
    add_heading(doc, "2.3.8. Description textuelle du cas « Publier un bloc PDF »", 3)
    add_body(doc, "Préconditions : l'agent est authentifié, le fichier est au format PDF, la période est connue et les factures candidates existent dans la base. Le traitement commence par une validation de taille, de chiffrement et de nombre de pages. Pour chaque page, le service extrait le texte et recherche un MSISDN, un compte entreprise, un numéro de facture et, lorsque la structure le permet, la date d'émission.")
    add_body(doc, "Lorsqu'un nouvel identifiant est rencontré, un bloc est ouvert ; les pages suivantes sont ajoutées jusqu'à l'apparition d'un autre identifiant. PdfWriter génère un fichier indépendant par bloc. Le rapprochement utilise le numéro de facture exact en priorité, puis le MSISDN pour les factures sommaires et le compte pour les factures globales. Une correspondance modifie la facture, associe le fichier, conserve les métadonnées extraites et fait évoluer son statut. Les anomalies sont ajoutées au rapport sans annuler les blocs correctement traités.")
    add_heading(doc, "2.3.9. Description textuelle du cas « Consulter et télécharger une facture »", 3)
    add_body(doc, "Le payeur ou l'employé ouvre la page des factures. L'API applique le périmètre d'accès avant de retourner la liste. Le payeur reçoit les documents de son contrat, alors que l'employé reçoit uniquement ceux dont la ligne est liée à son compte. L'interface affiche les métadonnées extraites du PDF, notamment le numéro réel, la date d'émission et le montant enregistré.")
    add_body(doc, "Lorsque le fichier existe, l'utilisateur peut l'ouvrir dans un nouvel onglet ou le télécharger. Une facture sans fichier reste visible avec un état « manquant » afin que l'agent puisse corriger l'association. Une session expirée, un fichier absent ou un accès interdit provoque un message explicite et ne doit jamais exposer le chemin interne du serveur.")
    add_heading(doc, "2.3.10. Description textuelle du cas « Simuler une facturation »", 3)
    add_body(doc, "L'utilisateur sélectionne une ligne et introduit ses consommations. Le moteur additionne le forfait, les options et les usages. La consommation voix est facturée à 79 FCFA par minute avec un pas de 30 secondes ; les SMS sont facturés à 30 FCFA l'unité ; la data applique les paliers configurés, notamment les paliers de 1, 7, 15, 35, 85 et 275 Go. Le résultat détaillé indique la contribution de chaque élément.")
    add_body(doc, "La simulation ne change pas le statut de la facture et ne déclenche pas une publication. Elle est enregistrée dans Simulation avec le montant estimé, la date, les services sélectionnés et un résultat JSON. L'utilisateur peut donc consulter ultérieurement l'historique et comparer plusieurs hypothèses de consommation.")
    add_heading(doc, "2.3.11. Dictionnaire des données métier", 3)
    add_table(doc, ["Objet", "Attributs représentatifs", "Règle de gestion"], [
        ["User", "email, role, status, telephone, two_factor_enabled", "Le rôle et le statut déterminent les droits ; le téléphone est limité à huit chiffres dans les formulaires."],
        ["Company", "compte, raison_sociale, categorie, dates, services par défaut", "Le compte identifie l'entreprise ; les services par défaut sont hérités par les lignes."],
        ["Line", "msisdn, utilisateur, forfait, cycle, options, employe", "Le MSISDN est unique ; la ligne appartient à une entreprise."],
        ["Invoice", "numero_facture, periode, montant, statut, fichier_pdf", "Le numéro et la période servent à retrouver la facture ; le fichier permet la consultation."],
        ["Package / Service", "nom, code, prix, type, quota, actif", "Seuls les éléments actifs sont proposés dans la simulation."],
        ["TraitementPDF", "type_facture, statut, progression, resultat, erreur", "L'état est conservé même si l'utilisateur quitte la page."],
        ["Simulation", "montant_estime, services, resultat_detaille", "Une simulation est une estimation historisée, pas une facture."],
    ], [2000, 3900, 3760], caption="Tableau 12 : Dictionnaire synthétique des données métier")
    add_heading(doc, "2.3.12. Matrice des droits par rôle", 3)
    add_table(doc, ["Fonction", "Administrateur", "Chef / agent", "Commercial", "Payeur", "Employé"], [
        ["Consulter les contrats", "Toutes les données", "Périmètre autorisé", "Demandes soumises", "Son contrat", "Contrat lié"],
        ["Créer un contrat", "Oui", "Oui", "Demande uniquement", "Non", "Non"],
        ["Valider une demande", "Oui", "Oui", "Non", "Non", "Non"],
        ["Gérer une ligne", "Oui", "Oui selon permission", "Non", "Ses lignes selon droit", "Sa ligne"],
        ["Importer un PDF", "Oui", "Oui", "Non", "Non", "Non"],
        ["Publier une facture", "Oui", "Oui", "Non", "Non", "Non"],
        ["Consulter une facture", "Toutes", "Selon rôle", "Non", "Son contrat", "Sa ligne"],
        ["Gérer les tarifs", "Oui", "Chef / agent habilité", "Non", "Non", "Non"],
        ["Simuler", "Pour test", "Pour test", "Non", "Oui", "Oui"],
    ], [1900, 1450, 1700, 1450, 1450, 1410], caption="Tableau 19 : Matrice synthétique des droits")
    add_body(doc, "Cette matrice est une vue fonctionnelle. La sécurité effective est appliquée par l'API, qui ne doit jamais faire confiance à un filtre envoyé par le navigateur. Par exemple, un employé qui modifie l'identifiant d'une facture dans l'URL doit recevoir une réponse d'accès refusé si la facture n'est pas reliée à sa ligne. Le frontend masque les actions non autorisées pour améliorer l'ergonomie, mais le contrôle backend reste la protection principale.")
    add_heading(doc, "2.3.13. Règles de validation des formulaires", 3)
    for item in [
        "Le compte entreprise et le code contrat doivent être non vides et uniques dans leur périmètre.",
        "La date de fin ne peut pas être antérieure à la date d'effet ; une date de résiliation est obligatoire lorsque le contrat est déclaré résilié.",
        "Le motif de rejet est obligatoire pour une décision REJECTED ; le commentaire est conservé dans l'historique.",
        "Le téléphone de l'utilisateur doit comporter huit chiffres après suppression des espaces éventuels.",
        "Le prix d'un forfait ou d'une option est un nombre positif ; la valeur zéro reste possible uniquement si le catalogue l'autorise explicitement.",
        "Un MSISDN déjà présent ne peut pas être recréé ; l'interface doit proposer l'association de la ligne existante plutôt qu'une seconde création.",
        "Un PDF global ne doit pas être traité comme un PDF sommaire, car les identifiants et la cardinalité des factures sont différents.",
        "Les périodes doivent être complètes avant de lancer un traitement, afin d'éviter une association sur une mauvaise facture.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "2.3.14. Scénarios nominaux et alternatifs", 3)
    add_body(doc, "Scénario nominal de création de ligne : l'agent sélectionne un payeur et une entreprise, ouvre l'action d'ajout de ligne, choisit un MSISDN disponible ou saisit un numéro conforme, renseigne le forfait et le cycle, puis affecte l'employé. Le système vérifie l'unicité et crée la relation. Si l'employé n'existe pas, l'agent peut ouvrir le formulaire de création avec le numéro prérempli et non modifiable.")
    add_body(doc, "Scénario alternatif d'une ligne existante : le numéro est déjà présent dans la base. Au lieu d'afficher une erreur générique, le système doit préciser que la ligne existe et proposer son association au payeur sélectionné, sous réserve des droits de l'agent. Cette règle évite les doublons et explique pourquoi la fonctionnalité « sélectionner depuis la base » est nécessaire.")
    add_body(doc, "Scénario nominal de publication : le fichier est accepté, le traitement passe de EN_ATTENTE à EN_COURS, les blocs sont générés et les associations réussissent. Le statut du traitement passe à TERMINE et l'historique conserve l'agent, la période, le nombre de fichiers et le rapport. Scénario partiel : certains blocs sont associés et d'autres sont signalés en rouge ; les associations réussies restent disponibles.")
    add_body(doc, "Scénario d'échec : le fichier est chiffré, vide, trop volumineux ou ne contient aucun identifiant exploitable. Le traitement passe à ECHEC, la progression est terminée et le champ erreur explique la cause. L'agent corrige le fichier ou les données de référence avant une nouvelle tentative.")
    add_heading(doc, "2.3.15. Lecture des diagrammes UML", 3)
    add_body(doc, "Le diagramme de contexte délimite le portail et présente les échanges avec les utilisateurs internes, les clients et les services externes. Il répond à la question « qui échange avec le système et pour quelle information ? ». Cette vue est utile au début de l'étude car elle évite de confondre une fonction interne du portail avec une fonction du système de facturation qui lui fournit les PDF.")
    add_body(doc, "Le diagramme de cas d'utilisation décrit les objectifs des acteurs. Les cas « s'authentifier », « gérer un contrat », « publier les blocs PDF », « consulter une facture » et « simuler une facturation » représentent les parcours majeurs. Les relations include et extend sont utilisées avec prudence : la consultation des détails est incluse dans une validation, tandis que la saisie d'un motif étend le rejet.")
    add_body(doc, "Le diagramme d'activité de la publication commence par la sélection du fichier et se poursuit par les décisions de validation, d'analyse, de découpage et de matching. Les branches « succès », « succès partiel » et « échec » rendent visibles les états possibles. Cette représentation a conduit à persister un objet TraitementPDF plutôt qu'à garder le résultat uniquement en mémoire dans la requête HTTP.")
    add_body(doc, "Le diagramme de séquence montre les messages entre l'agent, l'interface React, l'API, la tâche Celery, le service PDF et la base. L'API répond avec un task_id ; le worker effectue ensuite les opérations longues. Le frontend interroge l'état et affiche la progression. Pour une facture, une séquence analogue met en relation le client, l'API d'autorisation, la base et le stockage média.")
    add_body(doc, "Le diagramme de classes fournit la vue statique du domaine. Les associations Company-Line-Invoice décrivent le cœur de la facturation ; Package-Service-TarifService décrivent le catalogue ; ContractRequest, AuditContrat et HistoriqueFacturation décrivent les traces ; TraitementPDF et Simulation décrivent les traitements différés et les calculs. Les classes User et Role sont transversales car elles conditionnent les permissions de chaque opération.")
    add_heading(doc, "2.3.16. Justification de la séparation contrat / lignes", 3)
    add_body(doc, "Le contrat contient les informations communes à l'entreprise : catégorie, commercial, mode de règlement, adresses, dates, exonération, type de revenu, observation, résiliation et services par défaut. Les lignes contiennent les informations propres à chaque MSISDN : utilisateur, forfait, cycle, options et statut. Cette séparation évite de recopier les mêmes données sur chaque facture et autorise une personnalisation par ligne.")
    add_body(doc, "Lorsqu'un contrat est créé, les services par défaut ne doivent pas être interprétés comme une activation irrévocable. Ils servent de base aux nouvelles lignes ; une ligne peut retirer une option qui ne lui est pas applicable. Le journal d'audit conserve les modifications afin que l'équipe puisse expliquer pourquoi un service était actif à une date donnée.")
    add_heading(doc, "2.3.17. Justification de la séparation globale / sommaire", 3)
    add_body(doc, "Une facture globale est unique au niveau d'un contrat et peut couvrir plusieurs lignes. Une facture sommaire est rattachée à une ligne ; deux factures sommaires d'une même entreprise ne doivent jamais être confondues. La sélection du type de document dans l'interface sert donc à choisir le bon algorithme de détection et le bon ordre des critères de rapprochement.")
    add_body(doc, "Cette règle est également importante pour les droits de consultation. Le payeur peut ouvrir la facture globale ainsi que les factures sommaires de son contrat, tandis qu'un employé ne reçoit que le document lié à la ligne qui lui est affectée. Le backend ne se base pas seulement sur l'identifiant visible du document, mais vérifie la relation entre la facture, la ligne, le contrat et l'utilisateur.")
    add_heading(doc, "2.3.18. Catalogue détaillé des classes métier", 3)
    add_table(doc, ["Classe", "Rôle dans le système", "Principales opérations"], [
        ["User", "Compte authentifié et profil de sécurité.", "Connexion, profil, changement de mot de passe, 2FA."],
        ["StatusHistory", "Historique des changements de statut utilisateur.", "Enregistrer l'ancien et le nouveau statut, le motif et l'auteur."],
        ["Commercial", "Interlocuteur qui signe ou propose le contrat.", "Créer, modifier, activer, affecter à une entreprise."],
        ["Company", "Entreprise et contrat de facturation.", "Gérer catégorie, dates, adresses, services et résiliation."],
        ["ContractRequest", "Demande avant création effective.", "Soumettre, valider, rejeter avec motif."],
        ["AuditContrat", "Journal d'actions sur un contrat.", "Tracer création, modification, ligne et résiliation."],
        ["Line", "Ligne mobile rattachée à un contrat.", "Gérer MSISDN, employé, forfait, cycle et options."],
        ["LineService", "Service d'une ligne sur une période.", "Activer, désactiver, dater l'application."],
        ["Package", "Forfait commercial et ses quotas.", "Gérer code, prix, type et statut actif."],
        ["Service", "Option, pass ou promotion.", "Gérer type, prix, période et disponibilité."],
        ["TarifService", "Règle de prix utilisée dans un calcul.", "Définir valeur, unité, seuil et dates."],
        ["Invoice", "Facture globale ou sommaire.", "Stocker montant, période, statut et fichier."],
        ["Publication", "Trace d'une publication ou d'un import.", "Conserver agent, période, compteurs et commentaire."],
        ["TraitementPDF", "État persistant d'une tâche asynchrone.", "Suivre statut, progression, résultat et erreur."],
        ["HistoriqueFacturation", "Historique des transitions d'une facture.", "Enregistrer auteur, ancien statut et nouveau statut."],
        ["Simulation", "Estimation historisée d'un utilisateur.", "Calculer et conserver montant et détail."],
        ["NotificationFacture", "Résultat d'une notification.", "Conserver canal, destinataire, statut et erreur."],
        ["Cycle", "Période d'application d'un service ligne.", "Définir début, fin et état actif."],
    ], [1900, 3900, 3760], caption="Tableau 25 : Catalogue détaillé des classes métier")
    add_body(doc, "La liste ci-dessus montre que le modèle n'est pas limité à une table facture. Les classes de référence et d'historique sont nécessaires pour rendre le portail maintenable. La distinction entre Invoice et Publication permet de conserver la facture comme objet consultable et la publication comme événement d'exploitation. De même, TraitementPDF est différent de Publication car un import peut produire des fichiers sans que l'agent ait encore validé leur mise à disposition.")

    # PART 3
    add_part_heading(doc, "PARTIE 3 : RÉALISATION ET MISE EN ŒUVRE")
    add_body(doc, "Cette partie décrit la transformation des modèles en composants exécutables. Elle présente les choix logiciels et matériels, l'architecture en couches, la sécurité, la base de données, les échanges API et les traitements asynchrones. Les extraits et tableaux sont volontairement centrés sur les points qui conditionnent la fiabilité de la publication : persistance du statut, exactitude du matching et contrôle de l'accès au PDF.")
    add_heading(doc, "3.1. MATÉRIELS ET LOGICIELS UTILISÉS", 2)
    add_table(doc, ["Élément", "Choix", "Pertinence"], [
        ["Backend", "Python, Django, Django REST Framework", "Structure robuste, ORM, validation, API REST et intégration JWT."],
        ["Frontend", "React, Vite, JavaScript, styles utilitaires", "Navigation SPA, composants réutilisables et interfaces par rôle."],
        ["Base de données", "PostgreSQL", "Contraintes relationnelles, indexation et persistance adaptée à la production."],
        ["Tâches asynchrones", "Celery + Garnet", "Découpage PDF et notifications exécutés hors de la requête HTTP."],
        ["Traitement documentaire", "PyPDF2 / PdfReader / PdfWriter", "Extraction de texte, détection d'identifiants et création de fichiers."],
        ["Modélisation", "UML, Draw.io, PlantUML", "Documentation des acteurs, classes et scénarios."],
        ["Tests", "Django TestCase, tests manuels frontend", "Vérification des parcours d'authentification, publication et simulation."],
    ], [2400, 3300, 3660], caption="Tableau 8 : Matériels et logiciels utilisés")
    add_heading(doc, "3.1.2. LOGICIELS UTILISÉS ET JUSTIFICATION DES CHOIX", 3)
    add_body(doc, "Les logiciels retenus correspondent aux besoins réels du portail : construire une interface web par rôle, exposer une API sécurisée, conserver les données de facturation et traiter des blocs PDF parfois volumineux. Les choix sont présentés simplement afin de distinguer l'outil utilisé de la fonction qu'il remplit dans le projet.")
    add_body(doc, "Python et Django — Description : Python est le langage du backend et Django est le framework web qui structure les modèles, les utilisateurs, les migrations et les règles métier. Justification : Django a été retenu pour organiser la gestion des contrats, des lignes, des factures, des forfaits et des services dans une même application. Une solution PHP comme Symfony ou Laravel aurait été possible, mais aurait imposé un autre langage et un autre environnement.")
    add_body(doc, "Django REST Framework et JWT — Description : Django REST Framework permet de fournir les routes API consommées par React ; JWT protège les sessions par des jetons d'accès et de renouvellement. Justification : cette séparation permet au frontend et au backend de communiquer clairement tout en appliquant les permissions selon le rôle de l'utilisateur.")
    add_body(doc, "React et Vite — Description : React construit l'interface web et Vite assure le serveur de développement ainsi que la compilation. Justification : React permet de proposer des espaces différents pour l'administrateur, le chef, l'agent, le commercial, le payeur et l'employé. Axios, React Router, Recharts et Tailwind CSS complètent l'interface pour les appels API, la navigation, les graphiques et la mise en forme.")
    add_body(doc, "PostgreSQL et SQLite — Description : PostgreSQL est la base relationnelle cible ; SQLite reste disponible pour certains essais locaux. Justification : PostgreSQL convient aux relations entre utilisateurs, contrats, lignes et factures et garantit les contraintes d'unicité nécessaires au matching. SQLite facilite les premiers tests lorsque PostgreSQL n'est pas encore configuré, mais PostgreSQL est préféré pour un usage partagé.")
    add_body(doc, "Celery et Garnet — Description : Celery exécute les tâches longues et Garnet fournit un service compatible Redis pour transmettre ces tâches et conserver leurs résultats. Justification : le découpage des gros PDF peut continuer en arrière-plan avec les statuts EN_ATTENTE, EN_COURS, TERMINE ou ECHEC. L'agent peut donc quitter l'écran de publication sans interrompre le traitement.")
    add_body(doc, "PyPDF2, Pillow et pdf2image — Description : ces bibliothèques servent à lire, analyser et découper les PDF et à traiter les pages lorsque cela est nécessaire. Justification : elles permettent de produire un fichier individuel à partir d'un bloc global ou sommaire et de rechercher les identifiants utiles au rapprochement. L'OCR avec pytesseract reste une possibilité d'évolution et n'est pas considéré comme entièrement disponible dans la version actuelle.")
    add_body(doc, "pyotp, qrcode et cryptography — Description : ces bibliothèques permettent de mettre en place le code TOTP compatible avec Google Authenticator. Justification : elles sont utilisées pour rendre le 2FA optionnel et renforcer la protection des opérations sensibles, notamment le changement de mot de passe.")
    add_body(doc, "Kiro et le navigateur web — Description : Kiro a servi d'environnement principal de travail sur le code et le navigateur a permis de tester les interfaces. Justification : cet ensemble a facilité les essais de connexion, de gestion des contrats, d'import PDF, de publication, de consultation des factures et de simulation. Les tests backend Django et les commandes npm de compilation complètent ces vérifications.")
    add_heading(doc, "3.2. ARCHITECTURES MATÉRIELLE ET LOGICIELLE", 2)
    add_heading(doc, "3.2.1. Architecture logicielle", 3)
    add_body(doc, "L'architecture logicielle est organisée en couches afin de limiter les dépendances entre l'interface, l'API et les traitements documentaires. React/Vite constitue la couche de présentation ; Django REST Framework expose les ressources ; les services métier appliquent les règles ; PostgreSQL et le stockage média assurent la persistance ; Celery et Garnet prennent en charge les opérations longues. Chaque couche possède une responsabilité identifiable et peut être testée séparément.")
    add_heading(doc, "3.2.2. Architecture matérielle", 3)
    add_body(doc, "Dans l'environnement de développement, le navigateur, le serveur Django, PostgreSQL, Garnet et le worker Celery peuvent fonctionner sur le même ordinateur. Une architecture de recette ou de production les sépare de préférence : le frontend est servi par un serveur web, l'API dispose d'un processus applicatif, PostgreSQL est isolé sur un serveur de données et les workers sont supervisés. Cette séparation protège la base et permet d'augmenter le nombre de workers sans modifier l'interface.")
    add_body(doc, "L'architecture est de type client-serveur. Le navigateur exécute l'application React et communique avec l'API Django par HTTP/JSON. L'API applique l'authentification, les permissions, la validation des données et les règles métier. Django utilise PostgreSQL pour les objets métiers et le système de fichiers média pour les PDF. Les tâches lentes sont publiées dans Garnet puis consommées par un worker Celery.")
    add_table(doc, ["Couche", "Composants", "Responsabilité"], [
        ["Présentation", "React, routeur, services Axios", "Afficher les espaces par rôle, les formulaires, tableaux, notifications et états."],
        ["API", "Django REST Framework, serializers, views", "Exposer les données et contrôler l'accès."],
        ["Métier", "Services de simulation, contrats, PDF et notifications", "Appliquer les règles et isoler les traitements réutilisables."],
        ["Asynchrone", "Celery, Garnet", "Exécuter les imports PDF, suivre progression et résultats."],
        ["Persistance", "PostgreSQL, fichiers média", "Conserver utilisateurs, contrats, lignes, factures et documents."],
    ], [2200, 3600, 3560])
    add_body(doc, "Le flux de publication se déroule en plusieurs étapes : dépôt du fichier, création du traitement, validation du document, analyse page par page, découpage, rapprochement par identifiants, enregistrement du résultat et consultation de l'historique. Pour un PDF global, le compte entreprise est prioritaire ; pour un PDF sommaire, le numéro de facture puis le MSISDN sont utilisés afin d'éviter de rattacher une facture à la mauvaise ligne.")
    add_heading(doc, "3.3. SÉCURITÉ DE L'APPLICATION", 2)
    for item in [
        "Les utilisateurs sont authentifiés par des jetons JWT avec durée de vie limitée et renouvellement contrôlé.",
        "Les permissions sont calculées à partir du rôle et de l'état du compte ; un compte inactif ne peut plus accéder aux fonctions métier.",
        "Les mots de passe ne sont jamais stockés en clair. Le 2FA TOTP est optionnel et peut être activé depuis le profil.",
        "Les routes de factures vérifient le périmètre de l'utilisateur avant d'autoriser l'aperçu ou le téléchargement.",
        "Les événements liés aux contrats, aux statuts et aux publications sont historisés pour faciliter l'audit.",
        "En production, les fichiers média doivent être protégés par un stockage privé, HTTPS, des sauvegardes et des contrôles de taille.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "3.4. MISE EN PLACE DE LA BASE DE DONNÉES", 2)
    add_body(doc, "Le modèle relationnel est implémenté avec l'ORM Django. Les migrations créent les tables et leurs contraintes. Les relations principales sont : une entreprise possède plusieurs lignes et un payeur ; une ligne peut être rattachée à un employé ; une facture peut être globale ou sommaire ; un forfait possède des services et des tarifs ; un traitement PDF est créé par un agent et produit un résultat JSON détaillé.")
    add_table(doc, ["Domaine", "Entités principales", "Relations importantes"], [
        ["Comptes", "User, StatusHistory", "Un utilisateur porte un rôle et peut avoir un historique de statuts."],
        ["Contrats", "Company, ContractRequest, Commercial, AuditContrat", "Une demande commerciale peut produire un contrat après validation."],
        ["Lignes", "Line, LineService, Cycle", "Une ligne appartient à une entreprise et peut être liée à un employé."],
        ["Facturation", "Invoice, Publication, HistoriqueFacturation", "Une facture conserve période, statut, montant et PDF."],
        ["Catalogue", "Package, Service, TarifService", "Les tarifs alimentent les simulations."],
        ["Traitements", "TraitementPDF, Simulation, NotificationFacture", "Les traitements et simulations sont persistants et consultables."],
    ], [2200, 3500, 3660])
    add_heading(doc, "3.4.1. Organisation des migrations et contraintes", 3)
    add_body(doc, "Chaque évolution du modèle est enregistrée dans une migration Django versionnée. Cette pratique permet de reproduire la base sur une installation neuve et de déployer les changements sans modifier manuellement les tables. Les contraintes d'unicité protègent les comptes entreprise, les codes de forfait, les matricules commerciaux et les MSISDN. Les clés étrangères utilisent des comportements adaptés : la suppression d'une entreprise supprime ses lignes, tandis qu'un utilisateur supprimé peut être conservé dans l'historique par une relation SET_NULL lorsque la traçabilité l'exige.")
    add_heading(doc, "3.4.2. Endpoints principaux de l'API", 3)
    add_table(doc, ["Domaine", "Exemples d'URL", "Opérations"], [
        ["Authentification", "/api/auth/login/, /api/auth/token/refresh/", "Connexion, renouvellement JWT, profil et 2FA."],
        ["Contrats", "/api/billing/companies/, /api/billing/contract-requests/", "Lister, créer, modifier, soumettre, valider et rejeter."],
        ["Lignes", "/api/billing/lines/, /api/billing/lines/bulk-create/", "Créer, associer, importer et affecter des lignes."],
        ["Factures", "/api/billing/invoices/, /api/billing/invoices/{id}/pdf/", "Lister, filtrer, publier et télécharger un PDF."],
        ["Publication", "/api/billing/invoices/publier_masse/", "Lancer ou suivre un traitement PDF et son rapport."],
        ["Catalogue", "/api/billing/packages/, /api/billing/services/", "Gérer les forfaits, options et tarifs actifs."],
        ["Simulation", "/api/billing/simulations/", "Calculer, enregistrer et consulter l'historique."],
    ], [2100, 4200, 3060], caption="Tableau 13 : Principaux endpoints de l'API")
    add_heading(doc, "3.4.3. Algorithme de découpage et de rapprochement", 3)
    add_body(doc, "L'algorithme commence par ouvrir le lecteur PDF et par contrôler les limites de sécurité. Il parcourt ensuite les pages dans l'ordre. Une page qui contient un nouvel identifiant ouvre un bloc ; une page sans identifiant est rattachée au bloc courant et une page sans bloc produit un avertissement. À la fin du parcours, le dernier bloc est fermé puis tous les blocs sont envoyés à la fonction de découpage.")
    for item in [
        "Valider le PDF : lisibilité, absence de chiffrement bloquant, nombre de pages et taille maximale.",
        "Extraire le texte de la page et normaliser les espaces.",
        "Chercher les motifs MSISDN, compte entreprise, numéro de facture et dates.",
        "Ouvrir, poursuivre ou fermer un bloc selon l'identifiant détecté.",
        "Créer un fichier PDF individuel avec PdfWriter et un nom stable basé sur l'identifiant.",
        "Rechercher une facture existante par numéro exact, puis par MSISDN ou compte selon le type.",
        "Associer le fichier, la date et le numéro extraits ; enregistrer les erreurs sans interrompre les autres blocs.",
    ]:
        add_number(doc, item)
    add_body(doc, "Ce choix explique les notifications telles que « fichiers créés », « factures mises à jour », « déjà traitées » et « erreurs ». Une erreur de rapprochement ne signifie pas nécessairement que le découpage a échoué : le rapport distingue la production physique du PDF et son association à une facture métier.")
    add_heading(doc, "3.4.3.1. Extrait de logique de traitement", 3)
    add_body(doc, "Le code réel est réparti entre un service PDF et une tâche Celery. Le pseudo-code suivant résume l'ordre des opérations sans remplacer les fichiers versionnés du projet :")
    add_code_block(doc, "for page in reader.pages:\n    text = normalize(extract_text(page))\n    identifier = detect_invoice_or_msisdn(text)\n    if identifier and current_block:\n        close_block(current_block)\n    append_to_current_block(page, identifier)\n\nfor block in blocks:\n    pdf_path = write_pdf(block)\n    invoice = match_exact_then_scope(block.identifiers, kind)\n    save_result(pdf_path, invoice, report)")
    add_body(doc, "L'extrait montre deux principes retenus : ne jamais attribuer une page isolée sans contexte fiable et conserver séparément le fichier créé, la facture associée et l'erreur éventuelle. Cette distinction est indispensable pour interpréter une notification du type « 20 PDF créés, 11 factures mises à jour, 9 erreurs ».")
    add_heading(doc, "3.4.4. Règles de calcul de la simulation", 3)
    add_body(doc, "Le moteur de simulation sépare le montant récurrent du forfait et le montant variable de la consommation. Pour la voix, le nombre de tranches de 30 secondes est obtenu par arrondi supérieur de la durée en secondes divisée par 30 ; le prix est ensuite multiplié par 79/2. Pour les SMS, le nombre de messages est multiplié par 30 FCFA. Pour la data, le moteur choisit le palier correspondant à la consommation et applique le prix ou la surcharge configurée.")
    add_table(doc, ["Service", "Règle", "Exemple"], [
        ["Voix", "79 FCFA par minute, pas de 30 secondes ; 0 à 30 s = 39,5 FCFA.", "1 min 20 s = 3 tranches x 39,5 = 118,5 FCFA."],
        ["SMS", "30 FCFA par message envoyé.", "25 SMS = 750 FCFA."],
        ["Data", "Paliers selon le volume ; au-delà de 275 Go, surcharge de 5 FCFA par Mo excédentaire et forfait de 50 000 FCFA.", "280 Go : (5 000 x 5) + 50 000 = 75 000 FCFA."],
    ], [1800, 4500, 3060], caption="Tableau 14 : Règles de tarification utilisées par la simulation")
    add_heading(doc, "3.4.5. Tests techniques réalisés", 3)
    add_body(doc, "Les tests backend couvrent l'authentification, les permissions, les contrats, les affectations de lignes, le traitement PDF, le matching, les publications, les simulations et les notifications configurées. Les tests manuels frontend vérifient la navigation par rôle, les validations de formulaires, les tableaux paginés, les messages d'état et l'ouverture des fichiers PDF. Les scénarios de non-régression sont conservés dans les documents de tests du projet.")
    add_heading(doc, "3.5. CONCEPTION DES API ET ÉCHANGES", 2)
    add_body(doc, "Les échanges entre React et Django utilisent des objets JSON. Pour les fichiers, le navigateur envoie une requête multipart/form-data, car le PDF et les métadonnées doivent être transmis dans la même opération. Les réponses de l'API contiennent un code HTTP, un message lisible et, lorsque nécessaire, un détail par champ. Cette structure permet au frontend d'afficher une erreur près du formulaire plutôt qu'une alerte générique.")
    add_table(doc, ["Requête", "Réponse de succès", "Réponse d'erreur"], [
        ["POST /auth/login/", "Jetons access et refresh, profil, rôle.", "401 et message d'authentification invalide."],
        ["POST /contract-requests/", "Demande PENDING et identifiant.", "400 si compte, date ou catégorie est invalide."],
        ["POST /contract-requests/{id}/approve/", "Contrat créé/validé et trace d'audit.", "403 si rôle insuffisant ; 409 si déjà décidé."],
        ["POST /invoices/publier_masse/", "Traitement EN_ATTENTE et task_id.", "400 si fichier ou période invalide."],
        ["GET /traitements-pdf/{id}/", "Statut, progression, résultat et erreurs.", "404 si traitement inexistant ou non autorisé."],
        ["POST /simulations/", "Montant, détail et historique créé.", "400 si consommation négative ou service inactif."],
    ], [3200, 3000, 3460], caption="Tableau 20 : Contrats d'échange API représentatifs")
    add_heading(doc, "3.6. TRAITEMENT ASYNCHRONE AVEC CELERY", 2)
    add_body(doc, "Sans traitement asynchrone, le navigateur resterait bloqué pendant toute la lecture et l'écriture d'un gros PDF. L'import crée donc d'abord une instance TraitementPDF et retourne immédiatement un identifiant. Le worker Celery reçoit la tâche avec cet identifiant, relit le fichier depuis le stockage média, met à jour la progression et écrit le résultat final dans la base.")
    add_body(doc, "Garnet expose le protocole RESP compatible avec Redis. L'application sépare les bases logiques : une base pour le cache, une pour le broker Celery et une pour les résultats. Cette séparation limite les collisions de clés et rend le diagnostic plus simple. En cas d'indisponibilité du broker, l'API doit informer l'agent que le traitement n'a pas pu être planifié au lieu de simuler une publication terminée.")
    add_body(doc, "Le worker est lancé en environnement Windows avec le pool solo pour les essais. En production, un processus supervisé et une configuration adaptée devront être utilisés. Les limites de temps empêchent une tâche bloquée de monopoliser le worker ; les erreurs sont stockées dans TraitementPDF et remontées dans l'interface.")
    add_heading(doc, "3.7. MESURES DE SÉCURITÉ COMPLÉMENTAIRES", 2)
    add_body(doc, "La sécurité ne se limite pas à la connexion. Les serializers valident les formats et les relations, les permissions vérifient le rôle et le périmètre, et les vues évitent de renvoyer des données appartenant à une autre entreprise. Les fichiers PDF doivent être servis par une route contrôlée, et non par un répertoire public où un utilisateur pourrait deviner une URL.")
    add_body(doc, "Les clés SMTP, Vonage ou d'autres fournisseurs ne figurent jamais dans le code ou le mémoire. Elles sont chargées depuis l'environnement. Le 2FA TOTP est optionnel : lorsqu'il est activé, un changement de mot de passe exige le code généré par l'application d'authentification. Les écarts d'horloge doivent être limités et documentés, car un décalage trop grand affaiblit la sécurité.")
    add_heading(doc, "3.8. ORGANISATION DU CODE BACKEND", 2)
    add_body(doc, "Le projet Django est découpé en applications accounts et billing. L'application accounts concentre le modèle utilisateur personnalisé, les rôles, les permissions, l'authentification, le profil et le 2FA. L'application billing regroupe les modèles de contrats, de lignes, de catalogue, de factures, de simulations, de publications et de traitements PDF.")
    add_body(doc, "Les serializers transforment les modèles en représentations JSON et contrôlent les données reçues. Les views et viewsets gèrent les routes HTTP et délèguent les calculs ou les opérations documentaires aux services. Cette séparation permet de tester le service PDF sans passer par un navigateur et de réutiliser la même logique pour une commande d'administration ou une tâche Celery.")
    add_body(doc, "Les fichiers de migration décrivent l'évolution de la base. Les tests sont organisés par domaine : authentification, contrats, affectations, packages et services, traitement PDF, publications et simulations. Les scripts de création de données ne doivent être utilisés que dans l'environnement de démonstration.")
    add_table(doc, ["Module", "Responsabilité", "Exemples de composants"], [
        ["accounts", "Comptes et sécurité", "User, permissions, JWT, TOTP, historique de statut"],
        ["billing.models", "Domaine métier", "Company, Line, Invoice, Package, Service, Simulation"],
        ["billing.serializers", "Validation et représentation", "Contrats, lignes, factures, traitements"],
        ["billing.services", "Règles réutilisables", "Calcul, PDF, contrats, notifications"],
        ["billing.tasks", "Asynchrone", "traiter_import_pdf, notifications, contrôle broker"],
        ["billing.tests", "Non-régression", "Matching, publication, contrats, simulation"],
    ], [2100, 3500, 3660], caption="Tableau 24 : Organisation logique du backend")
    add_heading(doc, "3.9. ORGANISATION DU CODE FRONTEND", 2)
    add_body(doc, "L'application React regroupe les pages par espace fonctionnel : pages communes, pages agent, pages chef, pages administrateur, pages commercial et espaces payeur/employé. Les services frontend centralisent les appels Axios et les composants communs assurent la cohérence des tableaux, modales, badges d'état, paginations et notifications.")
    add_body(doc, "Le contexte d'authentification conserve le profil et les jetons, applique la redirection par rôle et déconnecte l'utilisateur lorsque le refresh token n'est plus valide. Les routes protégées empêchent l'affichage d'une page qui ne correspond pas à l'utilisateur connecté, mais les contrôles d'autorisation sont également réalisés par l'API.")
    add_body(doc, "La page de publication interroge périodiquement le traitement lorsqu'il est asynchrone. Elle affiche une progression et un résumé détaillé. Les erreurs de matching sont présentées en rouge, les fichiers déjà traités en orange et les succès en vert. La simulation affiche le résultat en haut de l'écran, puis met à jour son historique.")
    add_heading(doc, "3.10. FLUX D'AUTHENTIFICATION JWT", 2)
    for item in [
        "Le navigateur envoie l'identifiant et le mot de passe à la route de connexion.",
        "Django recherche l'utilisateur et vérifie son statut ainsi que son mot de passe haché.",
        "Si le 2FA est actif, l'API vérifie le code TOTP dans la fenêtre de temps configurée.",
        "L'API signe un access token court et un refresh token plus long.",
        "Axios ajoute le token dans l'en-tête Authorization des requêtes protégées.",
        "À l'expiration de l'access token, le frontend demande un renouvellement ; en cas d'échec, il supprime la session.",
        "Chaque vue protégée recalcule le rôle et le périmètre avant de renvoyer les données.",
    ]:
        add_number(doc, item)
    add_heading(doc, "3.11. GESTION DES ERREURS ET DE LA TRAÇABILITÉ", 2)
    add_body(doc, "Une erreur technique est différente d'une anomalie métier. Une exception de lecture PDF doit être journalisée comme erreur technique, alors qu'une facture sans correspondance est une anomalie métier qui peut être corrigée par les données de référence. Le rapport conserve ces deux catégories afin que l'agent ne perde pas de temps à chercher une panne serveur lorsqu'il manque simplement un MSISDN.")
    add_body(doc, "Les actions sensibles sont également consignées : création ou modification d'un contrat, validation ou rejet d'une demande, changement de statut, association d'une ligne, ajout d'un service, publication et rattachement d'un PDF. L'audit doit conserver l'utilisateur, la date, le type d'action, une description et les valeurs pertinentes avant/après.")
    add_heading(doc, "3.12. CHOIX D'IMPLÉMENTATION ET COMPROMIS", 2)
    add_body(doc, "Django a été préféré à un développement serveur entièrement manuel car son ORM permet de faire évoluer le modèle et d'appliquer les migrations, tandis que Django REST Framework fournit un cadre de validation et d'authentification. React a été retenu pour séparer la présentation des données métier et pour offrir des interfaces différentes selon le rôle sans dupliquer le backend.")
    add_body(doc, "PostgreSQL est la base cible car les relations et les contraintes d'unicité sont importantes dans le rapprochement des lignes et des contrats. SQLite reste utile pour certains essais isolés, mais ne doit pas être considérée comme la base de production lorsque plusieurs utilisateurs et workers accèdent simultanément aux données.")
    add_body(doc, "Le traitement PDF utilise l'extraction de texte plutôt qu'une reconnaissance d'image. Ce choix simplifie le déploiement et fournit de bons résultats lorsque les fichiers produits par l'opérateur contiennent une couche texte. En contrepartie, un PDF scanné ou un changement important de mise en page peut nécessiter un module OCR dans une version ultérieure.")
    add_body(doc, "Le découpage est réalisé dans un répertoire de travail puis le fichier est associé à la facture seulement après vérification. Cette séquence réduit le risque d'enregistrer une facture partiellement écrite. Les noms de fichiers sont dérivés d'identifiants issus du document, avec un suffixe unique pour éviter les collisions.")
    add_body(doc, "Les traitements asynchrones augmentent la fiabilité perçue, mais ajoutent un composant d'exploitation. Le broker, le worker et le backend doivent être démarrés ensemble, leurs mots de passe doivent être cohérents et leurs journaux doivent être surveillés. La version de stage documente volontairement cette contrainte afin qu'elle ne soit pas masquée lors de la livraison.")
    add_heading(doc, "3.13. PERFORMANCE ET DIMENSIONNEMENT", 2)
    add_body(doc, "Le temps de traitement dépend du nombre de pages, de la quantité de texte à extraire, du nombre de blocs et de la vitesse du stockage. La pagination évite de charger de grandes listes dans le navigateur. Les filtres par période et par statut réduisent le volume des requêtes. Les relations utilisées pour afficher le nom de l'entreprise, le payeur et la ligne doivent être chargées de manière optimisée pour éviter une requête par cellule du tableau.")
    add_body(doc, "Pour une montée en charge, le stockage des PDF devra être externalisé ou organisé par période, les index des champs de recherche devront être vérifiés et plusieurs workers pourront être utilisés. Une file dédiée aux imports peut empêcher une tâche de notification ou de contrôle de bloquer une publication importante. Ces optimisations ne sont pas nécessaires pour le prototype de stage mais sont prévues dans l'architecture.")

    # PART 4
    add_part_heading(doc, "PARTIE 4 : EXPLOITATION (GUIDE D'EXPLOITATION)")
    add_body(doc, "Cette partie transforme les choix techniques en procédures d'exploitation. Elle indique les prérequis, l'ordre de démarrage, le suivi d'une tâche Celery, les actions de maintenance et les contrôles à effectuer avant une livraison. L'objectif est qu'un autre intervenant puisse reproduire l'installation et diagnostiquer une publication sans dépendre de la seule mémoire du développeur.")
    add_heading(doc, "4.1. CONFIGURATION LOGICIELLE ET MATÉRIELLE", 2)
    add_body(doc, "Pour un environnement de développement, il faut disposer d'un ordinateur récent sous Windows, Linux ou macOS, d'au moins 8 Go de mémoire vive, de Python 3.11 ou version compatible avec le projet, de Node.js et npm, de PostgreSQL 16, ainsi que d'un serveur Garnet ou Redis compatible lorsque les tâches Celery sont utilisées. Un navigateur moderne est nécessaire pour l'interface React.")
    add_table(doc, ["Composant", "Minimum conseillé", "Utilisation"], [
        ["Mémoire", "8 Go RAM", "Backend, frontend, base et worker en parallèle."],
        ["Stockage", "10 Go libres", "Dépendances, base, journaux et PDF de test."],
        ["Python", "3.11+", "Django et services PDF."],
        ["Node.js", "18+", "Vite et compilation React."],
        ["PostgreSQL", "16", "Base relationnelle de développement/production."],
        ["Garnet/Redis", "Port 6379", "Cache, broker Celery et résultats."],
    ], [2300, 2600, 4460])
    add_heading(doc, "4.2. DÉPLOIEMENT ET SUIVI", 2)
    add_body(doc, "Les étapes suivantes décrivent le démarrage de l'environnement local. Les secrets doivent être fournis par variables d'environnement et ne doivent pas être copiés dans le dépôt.")
    for step in [
        "Créer et activer l'environnement virtuel Python dans le dossier Back.",
        "Installer les dépendances backend à partir du fichier de dépendances du projet.",
        "Renseigner POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST et POSTGRES_PORT dans .env.",
        "Appliquer les migrations avec python manage.py migrate et créer un compte administrateur si nécessaire.",
        "Démarrer le serveur Django avec python manage.py runserver.",
        "Démarrer le frontend avec npm install puis npm run dev dans le dossier Front.",
        "Démarrer Garnet/Redis, puis le worker avec python -m celery -A moov_backend worker -l INFO -P solo.",
        "Vérifier python manage.py check, les journaux et l'accès à l'interface avant d'importer des PDF réels.",
    ]:
        add_number(doc, step)
    add_body(doc, "Le suivi d'un import s'effectue dans l'interface de publication et dans la table TraitementPDF. Les statuts EN_ATTENTE, EN_COURS, TERMINE et ECHEC permettent de distinguer une file d'attente, une exécution active, un résultat terminé et une erreur. L'agent peut fermer la page ; le worker continue le traitement et le résultat reste disponible.")
    add_heading(doc, "4.3. MAINTENANCE : ACTIONS EN CAS D'ERREUR", 2)
    add_table(doc, ["Symptôme", "Vérifications", "Action recommandée"], [
        ["Le backend ne démarre pas", "Variables .env, migrations, port utilisé.", "Corriger la configuration puis relancer manage.py check."],
        ["Le worker ne se connecte pas", "Garnet/Redis, port 6379, URL et mot de passe.", "Tester la connexion puis relancer le worker."],
        ["PDF invalide", "Taille, chiffrement, nombre de pages, texte extractible.", "Fournir un PDF lisible et consulter les erreurs par page."],
        ["Facture non associée", "Numéro de facture, compte, MSISDN et période en base.", "Corriger les données de référence puis réimporter le bloc."],
        ["Facture déjà traitée", "Statut VALIDEE, PUBLIEE ou PAYEE.", "Utiliser une nouvelle période ou réinitialiser les données de test selon la procédure autorisée."],
        ["Aperçu indisponible", "Fichier PDF associé et accès média.", "Vérifier le champ fichier, le stockage et les permissions HTTP."],
    ], [2600, 3400, 3360], caption="Tableau 9 : Matrice de maintenance et résolution d'incidents")
    add_heading(doc, "4.3.1. Sauvegarde et restauration", 3)
    add_body(doc, "La base PostgreSQL doit être sauvegardée régulièrement avec pg_dump, en conservant plusieurs générations sur un support séparé. Les fichiers PDF du répertoire média doivent être sauvegardés en même temps que la base, car une ligne de facture peut référencer un fichier qui n'est pas contenu dans PostgreSQL. Une restauration complète doit donc rétablir la base, les médias, les variables d'environnement et les droits d'accès au stockage.")
    add_body(doc, "Avant toute opération destructive sur les données de test, l'opérateur doit vérifier l'environnement et réaliser une copie. La suppression d'une facture déjà traitée ne doit jamais être effectuée sur la base de production sans procédure validée. Pour les tests locaux, un script de réinitialisation dédié peut supprimer uniquement les factures, traitements et fichiers de test associés à une période donnée.")
    add_heading(doc, "4.3.2. Journalisation et supervision", 3)
    add_body(doc, "Les journaux applicatifs consignent les erreurs Django, les événements de sécurité et les anomalies de traitement. En production, la taille des fichiers doit être limitée par rotation et les messages ne doivent pas contenir de mot de passe, de jeton JWT ou de clé API. Une supervision minimale doit vérifier la disponibilité du backend, la connexion PostgreSQL, le broker Garnet et l'état du worker Celery.")
    add_table(doc, ["Contrôle", "Fréquence", "Seuil ou résultat attendu"], [
        ["Disponibilité API", "Continue", "Réponse HTTP saine sur la route de contrôle."],
        ["Connexion PostgreSQL", "À chaque démarrage", "Migrations appliquées et connexion acceptée."],
        ["Broker Garnet", "Continue", "Le worker reste connecté et reçoit une tâche de test."],
        ["Traitements ECHEC", "Quotidienne", "Les erreurs sont analysées et corrigées avant la période suivante."],
        ["Espace média", "Quotidienne", "Seuil d'alerte défini avant saturation."],
        ["Sauvegardes", "Quotidienne", "Dernière sauvegarde vérifiable et restauration testée périodiquement."],
    ], [2500, 2200, 4660], caption="Tableau 15 : Contrôles d'exploitation recommandés")
    add_heading(doc, "4.3.3. Checklist avant mise en production", 3)
    for item in [
        "Remplacer la SECRET_KEY de développement et désactiver DEBUG.",
        "Configurer ALLOWED_HOSTS, HTTPS, les cookies sécurisés et les règles CORS adaptées.",
        "Créer un compte administrateur nominatif et supprimer les comptes de démonstration inutiles.",
        "Configurer PostgreSQL, les sauvegardes, les médias privés et la rotation des journaux.",
        "Configurer Garnet/Redis et démarrer un worker Celery supervisé.",
        "Tester les cinq rôles : administrateur, chef, agent, commercial et client.",
        "Importer un PDF d'essai, vérifier le rapport, puis contrôler l'accès au document depuis le compte concerné.",
        "Actualiser la documentation et conserver la liste des limites connues.",
    ]:
        add_bullet(doc, item)
    add_table(doc, ["Contrôle de livraison", "Commande ou vérification", "Résultat attendu"], [
        ["Django", "python manage.py check", "Aucune erreur de configuration"],
        ["Sécurité", "python manage.py check --deploy", "Avertissements examinés et documentés"],
        ["Base", "python manage.py makemigrations --check --dry-run", "Aucune migration oubliée"],
        ["Tests", "python manage.py test", "Tests critiques verts"],
        ["Frontend", "npm run build", "Compilation Vite terminée"],
        ["Asynchrone", "Worker Celery prêt et tâche de contrôle exécutée", "Broker joignable et statut persistant"],
    ], [2300, 4200, 3060], caption="Tableau 30 : Vérifications de déploiement et de mise en service")
    add_heading(doc, "4.4. Procédures de diagnostic", 2)
    add_heading(doc, "4.4.1. Diagnostic d'une publication lente", 3)
    add_body(doc, "L'opérateur vérifie d'abord si une ligne de traitement existe en base. Si le statut reste EN_ATTENTE, le worker n'a probablement pas reçu la tâche ou le broker est indisponible. Si le statut reste EN_COURS, il faut consulter les journaux et vérifier la taille du PDF, la mémoire disponible et la limite de temps. Le navigateur ne doit pas être rechargé en boucle, car la tâche peut continuer indépendamment de la page.")
    add_heading(doc, "4.4.2. Diagnostic d'un rapport avec erreurs", 3)
    add_body(doc, "Le premier contrôle porte sur le type de fichier : un bloc global doit être déclaré GLO et un bloc sommaire SOM. Le deuxième contrôle porte sur les périodes en base. Le troisième porte sur les identifiants détectés. Un PDF peut être visuellement correct mais ne pas contenir de texte extractible ; dans ce cas le projet signale l'absence d'identifiant et l'OCR doit être envisagé comme évolution.")
    add_heading(doc, "4.4.3. Diagnostic d'un aperçu PDF manquant", 3)
    add_body(doc, "L'agent vérifie que la facture possède un fichier dans le champ fichier_pdf, que le fichier existe réellement sous MEDIA_ROOT et que la route PDF renvoie le bon type MIME. L'utilisateur vérifie ensuite qu'il possède le droit de consulter la facture. Une différence entre le nom affiché dans le tableau et le nom physique du fichier doit être corrigée au niveau du serializer ou du service de publication, et non par une valeur aléatoire dans le frontend.")
    add_heading(doc, "4.5. Gestion des versions", 2)
    add_body(doc, "Chaque livraison doit indiquer la version du backend, du frontend, des migrations et du document. Une modification de règle métier doit être accompagnée d'un test et d'une mise à jour de la documentation. Les migrations ne doivent pas être supprimées après avoir été appliquées sur une base partagée. Les données de démonstration doivent être séparées des données réelles et identifiées comme telles.")
    add_heading(doc, "4.6. Procédure d'installation locale détaillée", 2)
    add_body(doc, "L'installation locale se déroule dans l'ordre suivant. Il est recommandé d'ouvrir trois terminaux : un pour PostgreSQL et les commandes Django, un pour le serveur frontend et un pour le worker Celery. Les chemins sont donnés à titre indicatif et doivent être adaptés à l'installation de l'opérateur.")
    add_heading(doc, "4.6.1. Préparation du backend", 3)
    for item in [
        "Ouvrir un terminal dans le dossier Back.",
        "Créer l'environnement virtuel avec python -m venv venv.",
        "Activer l'environnement avec venv\\Scripts\\Activate.ps1 sous PowerShell.",
        "Installer les dépendances avec pip install -r requirements.txt.",
        "Vérifier les variables POSTGRES et les paramètres de connexion dans .env.",
        "Exécuter python manage.py check puis python manage.py migrate.",
        "Créer un superutilisateur avec python manage.py createsuperuser si nécessaire.",
        "Lancer python manage.py runserver 8000 et vérifier l'URL API.",
    ]:
        add_number(doc, item)
    add_heading(doc, "4.6.2. Préparation du frontend", 3)
    for item in [
        "Ouvrir un second terminal dans le dossier Front.",
        "Installer les modules avec npm install.",
        "Vérifier l'URL de l'API dans la configuration Vite ou les variables de développement.",
        "Lancer npm run dev et ouvrir l'adresse affichée par Vite.",
        "Tester d'abord la connexion, puis la navigation vers le tableau de bord du rôle.",
        "Lancer npm run build avant une livraison afin de détecter les imports ou erreurs de compilation.",
    ]:
        add_number(doc, item)
    add_heading(doc, "4.6.3. Préparation de Garnet et Celery", 3)
    add_body(doc, "Garnet doit écouter sur le port indiqué dans REDIS_URL. Le mot de passe ne doit pas être placé directement dans une commande visible ou dans le mémoire. Après vérification de la connexion, le worker est lancé avec python -m celery -A moov_backend worker -l INFO -P solo sous Windows. La présence de la tâche billing.traiter_import_pdf dans la liste affichée par Celery confirme que l'application l'a bien découverte.")
    add_body(doc, "Un contrôle de bout en bout peut être réalisé en lançant la tâche billing.verifier_garnet. Le résultat attendu indique que le broker répond, que le cache peut écrire et relire une clé, et que le worker est prêt. Cette vérification doit être effectuée avant un test de publication afin de distinguer un problème d'infrastructure d'un problème de PDF.")
    add_heading(doc, "4.7. Procédure de livraison", 2)
    for item in [
        "Geler la version du code et sauvegarder la base de données.",
        "Appliquer les migrations sur une copie de recette.",
        "Exécuter python manage.py check --deploy et les tests Django.",
        "Compiler le frontend et vérifier les routes principales dans un navigateur propre.",
        "Charger un PDF sommaire et un PDF global de test ; vérifier les rapports et l'accès client.",
        "Vérifier la consultation des contrats, le rejet avec motif et la simulation.",
        "Documenter les anomalies restantes et obtenir la validation du responsable.",
        "Déployer avec des secrets injectés par l'environnement et non dans Git.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "4.8. Procédure de reprise après incident", 2)
    add_body(doc, "Lorsqu'un incident est détecté, l'opérateur note l'heure, le rôle concerné, la période et l'action en cours. Il évite de relancer plusieurs fois la même publication tant que le statut de TraitementPDF n'est pas connu. Il exporte ou copie le rapport, consulte les journaux et vérifie si des factures ont déjà été associées avant toute correction.")
    add_body(doc, "Si l'incident concerne le broker, le service Garnet est redémarré puis la connexion est testée avec une tâche de contrôle. Si l'incident concerne la base, l'accès est suspendu le temps de vérifier les migrations et la dernière sauvegarde. Si l'incident concerne un PDF, le fichier original est conservé et l'opérateur travaille sur une copie afin de garder une preuve de l'entrée reçue.")
    add_body(doc, "Une reprise réussie doit être documentée : cause, données corrigées, traitement relancé, nombre de factures associées et éventuelles actions manuelles. Cette fiche peut être ajoutée à l'historique de publication ou au journal de maintenance. Elle contribue à réduire le temps de résolution lors de la période suivante.")
    add_heading(doc, "4.9. Sécurité opérationnelle", 2)
    add_body(doc, "Les comptes de test ne doivent pas être réutilisés par plusieurs agents en production. Les droits doivent suivre le principe du moindre privilège : un commercial soumet une demande, mais ne valide pas son propre contrat ; un employé consulte sa ligne, mais ne voit pas les données de la flotte ; un agent ne modifie que le périmètre qui lui est confié.")
    add_body(doc, "Les PDF peuvent contenir des informations financières et personnelles. Leur téléchargement doit être journalisé si les exigences de l'organisation le prévoient. Les sauvegardes doivent être chiffrées, les liens temporaires préférés aux URL permanentes et les fichiers supprimés conformément à la politique de conservation validée par Moov Africa Togo.")

    # PART 5
    add_part_heading(doc, "PARTIE 5 : GUIDE D'UTILISATION")
    add_body(doc, "Cette partie s'adresse aux utilisateurs qui exploitent le portail au quotidien. Elle décrit la navigation, les écrans et les états visibles, puis détaille les procédures propres à chaque rôle. Les explications s'appuient sur les interfaces développées et sur les règles métier présentées dans les parties précédentes.")
    add_heading(doc, "5.1. DESCRIPTION TEXTUELLE DU LOGICIEL", 2)
    add_body(doc, "Moov e-Factures est une application web à espaces différenciés. Après connexion, l'utilisateur est orienté vers un tableau de bord correspondant à son rôle. Les rôles internes disposent d'outils d'administration, de gestion des contrats et de publication. Les rôles clients disposent de leurs lignes, de leurs factures et de la simulation.")
    add_heading(doc, "5.1.1. Modules et parcours par rôle", 3)
    add_body(doc, "Le tableau suivant fournit une vue rapide du guide. Il peut être utilisé comme index de démonstration : l'utilisateur identifie son rôle, ouvre le module indiqué et vérifie le résultat attendu avant de passer au parcours suivant.")
    add_table(doc, ["Rôle", "Parcours conseillé", "Écran de contrôle", "Résultat attendu"], [
        ["Administrateur", "Comptes, contrats, forfaits, services et paramètres", "Tableaux paginés et fiches de détail", "Référentiel cohérent et droits appliqués"],
        ["Chef de facturation", "Demandes, validation/rejet, commerciaux et supervision", "Détail de demande et historique", "Décision tracée avec motif si rejet"],
        ["Agent de facturation", "Lignes, import PDF, publication et erreurs", "Rapport et historique de traitement", "Associations réelles et anomalies identifiées"],
        ["Commercial", "Nouvelle demande puis suivi", "Liste des demandes", "Statut PENDING, APPROVED ou REJECTED visible"],
        ["Payeur", "Contrat, lignes, facture globale, sommaires et simulation", "Mes factures et historique", "Accès limité à son entreprise"],
        ["Employé", "Ma ligne, facture sommaire et simulation", "Mes factures", "Accès limité à sa ligne"],
    ], [1800, 3500, 2300, 1960], caption="Tableau 31 : Modules et parcours du guide utilisateur")
    add_heading(doc, "5.2. PLAN DE NAVIGATION", 2)
    add_table(doc, ["Rôle", "Rubriques principales"], [
        ["Super administrateur", "Tableau de bord, comptes, contrats, lignes, forfaits, services, paramètres et historiques."],
        ["Chef de facturation", "Tableau de bord, demandes de contrats, contrats, commerciaux, utilisateurs, publications et tarifs."],
        ["Agent de facturation", "Tableau de bord, contrats autorisés, lignes, forfaits/services, import PDF, factures à publier et historique."],
        ["Commercial", "Tableau de bord, nouvelles demandes de contrat et suivi des demandes soumises."],
        ["Payeur", "Tableau de bord, mes lignes, mes factures globales/sommaires, simulation, historique et profil."],
        ["Employé", "Tableau de bord, ma ligne, mes factures sommaires, simulation, historique et profil."],
    ], [2600, 6760])
    add_heading(doc, "5.3. PRÉSENTATION DES DIFFÉRENTES INTERFACES", 2)
    add_heading(doc, "a) Interfaces internes", 3)
    add_body(doc, "Le tableau de bord interne affiche les indicateurs liés au rôle. La gestion des contrats présente le code, la catégorie, le commercial, les dates, les services par défaut et le statut de résiliation. La publication permet de sélectionner un PDF, de choisir globale ou sommaire, de suivre la progression et de consulter un rapport détaillé. Les tableaux utilisent une pagination cohérente afin de rester exploitables avec un grand nombre de lignes.")
    add_heading(doc, "b) Interfaces payeur et employé", 3)
    add_body(doc, "Le payeur accède aux informations de son contrat et de sa flotte. Il peut ouvrir une facture globale ou sélectionner une facture sommaire d'une ligne. L'employé dispose d'un périmètre plus restreint : les contrôles backend et frontend empêchent l'accès aux factures d'une autre ligne. Lorsque le fichier est disponible, le téléchargement respecte le nom réel du PDF généré.")
    add_heading(doc, "c) Simulation", 3)
    add_body(doc, "La page de simulation présente les services et forfaits actifs. Elle affiche le résultat en haut de l'écran sous forme de notification visible, puis détaille le calcul. Chaque simulation validée est persistée avec la date, le montant estimé, les consommations et les services sélectionnés.")
    for image_path, caption in [
        (ILLUSTRATION_DASHBOARD, "Figure 2 : Illustration de l'espace de tableau de bord."),
        (ILLUSTRATION_PAYEUR, "Figure 3 : Illustration de l'espace payeur et de la consultation des factures."),
        (ILLUSTRATION_SIMULATION, "Figure 4 : Illustration de l'espace de simulation."),
    ]:
        if image_path.exists():
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            p.add_run().add_picture(str(image_path), width=Inches(4.9))
            add_caption(doc, caption)
    add_heading(doc, "5.4. PRÉSENTATION DES ÉTATS", 2)
    add_table(doc, ["Objet", "États", "Signification"], [
        ["Facture", "BROUILLON, EN_COURS, VALIDEE, PUBLIEE, PAYEE, ANNULEE", "Cycle de vie d'une facture depuis sa préparation jusqu'à son paiement ou son annulation."],
        ["Traitement PDF", "EN_ATTENTE, EN_COURS, TERMINE, ECHEC", "Suivi persistant d'un import et de son traitement Celery."],
        ["Demande de contrat", "PENDING, APPROVED, REJECTED", "Demande commerciale en attente, validée ou rejetée avec motif."],
        ["Contrat", "EN_ATTENTE, ACTIF, SUSPENDU, CLOS", "État de facturation du contrat, indépendant de la résiliation métier."],
    ], [2500, 3200, 3660], caption="Tableau 7 : Description des états métier")
    add_heading(doc, "5.5. Procédures détaillées par profil", 2)
    add_heading(doc, "5.5.1. Super administrateur", 3)
    for item in [
        "Se connecter avec un compte administrateur et vérifier le tableau de bord global.",
        "Ouvrir la gestion des comptes pour créer un utilisateur, choisir son rôle et définir son statut.",
        "Créer ou modifier un forfait en renseignant son code, son type, son prix et ses quotas.",
        "Créer un service optionnel et l'associer au forfait approprié ; vérifier qu'il apparaît dans la simulation.",
        "Consulter les contrats et les lignes pour corriger une donnée de référence avant une publication.",
        "Consulter les journaux et les historiques en cas d'anomalie.",
    ]:
        add_number(doc, item)
    add_heading(doc, "5.5.2. Chef de facturation", 3)
    for item in [
        "Ouvrir la page des demandes et filtrer les demandes PENDING.",
        "Consulter le détail d'une demande commerciale, notamment le compte, la catégorie, le commercial, les dates, les services et le payeur proposé.",
        "Valider la demande si les informations sont correctes ou la rejeter en saisissant un motif explicite.",
        "Gérer les commerciaux et affecter le commercial qui a signé le contrat.",
        "Superviser les publications, les erreurs et les traitements encore EN_COURS.",
        "Vérifier les tarifs avant le début d'une nouvelle période de simulation.",
    ]:
        add_number(doc, item)
    add_heading(doc, "5.5.3. Agent de facturation", 3)
    add_body(doc, "L'agent prépare d'abord la base : contrats actifs, périodes, lignes, MSISDN et factures candidates. Il ouvre ensuite la page de publication, sélectionne GLO pour un bloc global ou SOM pour un bloc sommaire, puis choisit le fichier. Après lancement, le traitement peut continuer même si l'agent quitte la page. Le tableau d'historique permet de revenir consulter le résultat et d'identifier les erreurs à corriger.")
    add_body(doc, "Avant une nouvelle tentative, l'agent doit lire le résumé : un fichier créé n'est pas obligatoirement une facture associée. Les éléments « déjà traités » ne doivent pas être supprimés au hasard ; il faut vérifier la période et le statut. Pour une reprise de test, l'opérateur utilise une sauvegarde ou le script prévu pour les données de démonstration.")
    add_heading(doc, "5.5.4. Commercial", 3)
    add_body(doc, "Le commercial crée une demande à partir d'un formulaire distinct de la gestion des contrats validés. Il renseigne les éléments du client, le mode de règlement, les adresses, la catégorie, les services et la date d'effet. La demande est ensuite suivie dans la page des demandes. Si elle est rejetée, le motif est affiché afin que le commercial puisse corriger et soumettre une nouvelle version.")
    add_heading(doc, "5.5.5. Payeur", 3)
    for item in [
        "Se connecter avec l'identifiant attribué au contrat et vérifier les informations de l'entreprise.",
        "Ouvrir « Mes lignes » pour consulter les MSISDN, utilisateurs, forfaits et services actifs.",
        "Ouvrir « Mes factures » et filtrer par période ou par type globale/sommaire.",
        "Consulter le PDF global ou une facture sommaire précise, puis télécharger le document si le fichier est attaché.",
        "Lancer une simulation pour estimer la consommation de la flotte et consulter l'historique.",
        "Modifier les informations autorisées du profil et activer le 2FA si nécessaire.",
    ]:
        add_number(doc, item)
    add_heading(doc, "5.5.6. Employé", 3)
    for item in [
        "Se connecter avec les informations du compte lié au MSISDN.",
        "Consulter la page de la ligne pour vérifier le forfait et les services attribués.",
        "Ouvrir uniquement les factures sommaires associées à sa ligne.",
        "Réaliser une simulation individuelle en saisissant minutes, SMS et data.",
        "Consulter l'historique et modifier le profil ou le mot de passe selon les droits.",
    ]:
        add_number(doc, item)
    add_heading(doc, "5.6. Lecture d'un rapport de publication", 2)
    add_body(doc, "Le rapport affiche le nombre total de pages analysées, le nombre de blocs détectés et de fichiers PDF générés. La partie rapprochement indique le nombre de factures associées, non associées et déjà traitées. Une couleur verte signale une réussite, une couleur orange un traitement déjà réalisé ou un avertissement, et une couleur rouge une erreur nécessitant une intervention. Cette distinction évite de confondre une publication partiellement réussie avec un échec complet.")
    add_heading(doc, "5.7. Limites connues présentées à l'utilisateur", 2)
    add_body(doc, "Le système ne remplace pas le moteur de facturation de l'opérateur. Il publie des documents préparés et s'appuie sur les identifiants textuels présents dans les PDF. Un document image nécessitant de l'OCR peut ne pas être reconnu. Les notifications SMS restent désactivées dans la version retenue ; les notifications e-mail dépendent de la configuration SMTP. Enfin, le stockage local des médias convient aux essais mais doit être remplacé ou sécurisé pour une exploitation réelle.")
    add_heading(doc, "5.8. Messages et états affichés", 2)
    add_table(doc, ["Situation", "Message attendu", "Couleur / action"], [
        ["Simulation réussie", "Simulation calculée et enregistrée dans l'historique.", "Notification visible en haut, couleur verte."],
        ["Facture déjà traitée", "Ce document a déjà été associé à une facture.", "Avertissement orange ; ne pas republier sans décision."],
        ["Erreur de matching", "Aucune facture correspondante pour les identifiants détectés.", "Erreur rouge ; corriger la base ou le PDF."],
        ["PDF manquant", "Le fichier de cette facture n'est pas attaché.", "Avertissement orange dans le tableau client."],
        ["Traitement en cours", "Le traitement continue en arrière-plan.", "Progression et bouton d'actualisation."],
        ["Accès refusé", "Vous n'êtes pas autorisé à consulter cette ressource.", "Erreur rouge, sans exposer les données."],
    ], [2400, 4600, 2660], caption="Tableau 21 : Messages et états visibles dans l'interface")
    add_heading(doc, "5.9. Questions fréquentes", 2)
    add_body(doc, "Pourquoi un traitement indique-t-il des fichiers créés mais zéro facture mise à jour ? Le découpage physique a réussi, mais les identifiants du PDF ne correspondent à aucune facture candidate ou la période sélectionnée ne correspond pas. Il faut consulter le détail des erreurs et vérifier le numéro, le compte, le MSISDN et les dates.")
    add_body(doc, "Pourquoi une facture apparaît-elle comme déjà traitée ? Le moteur recherche aussi les factures dont le statut est VALIDEE, PUBLIEE ou PAYEE. Cette vérification évite d'écraser un document déjà disponible. Pour un test, il faut travailler sur une période dédiée ou restaurer une sauvegarde de test.")
    add_body(doc, "Pourquoi le payeur ne voit-il pas un PDF sommaire ? Le payeur ne reçoit que les lignes liées à son contrat. Si le PDF est associé à une facture sans ligne ou à une autre entreprise, il peut être visible dans l'espace agent mais pas dans l'espace client. Le rapprochement doit donc associer la facture sommaire au bon MSISDN.")
    add_body(doc, "Pourquoi le montant affiché doit-il venir du PDF ? Une valeur générée par l'interface ne garantit pas la cohérence avec le document publié. Le montant, le numéro et la date d'émission doivent être extraits ou enregistrés au moment du matching, puis réutilisés par tous les espaces utilisateurs.")
    add_heading(doc, "5.10. Parcours complet d'une période de facturation", 2)
    add_body(doc, "Au début d'une période, l'agent vérifie les contrats actifs, les dates d'effet et de fin, les lignes et les services. Il contrôle également que le payeur et les employés possèdent les informations nécessaires à la consultation. Cette préparation réduit les erreurs de matching au moment de la réception du bloc PDF.")
    add_body(doc, "Lorsque les documents sont disponibles, l'agent importe séparément les blocs globaux et sommaires. Il renseigne la période exacte, choisit le type correspondant et lance le traitement. Pendant l'exécution, il peut consulter d'autres écrans ; la tâche reste exécutée par Celery. À la fin, l'agent lit les compteurs, ouvre la liste des erreurs et corrige les éléments non associés.")
    add_body(doc, "Après validation des résultats, les factures sont publiées. Le payeur se connecte pour vérifier le document global et les sommaires de sa flotte. Les employés vérifient leurs propres documents. Les écarts de montant, de numéro ou de date doivent être signalés avant l'envoi de toute notification. L'historique permet de conserver la date, le responsable, le statut et le fichier réel.")
    add_heading(doc, "5.11. Gestion des contrats et des résiliations", 2)
    add_body(doc, "La fiche contrat présente le code, le compte, la raison sociale, la catégorie, le commercial, le mode de règlement, les adresses, la date d'effet, la date de fin, l'exonération, le type de revenu, les observations et le statut de facturation. Une résiliation est représentée par un booléen, une date prévue ou effective, un motif et une observation. Le statut d'un contrat résilié doit être visuellement différent d'un contrat actif.")
    add_body(doc, "La page de détail permet de consulter les lignes et les services hérités. L'ajout d'une ligne ouvre un formulaire séparé pour éviter de mélanger les informations du contrat et celles de la ligne. Les actions importantes sont écrites dans AuditContrat afin que l'utilisateur puisse reconstituer l'évolution du contrat.")
    add_heading(doc, "5.12. Gestion des notifications", 2)
    add_body(doc, "La publication peut préparer une notification de disponibilité. Dans la version documentée, l'e-mail est le canal prévu lorsque SMTP est configuré ; le SMS est désactivé tant que les paramètres du fournisseur ne sont pas validés. La notification doit être déclenchée après l'association réussie du PDF, et non après la simple création d'un fichier sans correspondance.")
    add_body(doc, "Chaque notification conserve le canal, la facture concernée, le destinataire, le statut ENVOYEE, NON_CONFIGUREE ou ECHEC et le message d'erreur éventuel. L'agent peut donc vérifier si une facture est publiée sans supposer que le message a effectivement été transmis.")
    add_heading(doc, "5.13. Description des formulaires de gestion", 2)
    add_body(doc, "Le formulaire de contrat est organisé en groupes afin de distinguer les informations d'identification, les attributs administratifs, les services par défaut et la résiliation. Les dates sont saisies avec un calendrier, les catégories et modes de règlement utilisent des listes contrôlées et les cases d'exonération ou de résiliation sont associées à une zone de motif lorsque cela est nécessaire.")
    add_body(doc, "Le formulaire de ligne reprend le MSISDN, l'utilisateur, le forfait, le cycle et les options. Une ligne peut être saisie manuellement, importée depuis un fichier ou sélectionnée depuis la base. Dans ce dernier cas, l'interface doit afficher le numéro et le nom de l'utilisateur déjà associé. Si l'agent crée l'employé au moment de l'affectation, le numéro sélectionné doit être prérempli et non modifiable.")
    add_body(doc, "Le formulaire de forfait permet de saisir le nom, le code, le type, le prix et les quotas. Le formulaire de service indique s'il s'agit d'un pass, d'une option ou d'une promotion. Les montants sont contrôlés côté frontend pour guider l'utilisateur et côté backend pour empêcher une valeur négative ou une modification non autorisée.")
    add_body(doc, "Le formulaire de simulation adapte ses champs au type de service. Les unités doivent être explicites : minutes pour la voix, nombre de messages pour les SMS et Mo ou Go pour la data. Le résultat affiche à la fois le total estimé et la ventilation afin que le client puisse comprendre l'effet d'une option ou d'un dépassement de palier.")
    add_heading(doc, "5.14. Accessibilité et ergonomie", 2)
    add_body(doc, "Les boutons doivent porter un libellé compréhensible, les icônes d'action doivent proposer une infobulle et les couleurs ne doivent pas être l'unique moyen de distinguer un état. Les tableaux doivent avoir un en-tête identifiable, une pagination visible et un message lorsque la liste est vide. Les modales doivent pouvoir être fermées, notamment lorsqu'un utilisateur annule la création d'un payeur ou d'un employé.")
    add_body(doc, "La barre latérale reste fixe lors du défilement afin que l'utilisateur conserve son repère de navigation. Les formulaires longs sont découpés en sections et les erreurs sont affichées près des champs concernés. Sur mobile, les colonnes moins importantes peuvent être regroupées dans le détail, mais le numéro de facture, la date, le statut et l'action principale doivent rester accessibles.")
    add_heading(doc, "5.15. Parcours de contrôle avant publication", 2)
    for item in [
        "Vérifier que la période saisie correspond à celle du PDF.",
        "Vérifier que le type globale ou sommaire correspond au contenu du bloc.",
        "Vérifier que le compte ou les MSISDN présents dans les pages existent dans les contrats actifs.",
        "Lancer un traitement de test sur un échantillon lorsque la structure du document est nouvelle.",
        "Lire les erreurs rouges et corriger les associations sans modifier arbitrairement les factures déjà traitées.",
        "Contrôler un PDF global côté payeur et un PDF sommaire côté employé.",
        "Conserver le rapport et la date de publication pour la traçabilité.",
    ]:
        add_number(doc, item)

    add_heading(doc, "CONCLUSION", 1)
    add_body(doc, "Le projet avait pour question centrale la mise à disposition d'un portail sécurisé pour publier et consulter les factures clients postpayés de Moov Africa Togo. La solution développée répond à cette question par une architecture web composée d'une API Django, d'une interface React et d'une base PostgreSQL. Elle prend en compte la différence entre facture globale et facture sommaire, les droits du payeur et de l'employé, la gestion des contrats, la simulation et l'historique.")
    add_body(doc, "Sur le plan technique, le découpage et le rapprochement des PDF ont été isolés dans un service dédié. L'utilisation de Celery et de Garnet permet de rendre les traitements longs persistants et indépendants de la page affichée. Les tests fonctionnels ont permis de vérifier les principaux parcours d'authentification, de gestion, d'import et de consultation.")
    add_body(doc, "Le projet reste une version de stage : l'OCR n'est pas prévu pour les PDF image, le stockage média doit être durci en production, les clés SMTP et SMS doivent rester externalisées, et une supervision complète doit être ajoutée avant une mise en production à grande échelle. Les perspectives portent sur l'intégration aux systèmes de facturation de Moov Africa, la notification e-mail/SMS réellement activée, le déploiement conteneurisé, la supervision et l'amélioration du rapprochement des documents.")

    add_heading(doc, "BIBLIOGRAPHIE INDICATIVE", 1)
    for item in [
        "Documentation pédagogique IAI-TOGO, Cahier des charges du stage pratique GLSI-ASR, 2026.",
        "Cours de génie logiciel et de modélisation UML, IAI-TOGO.",
        "KOUMAGLO A. Jean-Luc, Mémoire de troisième année GLSI-A, IAI-TOGO, 2026 (référence de structure et de présentation).",
        "OURO-BANG'NA Taoufik, Mémoire ITI, IAI-TOGO, 2025 (référence de structure, de tableaux et de guide d'exploitation).",
        "Documentation Django, Django REST Framework et Django ORM.",
        "Documentation React et Vite.",
        "Documentation PostgreSQL, Celery et PyPDF2.",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "WEBOGRAPHIE INDICATIVE", 1)
    for item in [
        "https://docs.djangoproject.com/",
        "https://www.django-rest-framework.org/",
        "https://react.dev/",
        "https://vite.dev/",
        "https://www.postgresql.org/docs/",
        "https://docs.celeryq.dev/",
        "https://plantuml.com/",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "DOCUMENTS ANNEXES", 1)
    add_heading(doc, "Annexe A : commandes de démarrage", 2)
    add_body(doc, "Backend : python manage.py migrate puis python manage.py runserver. Frontend : npm install puis npm run dev. Traitements asynchrones : démarrer Garnet/Redis puis python -m celery -A moov_backend worker -l INFO -P solo. Les commandes doivent être exécutées dans les dossiers indiqués et avec les variables .env configurées.")
    add_heading(doc, "Annexe B : matrice de vérification fonctionnelle", 2)
    add_table(doc, ["Scénario", "Résultat attendu", "État"], [
        ["Connexion employé", "Accès au tableau de bord et aux seules factures de la ligne.", "À vérifier avant livraison"],
        ["Connexion payeur", "Accès à la facture globale et aux factures sommaires de la flotte.", "À vérifier avant livraison"],
        ["Demande commerciale", "Demande créée en attente et visible par le valideur.", "Fonctionnel"],
        ["Rejet de demande", "Motif obligatoire, visible par le commercial.", "Fonctionnel"],
        ["Import PDF sommaire", "Découpage, rapprochement par MSISDN et rapport.", "Fonctionnel selon structure PDF"],
        ["Import PDF global", "Découpage par compte entreprise et rattachement global.", "Fonctionnel selon structure PDF"],
        ["Simulation", "Calcul affiché et historique mis à jour.", "Fonctionnel"],
        ["Téléchargement PDF", "Téléchargement du fichier réellement associé.", "À vérifier avec stockage de production"],
    ], [2800, 5000, 2360], caption="Tableau 10 : Scénarios de vérification fonctionnelle")
    add_heading(doc, "Annexe C : pièces à joindre dans la version soutenue", 2)
    for item in [
        "Diagramme de contexte et diagrammes de cas d'utilisation exportés depuis Draw.io ou PlantUML.",
        "Diagrammes d'activité et de séquence des cas « Publier un bloc PDF » et « Consulter une facture ».",
        "Captures des interfaces principales avec légendes et sources.",
        "Copie du planning validé et des comptes rendus de suivi.",
        "Guide de démarrage et liste des comptes de démonstration sans mots de passe réels.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "Annexe D : exemple de rapport de traitement PDF", 2)
    add_table(doc, ["Indicateur", "Valeur exemple", "Interprétation"], [
        ["Pages analysées", "120", "Nombre de pages parcourues par le lecteur PDF."],
        ["Blocs détectés", "20", "Nombre de débuts de factures reconnus."],
        ["Fichiers créés", "20", "Nombre de PDF individuels générés sur le disque."],
        ["Factures associées", "18", "Fichiers rapprochés avec une facture EN_COURS."],
        ["Déjà traitées", "1", "Facture retrouvée avec un statut VALIDEE, PUBLIEE ou PAYEE."],
        ["Erreurs", "1", "Fichier sans correspondance ou erreur de traitement."],
    ], [2500, 2100, 4460], caption="Tableau 16 : Exemple de lecture d'un rapport de publication")
    add_body(doc, "Dans cet exemple, le découpage physique est réussi pour les vingt blocs. Le résultat métier est partiel puisque deux blocs ne deviennent pas immédiatement consultables : l'un correspond à un document déjà traité et l'autre doit être analysé à partir de ses identifiants et de la période. L'opérateur ne doit donc pas conclure à un échec complet en regardant uniquement le nombre d'erreurs.")
    add_heading(doc, "Annexe E : exemple de données de test non sensibles", 2)
    add_table(doc, ["Profil", "Identifiant de démonstration", "Données associées"], [
        ["Agent", "agent.demo@moov.test", "Droit de publication et de suivi des traitements."],
        ["Payeur", "compte de démonstration", "Contrat de test et factures globales/sommaires."],
        ["Employé", "MSISDN de démonstration", "Une ligne et une facture sommaire."],
        ["Commercial", "commercial.demo@moov.test", "Demandes de contrat en attente ou rejetées."],
    ], [2300, 3000, 3760], caption="Tableau 17 : Profils de démonstration à remplacer par des comptes temporaires")
    add_body(doc, "Les mots de passe réels ne doivent pas figurer dans le mémoire. Les comptes de démonstration sont créés uniquement dans une base de test et doivent être désactivés ou supprimés avant une mise en production.")
    add_heading(doc, "Annexe F : extraits de diagrammes à produire pour la soutenance", 2)
    add_body(doc, "Pour la version finale, les diagrammes de contexte, de cas d'utilisation, d'activité et de séquence doivent être exportés en haute résolution et insérés avec une légende. Le diagramme de classes intégré dans la partie 2 peut être complété par les diagrammes PlantUML versionnés dans le projet. Chaque figure doit être citée dans le texte et sa source doit être indiquée lorsqu'elle provient d'un outil externe.")
    add_heading(doc, "Annexe G : cahier de tests détaillé", 2)
    add_table(doc, ["ID", "Précondition", "Action", "Résultat attendu"], [
        ["T01", "Compte actif", "Saisir identifiant et mot de passe corrects", "Jetons reçus et redirection selon rôle"],
        ["T02", "Compte actif", "Saisir un mot de passe incorrect", "HTTP 401 sans détail sensible"],
        ["T03", "2FA activé", "Saisir un OTP valide", "Connexion acceptée"],
        ["T04", "2FA activé", "Saisir un OTP expiré", "Connexion refusée et message clair"],
        ["T05", "Rôle commercial", "Soumettre un contrat complet", "Demande PENDING créée"],
        ["T06", "Demande PENDING", "Valider la demande", "Contrat créé et audit enregistré"],
        ["T07", "Demande PENDING", "Rejeter sans motif", "Validation refusée"],
        ["T08", "Demande PENDING", "Rejeter avec motif", "REJECTED et motif visible"],
        ["T09", "MSISDN absent", "Créer une ligne de huit chiffres", "Ligne créée"],
        ["T10", "MSISDN existant", "Créer le même numéro", "Erreur d'unicité et proposition d'association"],
        ["T11", "Facture EN_COURS", "Importer PDF sommaire", "Bloc créé et matching MSISDN"],
        ["T12", "Facture EN_COURS", "Importer PDF global", "Bloc créé et matching compte"],
        ["T13", "Facture VALIDEE", "Réimporter le même PDF", "Document marqué déjà traité"],
        ["T14", "PDF chiffré", "Lancer l'import", "Traitement ECHEC"],
        ["T15", "PDF sans identifiant", "Lancer l'import", "Warning par page et aucune association arbitraire"],
        ["T16", "Traitement en cours", "Quitter la page", "Worker continue et statut persiste"],
        ["T17", "Facture avec PDF", "Ouvrir aperçu", "PDF réel retourné avec type application/pdf"],
        ["T18", "Employé d'une ligne", "Ouvrir facture d'une autre ligne", "HTTP 403 ou liste vide"],
        ["T19", "Payeur d'un contrat", "Ouvrir facture d'un autre contrat", "Accès refusé"],
        ["T20", "Catalogue actif", "Simuler voix/SMS/data", "Montant détaillé conforme aux paliers"],
        ["T21", "Simulation valide", "Consulter historique", "Simulation présente avec date et résultat"],
        ["T22", "Tarif option", "Modifier prix depuis rôle autorisé", "Prix enregistré et visible"],
        ["T23", "Utilisateur inactif", "Appeler une route métier", "Accès refusé"],
        ["T24", "Données de test", "Réinitialiser une période", "Seules les données prévues sont supprimées"],
    ], [700, 2200, 3000, 3460], caption="Tableau 22 : Cahier de tests détaillé")
    add_heading(doc, "Annexe H : structure indicative d'une réponse de traitement", 2)
    add_body(doc, "Un résultat de traitement doit pouvoir être lu par l'interface et par un opérateur. Il contient le statut, la progression, un résumé du nombre de pages et de blocs, puis une section matching avec attached, skipped et errors. Les erreurs doivent conserver le nom de fichier et les identifiants détectés ; cette information est indispensable pour corriger les données sans ouvrir chaque PDF manuellement.")
    add_table(doc, ["Section", "Contenu", "Usage"], [
        ["status", "EN_ATTENTE, EN_COURS, TERMINE ou ECHEC", "Badge d'état et filtrage de l'historique."],
        ["progression", "0 à 100", "Barre de progression et indication de durée."],
        ["summary", "pages, blocks_detected, files_created", "Résumé rapide de l'opération."],
        ["matching.attached", "facture_id, numéro, filename, identifiers", "Vérification des associations réussies."],
        ["matching.skipped", "facture_id, statut, raison", "Explication des documents déjà traités."],
        ["matching.errors", "filename, erreur, identifiers", "Correction des anomalies."],
    ], [2200, 4400, 2760], caption="Tableau 23 : Structure logique du rapport de traitement")

    # Update fields when opened by Word/LibreOffice.
    settings = doc.settings.element
    update = settings.find(qn("w:updateFields"))
    if update is None:
        update = OxmlElement("w:updateFields")
        settings.append(update)
    update.set(qn("w:val"), "true")
    doc.core_properties.title = "Développement d'un portail web de publication de factures clients postpayés"
    doc.core_properties.subject = "Mémoire de fin de formation GLSI - IAI-TOGO"
    doc.core_properties.author = "BANLEPO Mintre Benoît"
    doc.core_properties.comments = "Version de travail structurée selon le cahier des charges IAI-TOGO 2026."
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
