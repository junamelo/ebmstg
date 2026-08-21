from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PNG = DOCS / "diagramme_contexte_moov_efactures_nouveaux_acteurs.png"
SVG = DOCS / "diagramme_contexte_moov_efactures_nouveaux_acteurs.svg"

W, H = 2400, 1500
BLUE = "#0056B3"
BLACK = "#111111"
GREEN = "#35A853"
PURPLE = "#7659C7"
ORANGE = "#F0A000"
YELLOW = "#F3C74F"
GREY = "#777777"
LIGHT_GREY = "#F5F5F5"

font_dir = Path(r"C:\Windows\Fonts")


def fnt(size: int, bold: bool = False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(font_dir / name), size)


def multiline(draw, xy, text, size, fill=BLACK, bold=False, anchor="ma", spacing=5):
    draw.multiline_text(xy, text, font=fnt(size, bold), fill=fill, anchor=anchor, align="center", spacing=spacing)


def arrow(draw, start, end, color=BLACK, width=4, head=16):
    draw.line([start, end], fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) > abs(y2 - y1):
        sign = 1 if x2 > x1 else -1
        pts = [(x2, y2), (x2 - sign * head, y2 - head // 2), (x2 - sign * head, y2 + head // 2)]
    else:
        sign = 1 if y2 > y1 else -1
        pts = [(x2, y2), (x2 - head // 2, y2 - sign * head), (x2 + head // 2, y2 - sign * head)]
    draw.polygon(pts, fill=color)


def actor(draw, cx, top, female=False):
    # Simple black line-art actor, matching the supplied reference image.
    head_r = 22
    draw.ellipse((cx - head_r, top, cx + head_r, top + 2 * head_r), outline=BLACK, width=5)
    if female:
        draw.arc((cx - 28, top - 8, cx + 28, top + 44), 180, 360, fill=BLACK, width=5)
        draw.line((cx - 28, top + 16, cx - 28, top + 70), fill=BLACK, width=5)
        draw.line((cx + 28, top + 16, cx + 28, top + 70), fill=BLACK, width=5)
    body_y = top + 2 * head_r + 10
    draw.line((cx, body_y, cx, body_y + 68), fill=BLACK, width=5)
    draw.line((cx, body_y + 12, cx - 38, body_y + 50), fill=BLACK, width=5)
    draw.line((cx, body_y + 12, cx + 38, body_y + 50), fill=BLACK, width=5)
    draw.line((cx, body_y + 68, cx - 25, body_y + 115), fill=BLACK, width=5)
    draw.line((cx, body_y + 68, cx + 25, body_y + 115), fill=BLACK, width=5)


def rounded(draw, box, radius, outline, fill=None, width=4):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


def draw_envelope(draw, cx, cy, color):
    box = (cx - 40, cy - 26, cx + 40, cy + 26)
    draw.rounded_rectangle(box, radius=5, outline=color, width=5)
    draw.line((box[0], box[1], cx, cy + 5, box[2], box[1]), fill=color, width=4)


def draw_document(draw, cx, cy, color):
    box = (cx - 34, cy - 48, cx + 34, cy + 48)
    draw.rectangle(box, outline=color, width=5)
    draw.line((cx + 10, cy - 48, cx + 34, cy - 24), fill=color, width=5)
    draw.line((cx - 18, cy - 5, cx + 18, cy - 5), fill=color, width=4)
    draw.line((cx - 18, cy + 14, cx + 18, cy + 14), fill=color, width=4)


def draw_cylinder(draw, cx, cy, color):
    draw.ellipse((cx - 65, cy - 28, cx + 65, cy + 4), outline=color, width=4, fill="#FBF9FF")
    draw.rectangle((cx - 65, cy - 12, cx + 65, cy + 54), outline=color, width=4, fill="#FBF9FF")
    draw.ellipse((cx - 65, cy + 36, cx + 65, cy + 68), outline=color, width=4, fill="#FBF9FF")


def make_png():
    image = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(image)

    actor_data = [
        ("Super\nadministrateur", "Gérer les comptes et les rôles\nConfigurer les forfaits et services\nAdministrer la plateforme", True),
        ("Chef de\nfacturation", "Traiter les demandes de contrat\nValider ou rejeter les demandes\nSuperviser la facturation", False),
        ("Agent de\nfacturation", "Gérer les contrats et les lignes\nImporter et publier les PDF\nSuivre les traitements", False),
        ("Commercial", "Créer une demande de contrat\nSuivre ses demandes\nConsulter ses contrats", False),
        ("Payeur", "Consulter la facture globale\nConsulter les factures sommaires\nSimuler la facturation", False),
        ("Employé", "Consulter sa facture sommaire\nVoir ses services\nSimuler sa consommation", True),
    ]
    left = 65
    col_w = 370
    gap = 20
    centers = []
    for i, (name, interactions, female) in enumerate(actor_data):
        cx = left + i * (col_w + gap) + col_w // 2
        centers.append(cx)
        actor(draw, cx, 60, female)
        multiline(draw, (cx, 210), name, 26, bold=True, spacing=1)
        multiline(draw, (cx, 278), "Interactions :\n- " + interactions.replace("\n", "\n- "), 17, spacing=4)

    portal = (275, 610, 2125, 820)
    rounded(draw, portal, 12, BLUE, fill=BLUE, width=4)
    multiline(draw, ((portal[0] + portal[2]) // 2, 714), "PORTAIL WEB DE PUBLICATION\nDES FACTURES CLIENTS POSTPAYÉS\nMOOV AFRICA TOGO", 31, fill="white", bold=True, spacing=8)

    # Actor-to-portal arrows.
    for cx in centers:
        arrow(draw, (cx, 522), (cx, portal[1]), width=4)

    components = [
        ("Serveur SMTP", "Notifications par e-mail\n(réinitialisation de mot de passe,\nalertes et notifications)", GREEN, "smtp"),
        ("PostgreSQL", "Base de données\n(comptes, entreprises, contrats,\nlignes, factures, tarifs et historiques)", PURPLE, "db"),
        ("Stockage des\nfactures PDF", "Blocs PDF sources\net factures publiées", ORANGE, "pdf"),
        ("Traitement asynchrone", "Garnet + Celery\nDécoupage et publication\nen arrière-plan", YELLOW, "async"),
        ("Système de facturation\nMoov Africa", "Données de consommation\net de facturation", GREY, "billing"),
    ]
    box_w = 390
    box_h = 250
    gap_b = 35
    start_x = 75
    box_top = 1090
    for i, (title, desc, color, icon) in enumerate(components):
        x = start_x + i * (box_w + gap_b)
        box = (x, box_top, x + box_w, box_top + box_h)
        if icon == "db":
            draw_cylinder(draw, x + box_w // 2, box_top + 55, color)
            title_y = box_top + 110
        elif icon == "smtp":
            draw_envelope(draw, x + box_w // 2, box_top + 52, color)
            title_y = box_top + 105
        elif icon == "pdf":
            draw_document(draw, x + box_w // 2, box_top + 55, color)
            title_y = box_top + 112
        else:
            rounded(draw, box, 8, color, fill=LIGHT_GREY if icon != "billing" else "#FAFAFA", width=4)
            title_y = box_top + 62
        if icon in {"db", "smtp", "pdf"}:
            rounded(draw, box, 8, color, fill="#FFFFFF", width=4)
        multiline(draw, (x + box_w // 2, title_y), title, 23, bold=True, spacing=2)
        multiline(draw, (x + box_w // 2, box_top + 172), desc, 16, spacing=5)
        arrow(draw, ((portal[0] + portal[2]) // 2, portal[3]), (x + box_w // 2, box_top), width=4)

    # Labels on the lower connectors, kept short like the reference.
    connector_labels = [
        ("Envoi d'e-mails", 270),
        ("Lecture / écriture\ndes données", 675),
        ("Stockage / récupération\ndes factures PDF", 1080),
        ("Mise en file des\ntraitements longs", 1485),
        ("Échange de données\nde consommation", 1890),
    ]
    for text, cx in connector_labels:
        multiline(draw, (cx, 950), text, 16, spacing=3)

    image.save(PNG, optimize=True)


def svg_text(x, y, text, size, fill=BLACK, bold=False, anchor="middle"):
    weight = "700" if bold else "400"
    lines = text.split("\n")
    out = []
    for idx, line in enumerate(lines):
        dy = idx * (size + 5)
        out.append(f'<text x="{x}" y="{y + dy}" font-family="Arial" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(line)}</text>')
    return "".join(out)


def make_svg():
    # The SVG mirrors the PNG geometry and remains editable in Word/Inkscape.
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '<rect width="100%" height="100%" fill="white"/>']
    parts.append(svg_text(W // 2, 35, "Architecture de contexte du portail Moov e-Factures", 29, bold=True))
    actor_names = ["Super\nadministrateur", "Chef de\nfacturation", "Agent de\nfacturation", "Commercial", "Payeur", "Employé"]
    actor_interactions = ["Gérer les comptes et les rôles\\nConfigurer les forfaits et services\\nAdministrer la plateforme", "Traiter les demandes de contrat\\nValider ou rejeter les demandes\\nSuperviser la facturation", "Gérer les contrats et les lignes\\nImporter et publier les PDF\\nSuivre les traitements", "Créer une demande de contrat\\nSuivre ses demandes\\nConsulter ses contrats", "Consulter la facture globale\\nConsulter les factures sommaires\\nSimuler la facturation", "Consulter sa facture sommaire\\nVoir ses services\\nSimuler sa consommation"]
    left, col_w, gap = 65, 370, 20
    centers = []
    for i, name in enumerate(actor_names):
        cx = left + i * (col_w + gap) + col_w // 2
        centers.append(cx)
        parts.append(f'<circle cx="{cx}" cy="82" r="22" fill="none" stroke="{BLACK}" stroke-width="5"/><line x1="{cx}" y1="104" x2="{cx}" y2="180" stroke="{BLACK}" stroke-width="5"/><line x1="{cx}" y1="116" x2="{cx-38}" y2="154" stroke="{BLACK}" stroke-width="5"/><line x1="{cx}" y1="116" x2="{cx+38}" y2="154" stroke="{BLACK}" stroke-width="5"/><line x1="{cx}" y1="180" x2="{cx-25}" y2="227" stroke="{BLACK}" stroke-width="5"/><line x1="{cx}" y1="180" x2="{cx+25}" y2="227" stroke="{BLACK}" stroke-width="5"/>')
        parts.append(svg_text(cx, 220, name, 26, bold=True))
        parts.append(svg_text(cx, 285, "Interactions :", 17, bold=False))
        parts.append(svg_text(cx, 311, actor_interactions[i].replace('\\n', '\\n'), 16))
    portal = (275, 610, 2125, 820)
    parts.append(f'<rect x="{portal[0]}" y="{portal[1]}" width="{portal[2]-portal[0]}" height="{portal[3]-portal[1]}" rx="12" fill="{BLUE}" stroke="{BLUE}" stroke-width="4"/>')
    parts.append(svg_text(W // 2, 690, "PORTAIL WEB DE PUBLICATION\\nDES FACTURES CLIENTS POSTPAYÉS\\nMOOV AFRICA TOGO".replace('\\n', '\\n'), 31, fill="white", bold=True))
    for cx in centers:
        parts.append(f'<line x1="{cx}" y1="522" x2="{cx}" y2="610" stroke="{BLACK}" stroke-width="4" marker-end="url(#arrow)"/>')
    parts.append('<defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#111111"/></marker></defs>')
    components = [("Serveur SMTP", "Notifications par e-mail", GREEN), ("PostgreSQL", "Base de données métier", PURPLE), ("Stockage des factures PDF", "Blocs sources et factures publiées", ORANGE), ("Traitement asynchrone", "Garnet + Celery", YELLOW), ("Système de facturation Moov Africa", "Données de consommation et facturation", GREY)]
    box_w, box_h, gap_b, start_x, box_top = 390, 250, 35, 75, 1090
    for i, (title, desc, color) in enumerate(components):
        x = start_x + i * (box_w + gap_b)
        parts.append(f'<rect x="{x}" y="{box_top}" width="{box_w}" height="{box_h}" rx="8" fill="white" stroke="{color}" stroke-width="4"/>')
        parts.append(svg_text(x + box_w // 2, box_top + 94, title, 22, bold=True))
        parts.append(svg_text(x + box_w // 2, box_top + 160, desc, 16))
        parts.append(f'<line x1="{W//2}" y1="820" x2="{x+box_w//2}" y2="1090" stroke="{BLACK}" stroke-width="4" marker-end="url(#arrow)"/>')
    parts.append('</svg>')
    SVG.write_text("".join(parts), encoding="utf-8")


if __name__ == "__main__":
    DOCS.mkdir(parents=True, exist_ok=True)
    make_png()
    make_svg()
    print(PNG)
    print(SVG)
