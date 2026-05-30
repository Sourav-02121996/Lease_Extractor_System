"""PDF text extraction + OCR fallback (modular).

Flow:
  1. Try normal PDF text extraction (pdfplumber).
  2. If extracted text < 500 chars -> run OCR fallback (Tesseract).
  3. If both fail -> mark as failed.

OCR is kept modular so it can later be swapped for Azure Document Intelligence.
"""
import io
import logging

logger = logging.getLogger("extraction")

OCR_THRESHOLD = 500  # chars below which we attempt OCR


def extract_text_pdf(file_bytes: bytes) -> str:
    """Normal embedded-text extraction using pdfplumber."""
    try:
        import pdfplumber

        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts).strip()
    except Exception as e:  # bad/corrupt PDF should not crash the app
        logger.warning("pdfplumber extraction failed: %s", e)
        return ""


def extract_text_ocr(file_bytes: bytes) -> str:
    """OCR fallback using Tesseract. Modular: replace with Azure Doc Intelligence later.

    Returns extracted text, or "" if OCR is unavailable / fails.
    """
    try:
        import pytesseract  # noqa
        from pdf2image import convert_from_bytes  # noqa
    except Exception as e:
        logger.warning("OCR libraries not available: %s", e)
        return ""

    try:
        from pdf2image import convert_from_bytes
        import pytesseract

        images = convert_from_bytes(file_bytes, dpi=200)
        text_parts = []
        for img in images:
            text_parts.append(pytesseract.image_to_string(img) or "")
        return "\n".join(text_parts).strip()
    except Exception as e:
        logger.warning("OCR extraction failed: %s", e)
        return ""


def quality_score(text: str) -> str:
    n = len(text or "")
    if n > 3000:
        return "high"
    if n >= 1000:
        return "medium"
    return "low"


def extract_document_text(file_bytes: bytes) -> dict:
    """Run the full extraction pipeline.

    Returns dict: { text, extraction_method, text_quality_score, char_count }
    extraction_method in {text_pdf, ocr, failed}
    """
    text = extract_text_pdf(file_bytes)
    method = "text_pdf"

    if len(text) < OCR_THRESHOLD:
        ocr_text = extract_text_ocr(file_bytes)
        if len(ocr_text) > len(text):
            text = ocr_text
            method = "ocr"

    if not text.strip():
        method = "failed"

    return {
        "text": text,
        "extraction_method": method,
        "text_quality_score": quality_score(text),
        "char_count": len(text),
    }
