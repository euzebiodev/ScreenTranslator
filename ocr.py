"""Extração de texto de imagens via Tesseract OCR."""
import pytesseract

import config

pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD


def extract_text(image, lang="eng"):
    """Recebe uma PIL.Image e retorna o texto reconhecido (limpo)."""
    raw = pytesseract.image_to_string(image, lang=lang)
    lines = [line.strip() for line in raw.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines).strip()
