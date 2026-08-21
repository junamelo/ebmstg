from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "docs" / "diagramme_contexte_moov_efactures_illustration.png"
image = Image.open(path).convert("RGB")
draw = ImageDraw.Draw(image)
font_dir = Path(r"C:\Windows\Fonts")


def get_font(size: int, bold: bool = False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(font_dir / name), size)


def centered(text: str, box, size=20, bold=False, fill="#172033", spacing=4):
    x1, y1, x2, y2 = box
    f = get_font(size, bold)
    lines = text.split("\n")
    heights = [draw.textbbox((0, 0), line, font=f)[3] for line in lines]
    total = sum(heights) + spacing * (len(lines) - 1)
    y = y1 + (y2 - y1 - total) / 2
    for line, height in zip(lines, heights):
        width = draw.textbbox((0, 0), line, font=f)[2]
        draw.text((x1 + (x2 - x1 - width) / 2, y), line, font=f, fill=fill)
        y += height + spacing


centered("Architecture de contexte du portail Moov e-Factures", (80, 2, 1584, 38), 24, True, spacing=0)

actor_labels = [
    "Super\nadministrateur",
    "Chef de\nfacturation",
    "Agent de\nfacturation",
    "Commercial",
    "Payeur /\nEmployé",
]
actor_boxes = [(58, 45, 326, 234), (380, 45, 648, 234), (702, 45, 969, 234), (1023, 45, 1290, 234), (1346, 45, 1613, 234)]
for label, box in zip(actor_labels, actor_boxes):
    # Caption band keeps labels readable without covering the faces.
    draw.rectangle((box[0] + 3, box[3] - 58, box[2] - 3, box[3] - 3), fill="white")
    centered(label, (box[0] + 12, box[3] - 56, box[2] - 12, box[3] - 8), 18, True, spacing=1)

centered(
    "MOOV E-FACTURES\nPortail de publication et de consultation\ndes factures clients postpayés",
    (90, 360, 1580, 562), 25, True, fill="#123C80", spacing=8,
)

service_labels = [
    "PostgreSQL\nDonnées métier",
    "Stockage PDF\nBlocs sources et factures publiées",
    "Celery\nTraitement asynchrone",
    "Garnet\nBroker et cache",
    "SMTP\nNotifications e-mail",
]
service_boxes = [(58, 688, 326, 870), (380, 688, 648, 870), (702, 688, 969, 870), (1023, 688, 1290, 870), (1346, 688, 1613, 870)]
for label, box in zip(service_labels, service_boxes):
    draw.rectangle((box[0] + 3, box[1] + 3, box[2] - 3, box[3] - 3), fill="white")
    centered(label, (box[0] + 12, box[1] + 12, box[2] - 12, box[3] - 12), 17, True, spacing=7)

image.save(path, optimize=True)
print(path)
