from pathlib import Path
import re
import pdfplumber

source = Path(r"C:\Users\Benoit\Desktop\bonA4gcjtxutxwjtsxyju - Copie.pdf")
target_dir = Path(__file__).parent
full_text_path = target_dir / "memoire.txt"
summary_path = target_dir / "resume_extraction.txt"

with pdfplumber.open(source) as pdf:
    pages = []
    page_summaries = []
    for number, page in enumerate(pdf.pages, start=1):
        text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
        pages.append(f"\n\n===== PAGE {number} =====\n{text}")
        page_summaries.append(f"PAGE {number}: {len(text)} caractères")

    full_text = "".join(pages)
    headings = []
    for line in full_text.splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip()
        if not cleaned:
            continue
        if (re.match(r"^(PARTIE|CHAPITRE)\b", cleaned, re.I)
                or re.match(r"^\d+(?:\.\d+){0,4}\.?\s+[A-ZÉÈÀÙÂÊÎÔÛÇ][A-ZÉÈÀÙÂÊÎÔÛÇ '\-]{4,}$", cleaned)
                or cleaned.upper() in {"INTRODUCTION GÉNÉRALE", "CONCLUSION GÉNÉRALE", "SOMMAIRE", "RÉSUMÉ", "ABSTRACT"}):
            if cleaned not in headings:
                headings.append(cleaned)

full_text_path.write_text(full_text, encoding="utf-8")
summary_path.write_text(
    f"Pages: {len(pdf.pages)}\n"
    + "\n".join(page_summaries)
    + "\n\nTITRES DÉTECTÉS\n"
    + "\n".join(headings),
    encoding="utf-8",
)

print(f"Pages: {len(pdf.pages)}")
print(f"Texte extrait: {full_text_path}")
print("Titres détectés:")
print("\n".join(headings))
