"""Shared serialization helper for document dicts."""


def serialize_doc(doc: dict, include_text: bool = False) -> dict:
    if not doc:
        return doc
    out = {
        "id": str(doc.get("_id")),
        "file_name": doc.get("file_name", ""),
        "upload_date": doc.get("upload_date", ""),
        "status": doc.get("status", ""),
        "extraction_method": doc.get("extraction_method", ""),
        "text_quality_score": doc.get("text_quality_score", ""),
        "char_count": doc.get("char_count", 0),
        "summary": doc.get("summary", ""),
        "overall_status": doc.get("overall_status", ""),
        "warnings": doc.get("warnings", []),
        "fields": doc.get("fields", []),
    }
    if include_text:
        out["raw_text"] = doc.get("raw_text", "")
    return out
