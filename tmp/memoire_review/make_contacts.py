from pathlib import Path
from PIL import Image, ImageDraw

input_dir = Path(__file__).parent / "renders"
files = sorted(input_dir.glob("page_*.png"))

for group_index, start in enumerate(range(0, len(files), 8), start=1):
    group = files[start:start + 8]
    sheet = Image.new("RGB", (920, 680), "white")
    draw = ImageDraw.Draw(sheet)
    for index, file in enumerate(group):
        x = (index % 4) * 230
        y = (index // 4) * 340
        image = Image.open(file).convert("RGB")
        image.thumbnail((220, 311))
        sheet.paste(image, (x, y + 24))
        draw.text((x, y + 4), file.stem, fill="black")
    sheet.save(Path(__file__).parent / f"contact_{group_index}.png")
