"""Core document processing pipeline shared by upload route and seeding."""
import logging

from db import documents, now_iso
from fields import normalize_fields
from services.ai_extraction import extract_fields
from services.extraction import extract_document_text

logger = logging.getLogger("processing")

OCR_WARNING = "OCR was used. Please review extracted values carefully."
FAILED_WARNING = "Text extraction failed. This document needs manual review."


def _derive_status(extraction_method: str, ai_overall: str, fields: list) -> str:
    if extraction_method == "failed":
        return "needs_review"
    if ai_overall == "failed":
        return "needs_review"
    for f in fields:
        if f["status"] in ("missing", "needs_review"):
            return "needs_review"
        if float(f.get("confidence", 0) or 0) < 0.75:
            return "needs_review"
    return "processed"


async def process_and_store(file_name: str, file_bytes: bytes) -> str:
    """Run extraction + AI, persist a document, return its id (str)."""
    ext = extract_document_text(file_bytes)

    warnings = []
    if ext["extraction_method"] == "ocr":
        warnings.append(OCR_WARNING)
    if ext["extraction_method"] == "failed":
        warnings.append(FAILED_WARNING)

    ai = await extract_fields(ext["text"])
    fields = normalize_fields(ai.get("fields", []))

    status = _derive_status(ext["extraction_method"], ai.get("overallStatus", ""), fields)

    summary = ai.get("summary") or ""
    if ext["extraction_method"] == "failed" and not summary:
        summary = "Text could not be extracted from this document. Manual review required."

    doc = {
        "file_name": file_name,
        "upload_date": now_iso(),
        "status": status,
        "extraction_method": ext["extraction_method"],
        "text_quality_score": ext["text_quality_score"],
        "char_count": ext["char_count"],
        "summary": summary,
        "raw_text": ext["text"],
        "overall_status": ai.get("overallStatus", "needs_review"),
        "warnings": warnings,
        "fields": fields,
    }

    result = await documents.insert_one(doc)
    logger.info("Stored document %s (method=%s, status=%s)", result.inserted_id, ext["extraction_method"], status)
    return str(result.inserted_id)
