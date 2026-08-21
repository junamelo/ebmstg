from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape
from pathlib import Path

OUT = Path('docs/PRESENTATION_DES_ETATS_MOOV_EFACTURES.docx')
OUT.parent.mkdir(parents=True, exist_ok=True)

NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def rpr(bold=False, size=24, color='000000'):
    return (
        '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/>'
        + (f'<w:b/>' if bold else '')
        + f'<w:sz w:val="{size}"/><w:color w:val="{color}"/>'
        + '</w:rPr>'
    )

def run(text, bold=False, size=24, color='000000'):
    return f'<w:r>{rpr(bold, size, color)}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'

def p(text='', bold=False, size=24, align='left', before=0, after=120, keep=False):
    jc = f'<w:jc w:val="{align}"/>'
    keep_xml = '<w:keepNext/>' if keep else ''
    return (
        f'<w:p><w:pPr>{jc}<w:spacing w:before="{before}" w:after="{after}" w:line="276" w:lineRule="auto"/>{keep_xml}</w:pPr>'
        f'{run(text, bold, size)}</w:p>'
    )

def table(rows, widths=(2250, 6808)):
    grid = ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    parts = [
        '<w:tbl><w:tblPr><w:tblW w:w="9058" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
        '<w:tblBorders><w:top w:val="single" w:sz="6" w:color="808080"/><w:left w:val="single" w:sz="6" w:color="808080"/>'
        '<w:bottom w:val="single" w:sz="6" w:color="808080"/><w:right w:val="single" w:sz="6" w:color="808080"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="BFBFBF"/><w:insideV w:val="single" w:sz="4" w:color="BFBFBF"/></w:tblBorders>'
        '<w:tblCellMar><w:top w:w="100" w:type="dxa"/><w:left w:w="120" w:type="dxa"/><w:bottom w:w="100" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tblCellMar>'
        '</w:tblPr><w:tblGrid>' + grid + '</w:tblGrid>'
    ]
    for row_i, row in enumerate(rows):
        parts.append('<w:tr>')
        for col_i, value in enumerate(row):
            fill = 'E7E6E6' if row_i == 0 else 'FFFFFF'
            bold = row_i == 0
            parts.append(
                f'<w:tc><w:tcPr><w:tcW w:w="{widths[col_i]}" w:type="dxa"/><w:shd w:fill="{fill}"/></w:tcPr>'
                f'<w:p><w:pPr><w:spacing w:after="0" w:line="276" w:lineRule="auto"/></w:pPr>{run(value, bold, 22)}</w:p></w:tc>'
            )
        parts.append('</w:tr>')
    parts.append('</w:tbl>')
    return ''.join(parts)

body = []
body.append(p('5.4. PRÉSENTATION DES ÉTATS', bold=True, size=32, align='center', after=240))
body.append(p("Les états de l'application Moov e-Factures permettent de connaître l'avancement d'une demande, d'une facture, d'un traitement PDF ou d'une notification. Ils sont présentés ci-dessous sous la forme de tableaux indiquant l'état et sa signification." , size=24, after=180))

tables = [
    ('Tableau 1 : États d’une demande de contrat', [
        ('État', 'Signification'),
        ('En attente de validation', 'La demande a été soumise par le commercial et attend la décision d’un agent ou du chef de facturation.'),
        ('Approuvée', 'La demande a été acceptée et peut donner lieu à la création effective du contrat.'),
        ('Rejetée', 'La demande n’a pas été acceptée. Le motif de rejet est conservé et rendu visible au commercial.'),
    ]),
    ('Tableau 2 : États d’une facture', [
        ('État', 'Signification'),
        ('Brouillon', 'La facture est enregistrée mais n’est pas encore prête pour la validation.'),
        ('En cours', 'La facture est en cours de contrôle ou de traitement.'),
        ('Validée', 'La facture a été contrôlée et peut être publiée.'),
        ('Publiée', 'La facture est disponible pour le payeur ou l’employé autorisé.'),
        ('Payée', 'Le règlement de la facture a été enregistré.'),
        ('Annulée', 'La facture ne peut plus être utilisée comme facture active.'),
    ]),
    ('Tableau 3 : États d’un traitement PDF', [
        ('État', 'Signification'),
        ('En attente', 'Le traitement est enregistré et attend son exécution par le worker Celery.'),
        ('En cours', 'Le bloc PDF est en train d’être découpé et les factures sont rapprochées des contrats ou des lignes.'),
        ('Terminé', 'Le traitement est achevé. Le résultat et les éventuelles erreurs sont disponibles dans le rapport.'),
        ('Échec', 'Le traitement n’a pas pu aboutir. Une erreur doit être consultée avant une nouvelle tentative.'),
    ]),
    ('Tableau 4 : États d’une notification de facture', [
        ('État', 'Signification'),
        ('Envoyée', 'La notification a été transmise correctement au destinataire.'),
        ('Échec', 'L’envoi n’a pas abouti. Le détail de l’erreur est conservé dans l’historique.'),
        ('Service non configuré', 'Le service de notification n’est pas configuré ; la publication de la facture reste indépendante de cette notification.'),
    ]),
]

for idx, (caption, rows) in enumerate(tables):
    body.append(p(caption, bold=True, size=24, before=160, after=100, keep=True))
    body.append(table(rows))
    body.append(p('', after=80))

body.append(p("La consultation de ces états permet aux utilisateurs de comprendre la situation d’une opération et de savoir quelle action doit être effectuée. Les droits d’accès aux états restent contrôlés selon le rôle de l’utilisateur.", size=24, before=140, after=0))

document = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{NS}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<w:body>{''.join(body)}
<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>
</w:body></w:document>'''

styles = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{NS}">
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="24"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="24"/></w:rPr></w:style>
</w:styles>'''

content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>'''

rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

doc_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''

with ZipFile(OUT, 'w', ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', content_types)
    z.writestr('_rels/.rels', rels)
    z.writestr('word/document.xml', document)
    z.writestr('word/styles.xml', styles)
    z.writestr('word/_rels/document.xml.rels', doc_rels)

print(OUT.resolve())
