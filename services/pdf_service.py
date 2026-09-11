import io
import fitz
from pypdf import PdfReader


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract selectable text from a PDF."""
    text_parts = []
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
    except Exception:
        pass
    return "\n\n".join(text_parts).strip()


def get_pdf_page_count(pdf_bytes: bytes) -> int:
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        count = len(doc)
        doc.close()
        return count
    except Exception:
        return 0


def render_pdf_pages(pdf_bytes: bytes, max_pages: int = 30, scale: float = 1.5):
    """Render up to max_pages as JPEG bytes for vision/OCR."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    try:
        for index, page in enumerate(doc):
            if index >= max_pages:
                break
            pix = page.get_pixmap(
                matrix=fitz.Matrix(scale, scale),
                alpha=False,
            )
            images.append(pix.tobytes("jpeg"))
    finally:
        doc.close()
    return images
