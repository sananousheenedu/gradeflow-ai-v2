import io
import re
import fitz
from pypdf import PdfReader


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """
    Extract text from a digital PDF.

    We intentionally do not depend on local Tesseract for the cloud MVP.
    If extraction is weak, app.py can route the PDF to Groq Vision.
    """
    text_parts = []

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
    except Exception:
        pass

    return "\n\n".join(text_parts).strip()


def render_pdf_pages(pdf_bytes: bytes, max_pages: int = 20):
    """
    Render PDF pages as JPEG bytes for Groq Vision.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []

    for index, page in enumerate(doc):
        if index >= max_pages:
            break

        pix = page.get_pixmap(
            matrix=fitz.Matrix(1.5, 1.5),
            alpha=False,
        )

        images.append(pix.tobytes("jpeg"))

    return images
