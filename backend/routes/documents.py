"""Document routes: list, get, save draft (corrections), approve."""
import logging
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db import documents
from serializers import serialize_doc

logger = logging.getLogger("documents")
router = APIRouter(prefix="/api", tags=["documents"])


class FieldUpdate(BaseModel):
    fieldName: str
    value: Optional[str] = ""
    confidence: Optional[float] = None
    evidence: Optional[str] = None
    status: Optional[str] = None
    section: Optional[str] = None


class SaveDraftBody(BaseModel):
    fields: List[FieldUpdate]


def _oid(document_id: str) -> ObjectId:
    try:
        return ObjectId(document_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document id.")


@router.get("/documents")
async def list_documents():
    docs = await documents.find().sort("upload_date", -1).to_list(length=500)
    return [serialize_doc(d) for d in docs]


@router.get("/documents/stats")
async def document_stats():
    all_docs = await documents.find().to_list(length=1000)
    total = len(all_docs)
    processed = sum(1 for d in all_docs if d.get("status") in ("processed", "approved", "needs_review"))
    needs_review = sum(1 for d in all_docs if d.get("status") == "needs_review")
    approved = sum(1 for d in all_docs if d.get("status") == "approved")
    return {
        "total": total,
        "processed": processed,
        "needs_review": needs_review,
        "approved": approved,
    }


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    doc = await documents.find_one({"_id": _oid(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return serialize_doc(doc, include_text=True)


def _merge_fields(existing: list, updates: List[FieldUpdate]) -> list:
    update_map = {u.fieldName: u for u in updates}
    merged = []
    for f in existing:
        u = update_map.get(f["fieldName"])
        if not u:
            merged.append(f)
            continue
        new_value = (u.value or "").strip()
        f = dict(f)
        f["value"] = new_value
        if u.status:
            f["status"] = u.status
        elif not new_value:
            f["status"] = "missing"
        elif f["status"] == "missing":
            f["status"] = "needs_review"
        if u.confidence is not None:
            f["confidence"] = max(0.0, min(1.0, float(u.confidence)))
        if u.evidence is not None:
            f["evidence"] = u.evidence
        if not new_value and f["status"] == "missing":
            f["confidence"] = 0
            if not (u.evidence and u.evidence.strip()):
                f["evidence"] = "Not found in extracted text"
        merged.append(f)
    return merged


@router.put("/documents/{document_id}/draft")
async def save_draft(document_id: str, body: SaveDraftBody):
    doc = await documents.find_one({"_id": _oid(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if doc.get("status") == "approved":
        raise HTTPException(status_code=400, detail="Approved records cannot be edited.")

    merged = _merge_fields(doc.get("fields", []), body.fields)
    await documents.update_one(
        {"_id": _oid(document_id)},
        {"$set": {"fields": merged}},
    )
    updated = await documents.find_one({"_id": _oid(document_id)})
    return serialize_doc(updated, include_text=True)


@router.post("/documents/{document_id}/approve")
async def approve_document(document_id: str, body: Optional[SaveDraftBody] = None):
    doc = await documents.find_one({"_id": _oid(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    fields = doc.get("fields", [])
    if body and body.fields:
        fields = _merge_fields(fields, body.fields)

    # promote non-missing fields to approved
    for f in fields:
        if f.get("value") and f.get("status") != "missing":
            f["status"] = "approved"

    await documents.update_one(
        {"_id": _oid(document_id)},
        {"$set": {"status": "approved", "fields": fields}},
    )
    updated = await documents.find_one({"_id": _oid(document_id)})
    return serialize_doc(updated, include_text=True)
