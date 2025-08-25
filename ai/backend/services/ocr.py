from pathlib import Path
import pdfplumber
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import cv2
import numpy as np

# --- Helper: determine if PDF is digital vs scanned ---
def _looks_scanned(pdf_path: str, sample_pages: int = 2) -> bool:
    try:
        text_chars = 0
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:sample_pages]:
                t = page.extract_text() or ""
                text_chars += len(t.strip())
        return text_chars < 30  # heuristic
    except Exception:
        # If pdfplumber fails (encrypted/unsupported), fall back to OCR
        return True

def _preprocess_for_ocr(pil_img: Image.Image) -> Image.Image:
    img = np.array(pil_img.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # denoise
    gray = cv2.medianBlur(gray, 3)
    # adaptive threshold (robust to uneven illumination)
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 31, 11)
    return Image.fromarray(bw)

def _ocr_pil(pil_img: Image.Image, lang: str = "eng", psm: int = 6) -> str:
    pre = _preprocess_for_ocr(pil_img)
    config = f"--oem 1 --psm {psm}"
    return pytesseract.image_to_string(pre, lang=lang, config=config)

def extract_text(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        # digital vs scanned
        if not _looks_scanned(path):
            text_parts = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts)

        # scanned: convert pages to images and OCR
        pages = convert_from_path(path, dpi=300)
        text = []
        for pg in pages:
            text.append(_ocr_pil(pg))
        return "\n".join(text)

    # If image files are ever uploaded directly
    if ext in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
        pil = Image.open(path)
        return _ocr_pil(pil)

    # As a fallback attempt, try OCR anyway
    try:
        pil = Image.open(path)
        return _ocr_pil(pil)
    except Exception:
        return ""
