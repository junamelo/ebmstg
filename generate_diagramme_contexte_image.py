from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "docs"
PNG = OUT_DIR / "diagramme_contexte_moov_efactures.png"
SVG = OUT_DIR / "diagramme_contexte_moov_efactures.svg"

W, H = 2200, 1500
WHITE = "#FFFFFF"
INK = "#1F2937"
BLUE = "#0B56B8"
BLUE_DARK = "#073A82"
BLUE_LIGHT = "#EAF2FF"
GRAY = "#F5F6F8"
GRAY_BORDER = "#777777"
GOLD = "#FFF7E6"
GOLD_BORDER = "#A66A00"
GREEN = "#F2FFF3"
GREEN_BORDER = "#25833E"


def font(name, size, bold=False):
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


F_TITLE = font("Arial", 42, True)
F_PORTAL = font("Arial", 34, True)
F_ACTOR = font("Arial", 22, True)
F_LABEL = font("Arial", 20, False)
F_BOX = font("Arial", 23, True)
F_SMALL = font("Arial", 18, False)
F_TINY = font("Arial", 16, False)


def multiline(draw, xy, text, fnt, fill=INK, anchor="mm", spacing=5):
    draw.multiline_text(xy, text, font=fnt, fill=fill, anchor=anchor, align="center", spacing=spacing)


def arrow(draw, start, end, fill=INK, width=4, head=15):
    draw.line([start, end], fill=fill, width=width)
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    bx, by = x2 - ux * head * 1.6, y2 - uy * head * 1.6
    points = [(x2, y2), (bx + px * head, by + py * head), (bx - px * head, by - py * head)]
    draw.polygon(points, fill=fill)


def actor(draw, x, y, label):
    # stick figure
    draw.ellipse((x - 15, y - 55, x + 15, y - 25), outline=INK, width=4)
    draw.line((x, y - 25, x, y + 25), fill=INK, width=4)
    draw.line((x - 30, y - 5, x + 30, y - 5), fill=INK, width=4)
    draw.line((x, y + 25, x - 26, y + 62), fill=INK, width=4)
    draw.line((x, y + 25, x + 26, y + 62), fill=INK, width=4)
    multiline(draw, (x, y + 95), label, F_ACTOR, anchor="mm")


def rounded_box(draw, box, fill, outline, radius=18, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def component(draw, box, title, details, fill=GRAY, outline=GRAY_BORDER):
    rounded_box(draw, box, fill, outline, 16, 3)
    x1, y1, x2, y2 = box
    multiline(draw, ((x1 + x2) / 2, y1 + 40), title, F_BOX, anchor="mm")
    multiline(draw, ((x1 + x2) / 2, (y1 + y2) / 2 + 25), details, F_SMALL, anchor="mm")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(image)

    multiline(draw, (W / 2, 48), "Diagramme de contexte - Moov e-Factures", F_TITLE, BLUE_DARK, anchor="ma")

    # Actors
    actor(draw, 210, 170, "Super\nadministrateur")
    actor(draw, 610, 170, "Opérateur de facturation\n(Chef / Agent)")
    actor(draw, 1010, 170, "Commercial")
    actor(draw, 1410, 170, "Payeur")
    actor(draw, 1810, 170, "Employé")

    # Main system
    portal = (470, 455, 1730, 750)
    rounded_box(draw, portal, BLUE, BLUE_DARK, 22, 4)
    multiline(draw, (1100, 560), "PORTAIL WEB MOOV E-FACTURES\nPublication et consultation\ndes factures clients postpayés", F_PORTAL, WHITE, anchor="mm", spacing=9)
    multiline(draw, (1100, 704), "Authentification JWT - permissions par rôle", F_SMALL, "#DCEBFF", anchor="mm")

    # Actor arrows + interaction labels
    actor_targets = [(210, 232, 570, 455), (610, 232, 790, 455), (1010, 232, 990, 455), (1410, 232, 1260, 455), (1810, 232, 1550, 455)]
    for start_x, start_y, end_x, end_y in actor_targets:
        arrow(draw, (start_x, start_y), (end_x, end_y), BLUE_DARK, 4)
    labels = [
        (225, 315, "comptes, rôles\net paramètres"),
        (585, 330, "contrats, lignes\net publication PDF"),
        (1010, 330, "demandes\nde contrat"),
        (1410, 330, "factures globales\net simulation"),
        (1800, 330, "facture sommaire\net simulation"),
    ]
    for x, y, text in labels:
        multiline(draw, (x, y), text, F_TINY, INK, anchor="mm")

    # External components
    component(draw, (70, 1010, 410, 1280), "PostgreSQL", "Données métier\ncomptes, contrats,\nlignes et factures", GRAY)
    component(draw, (500, 1010, 840, 1280), "Stockage média", "PDF sources\net factures publiées", GOLD, GOLD_BORDER)
    component(draw, (930, 1000, 1270, 1290), "Garnet + Celery", "Cache, broker et\ntraitements PDF", BLUE_LIGHT, BLUE_DARK)
    component(draw, (1360, 1010, 1690, 1280), "Service SMTP", "Notifications\ne-mail", GREEN, GREEN_BORDER)
    component(draw, (1780, 980, 2140, 1310), "Système de facturation\nMoov Africa", "Données de consommation\net de facturation", GRAY)

    # System-to-component arrows
    arrow(draw, (650, 750), (240, 1010), BLUE_DARK, 4)
    arrow(draw, (850, 750), (670, 1010), BLUE_DARK, 4)
    arrow(draw, (1070, 750), (1100, 1000), BLUE_DARK, 4)
    arrow(draw, (1320, 750), (1515, 1010), BLUE_DARK, 4)
    arrow(draw, (1550, 750), (1960, 980), BLUE_DARK, 4)
    multiline(draw, (375, 875), "lecture / écriture\ndes données", F_TINY, INK, anchor="mm")
    multiline(draw, (690, 875), "déposer / récupérer\nles PDF", F_TINY, INK, anchor="mm")
    multiline(draw, (1100, 875), "tâches PDF\nen arrière-plan", F_TINY, INK, anchor="mm")
    multiline(draw, (1460, 875), "notifications\npar e-mail", F_TINY, INK, anchor="mm")
    multiline(draw, (1800, 875), "consommation et\nfacturation", F_TINY, INK, anchor="mm")

    # Celery data flow to storage and database
    arrow(draw, (1000, 1145), (840, 1145), BLUE_DARK, 3)
    arrow(draw, (1120, 1000), (1120, 750), BLUE_DARK, 3)
    arrow(draw, (1040, 1000), (260, 1280), BLUE_DARK, 3)

    # Footer note
    multiline(draw, (W / 2, 1430), "Les composants techniques assurent la persistance, le stockage des fichiers,\nles traitements asynchrones et l'envoi des notifications.", F_SMALL, "#555555", anchor="mm")
    image.save(PNG, "PNG", optimize=True)

    # Basic SVG export by embedding the PNG as a portable image.
    import base64
    data = base64.b64encode(PNG.read_bytes()).decode("ascii")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><image width="{W}" height="{H}" href="data:image/png;base64,{data}"/></svg>'''
    SVG.write_text(svg, encoding="utf-8")
    print(PNG)
    print(SVG)


if __name__ == "__main__":
    main()
