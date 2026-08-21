from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "docs" / "Configuration_materielle_Moov_eFactures_Dell_Precision_7680.docx"

ROWS = [
    ("Marque", "Dell Inc.", "Constructeur du poste utilisé pour le développement."),
    ("Modèle", "Precision 7680", "Modèle de l'ordinateur portable utilisé pour le projet."),
    ("Processeur", "Intel64 Family 6 Model 183 Stepping 1, environ 2100 MHz", "Processeur utilisé pour exécuter l'environnement de développement et les services locaux."),
    ("Type de système", "PC basé sur x64, système 64 bits", "Architecture du système installée sur le poste."),
    ("Mémoire vive (RAM)", "32 421 Mo, soit environ 32 Go", "Mémoire disponible pour le fonctionnement du backend, du frontend et des outils de test."),
    ("Disque dur", "NVMe PC811 SK hynix, environ 1 To", "Stockage utilisé pour le système, le code source, les dépendances et les fichiers PDF."),
    ("Système d'exploitation", "Windows 11 Professionnel, version 10.0.26200", "Système d'exploitation installé sur le poste de développement."),
    ("Cartes graphiques", "NVIDIA RTX 2000 Ada Generation Laptop GPU et Intel UHD Graphics", "Cartes graphiques détectées sur le poste."),
]

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def tag(name, attrs="", body=""):
    return f'<w:{name} {attrs}>{body}</w:{name}>' if attrs else f'<w:{name}>{body}</w:{name}>'


def font_props(size, bold=False, color="000000"):
    bits = ['<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/>', f'<w:sz w:val="{size * 2}"/><w:szCs w:val="{size * 2}"/>']
    if bold:
        bits.append('<w:b/><w:bCs/>')
    if color:
        bits.append(f'<w:color w:val="{color}"/>')
    return tag("rPr", body="".join(bits))


def run(text, size=10, bold=False, color="000000"):
    return tag("r", body=font_props(size, bold, color) + tag("t", 'xml:space="preserve"', escape(text)))


def paragraph(text, size=12, bold=False, color="000000", align="left", before=0, after=0):
    ppr = f'<w:spacing w:before="{before}" w:after="{after}" w:line="240" w:lineRule="auto"/><w:jc w:val="{align}"/>'
    return tag("p", body=tag("pPr", body=ppr) + run(text, size, bold, color))


def cell(text, width, fill=None, header=False):
    shading = f'<w:shd w:val="clear" w:fill="{fill}"/>' if fill else ""
    tcpr = (
        f'<w:tcW w:w="{width}" w:type="dxa"/>{shading}'
        '<w:tcMar><w:top w:w="90" w:type="dxa"/><w:start w:w="120" w:type="dxa"/>'
        '<w:bottom w:w="90" w:type="dxa"/><w:end w:w="120" w:type="dxa"/></w:tcMar>'
        '<w:vAlign w:val="center"/>'
    )
    return tag("tc", body=tag("tcPr", body=tcpr) + paragraph(text, 10, header, "FFFFFF" if header else "000000"))


def table_xml():
    widths = [2600, 3000, 4038]
    borders = ''.join(f'<w:{edge} w:val="single" w:sz="6" w:space="0" w:color="808080"/>' for edge in ("top", "left", "bottom", "right", "insideH", "insideV"))
    props = f'<w:tblW w:w="9638" w:type="dxa"/><w:tblLayout w:type="fixed"/><w:tblInd w:w="0" w:type="dxa"/><w:tblBorders>{borders}</w:tblBorders>'
    grid = ''.join(f'<w:gridCol w:w="{width}"/>' for width in widths)
    headers = tag("tr", body=''.join(cell(value, width, "1F4E78", True) for value, width in zip(("Composant", "Caractéristique", "Description / rôle"), widths)))
    rows = [headers]
    for values in ROWS:
        rows.append(tag("tr", body=''.join(cell(value, width) for value, width in zip(values, widths))))
    return tag("tbl", body=tag("tblPr", body=props) + tag("tblGrid", body=grid) + ''.join(rows))


def document_xml():
    title = paragraph("4.1.2. Configuration matérielle", 14, True, "1F4E78", "center", after=160)
    caption = paragraph("Tableau : Configuration matérielle de l'application", 11, True, "000000", "center", after=160)
    intro = paragraph("La configuration matérielle présentée correspond au poste utilisé pour développer, exécuter et tester le portail Moov e-Factures en environnement local.", 11, False, "000000", "left", after=160)
    note = paragraph("Remarque : cette configuration convient au développement et aux démonstrations locales. Une mise en production nécessiterait un serveur dimensionné selon le nombre d'utilisateurs et le volume de factures traitées.", 10, False, "444444", "left", before=160)
    sect = tag("sectPr", body='<w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="567" w:footer="567" w:gutter="0"/><w:cols w:space="720"/><w:docGrid w:linePitch="360"/>')
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>{tag("document", f'xmlns:w="{W}" xmlns:r="{R}"', tag("body", body=title + intro + caption + table_xml() + note + sect))}'


def styles_xml():
    normal = '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr></w:style>'
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>{tag("styles", f'xmlns:w="{W}"', '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/></w:rPr></w:rPrDefault></w:docDefaults>' + normal)}'


def build():
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'''
    root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
    doc_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", root_rels)
        archive.writestr("word/document.xml", document_xml())
        archive.writestr("word/styles.xml", styles_xml())
        archive.writestr("word/_rels/document.xml.rels", doc_rels)
    print(OUTPUT)


if __name__ == "__main__":
    build()
