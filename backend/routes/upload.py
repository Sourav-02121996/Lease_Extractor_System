"""Upload route: accept a lease PDF, process it, store the abstraction."""
import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from db import documents
from processing import process_and_store
from serializers import serialize_doc

logger = logging.getLogger("upload")
router = APIRouter(tags=["upload"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        doc_id = await process_and_store(file.filename, file_bytes)
    except RuntimeError as e:
        # e.g. missing API key — surface a clear backend error
        logger.error("Processing configuration error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected processing error")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {e}")

    from bson import ObjectId
    doc = await documents.find_one({"_id": ObjectId(doc_id)})
    return serialize_doc(doc)
