from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "docs" / "Configuration_logicielle_Moov_eFactures_sans_repetition.docx"

ROWS = [
    ("Système d'exploitation", "Windows 11 64 bits", "Système utilisé sur le poste de développement et de test."),
    ("Visual Studio Code", "Version installée sur le poste", "Environnement de développement intégré utilisé pour écrire, organiser et déboguer le backend et le frontend."),
    ("Python", "3.14.2", "Langage et environnement d'exécution du backend."),
    ("Django", "6.0.3", "Framework utilisé pour développer l'API et la logique métier."),
    ("Django REST Framework", "3.17.1", "Extension utilisée pour exposer les fonctionnalités sous forme d'API REST."),
    ("Simple JWT", "5.5.1", "Gestion de l'authentification par jetons."),
    ("React", "18.3.1", "Bibliothèque utilisée pour construire l'interface web."),
    ("Vite", "5.x", "Outil de développement et de compilation du frontend React."),
    ("Node.js", "24.16.0", "Environnement d'exécution nécessaire au frontend."),
    ("npm", "11.13.0", "Gestionnaire des dépendances et des scripts frontend."),
    ("PostgreSQL", "16", "Système de gestion de base de données relationnelle utilisé pour la persistance des données."),
    ("SQLite", "Version intégrée à Django", "Base de secours utilisable pour un démarrage local rapide sans PostgreSQL."),
    ("Garnet", "Compatible avec Redis", "Serveur de données en mémoire utilisé pour le cache et comme intermédiaire des tâches asynchrones."),
    ("Celery", "5.6.3", "Exécution en arrière-plan des traitements longs, notamment le découpage et la publication des blocs PDF."),
    ("django-redis", "7.0.0", "Connexion de Django au serveur Garnet compatible avec le protocole Redis."),
    ("PyPDF2", "3.0.1", "Lecture, découpage et manipulation des fichiers PDF."),
    ("Pillow / ReportLab", "12.1.1 / 4.4.10", "Traitement d'images et génération de documents PDF lorsque nécessaire."),
    ("psycopg", "3.3.4", "Pilote permettant à Django de communiquer avec PostgreSQL."),
    ("Git et GitHub", "Git 2.45.1", "Gestion des versions et conservation du code source."),
    ("Postman", "Version installée sur le poste", "Vérification des endpoints de l'API indépendamment de l'interface React."),
    ("Navigateur web", "Chrome, Edge ou équivalent récent", "Accès à l'interface et réalisation des tests fonctionnels."),
]

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XML = "http://www.w3.org/XML/1998/namespace"


def tag(name, attrs="", body=""):
    return f'<w:{name} {attrs}>{body}</w:{name}>' if attrs else f'<w:{name}>{body}</w:{name}>'


def font_props(size, bold=False, color="000000"):
    bits = [f'<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/>']
    bits.append(f'<w:sz w:val="{size * 2}"/><w:szCs w:val="{size * 2}"/>')
    if bold:
        bits.append('<w:b/><w:bCs/>')
    if color:
        bits.append(f'<w:color w:val="{color}"/>')
    return tag("rPr", body="".join(bits))


def run(text, size=10, bold=False, color="000000"):
    return tag("r", body=font_props(size, bold, color) + tag("t", 'xml:space="preserve"', escape(text)))


def paragraph(text, size=12, bold=False, color="000000", align="left", before=0, after=0):
    align_xml = f'<w:jc w:val="{align}"/>'
    spacing = f'<w:spacing w:before="{before}" w:after="{after}" w:line="240" w:lineRule="auto"/>'
    return tag("p", body=tag("pPr", body=spacing + align_xml) + run(text, size, bold, color))


def cell(text, width, fill=None, header=False):
    shading = f'<w:shd w:val="clear" w:fill="{fill}"/>' if fill else ""
    tc_pr = (
        f'<w:tcW w:w="{width}" w:type="dxa"/>'
        f'<w:tcMar><w:top w:w="90" w:type="dxa"/><w:start w:w="120" w:type="dxa"/>'
        f'<w:bottom w:w="90" w:type="dxa"/><w:end w:w="120" w:type="dxa"/></w:tcMar>'
        f'<w:vAlign w:val="center"/>{shading}'
    )
    return tag("tc", body=tag("tcPr", body=tc_pr) + paragraph(text, 10, header, "FFFFFF" if header else "000000", after=0))


def table_xml():
    widths = [2600, 2450, 4588]
    total = sum(widths)
    borders = ''.join(
        f'<w:{edge} w:val="single" w:sz="6" w:space="0" w:color="808080"/>'
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV")
    )
    grid = ''.join(f'<w:gridCol w:w="{width}"/>' for width in widths)
    props = (
        f'<w:tblW w:w="{total}" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
        f'<w:tblInd w:w="0" w:type="dxa"/><w:tblBorders>{borders}</w:tblBorders>'
    )
    rows = []
    header = tag("tr", body=''.join(
        cell(text, width, "1F4E78", True)
        for text, width in zip(("Composant", "Version / paquet", "Description / rôle"), widths)
    ))
    rows.append(header)
    for values in ROWS:
        rows.append(tag("tr", body=''.join(cell(value, width) for value, width in zip(values, widths))))
    return tag("tbl", body=tag("tblPr", body=props) + tag("tblGrid", body=grid) + ''.join(rows))


def document_xml():
    title = paragraph("4.1.1. Configuration logicielle", 14, True, "1F4E78", "center", after=160)
    caption = paragraph("Tableau : Configuration logicielle de mon application", 11, True, after=160)
    note = paragraph(
        "Remarque : PostgreSQL est utilisé pour une exploitation complète. SQLite reste disponible comme solution de secours pour les essais locaux. Les paramètres sensibles sont définis dans le fichier .env et ne doivent pas être versionnés.",
        10, False, "444444", "left", before=160,
    )
    sect = tag("sectPr", body=(
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="567" w:footer="567" w:gutter="0"/>'
        '<w:cols w:space="720"/>'
        '<w:docGrid w:linePitch="360"/>'
    ))
    body = title + caption + table_xml() + note + sect
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>{tag("document", f'xmlns:w="{W}" xmlns:r="{R}"', tag("body", body=body))}'


def styles_xml():
    normal = (
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
        '<w:name w:val="Normal"/><w:qFormat/>'
        '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>'
        '</w:style>'
    )
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>{tag("styles", f'xmlns:w="{W}"', '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/></w:rPr></w:rPrDefault></w:docDefaults>' + normal)}'


def write_docx():
    content_types = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>'''
    root_rels = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
    doc_rels = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", root_rels)
        archive.writestr("word/document.xml", document_xml())
        archive.writestr("word/styles.xml", styles_xml())
        archive.writestr("word/_rels/document.xml.rels", doc_rels)
    print(OUTPUT)


if __name__ == "__main__":
    write_docx()
