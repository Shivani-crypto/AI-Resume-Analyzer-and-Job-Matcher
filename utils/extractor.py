import pdfplumber
import docx
import pytesseract
from PIL import Image
import os
import re

# Set Tesseract path (change if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# -----------------------------
# 1. EXTRACT TEXT FROM FILE
# -----------------------------
def extract_raw_text(filepath):
    if not os.path.exists(filepath):
        return "File not found"

    text = ""

    # PDF
    if filepath.lower().endswith(".pdf"):
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                content = page.extract_text(x_tolerance=2, y_tolerance=2)
                if content:
                    text += content + "\n"

    # DOCX
    elif filepath.lower().endswith(".docx"):
        doc = docx.Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"

    # IMAGE (OCR)
    elif filepath.lower().endswith((".png", ".jpg", ".jpeg")):
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)

    else:
        return "Unsupported file format"

    return text


# -----------------------------
# 2. CLEAN TEXT
# -----------------------------
def clean_text(text):
    # Fix broken emails (gmail. com → gmail.com)
    text = re.sub(r'\s*\.\s*', '.', text)

    # Add space between words (FullStack → Full Stack)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    # Add space after comma
    text = re.sub(r',([A-Za-z])', r', \1', text)

    # Normalize spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# -----------------------------
# 3. FORMAT INTO RESUME STYLE
# -----------------------------
def format_resume(text):
    # Add section breaks
    sections = [
        "PROFESSIONAL SUMMARY",
        "EXPERIENCE",
        "EDUCATION",
        "TECHNICAL SKILLS",
        "PROJECTS"
    ]

    for sec in sections:
        text = re.sub(sec, f"\n\n{sec}\n", text, flags=re.IGNORECASE)

    # Format bullets
    text = text.replace("•", "\n•")

    # Improve spacing
    text = re.sub(r'\n\s+', '\n', text)

    return text.strip()


# -----------------------------
# 4. MAIN FUNCTION
# -----------------------------
def extract_text_from_file(filepath):
    raw_text = extract_raw_text(filepath)

    if raw_text in ["File not found", "Unsupported file format"]:
        return raw_text

    cleaned = clean_text(raw_text)

    formatted = format_resume(cleaned)

    return formatted


# -----------------------------
# 5. TEST (Run directly)
# -----------------------------
if __name__ == "__main__":
    file_path = "sample_resume.pdf"  # change file name

    result = extract_text_from_file(file_path)

    print("\n===== CLEAN FORMATTED RESUME =====\n")
    print(result)