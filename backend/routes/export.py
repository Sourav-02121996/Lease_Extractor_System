"""Export routes: download approved lease records as CSV or Excel."""
import logging

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response

from db import documents
from services.csv_export import build_csv
from services.excel_export import build_excel

logger = logging.getLogger("export")
router = APIRouter(prefix="/api", tags=["export"])


@router.get("/export/approved")
async def export_approved():
    docs = await documents.find({"status": "approved"}).sort("upload_date", -1).to_list(length=1000)

    if not docs:
        return PlainTextResponse(
            "No approved lease records available for export.",
            status_code=404,
        )

    csv_text = build_csv(docs)
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=approved_leases.csv"},
    )


@router.get("/export/approved/excel")
async def export_approved_excel():
    docs = await documents.find({"status": "approved"}).sort("upload_date", -1).to_list(length=1000)

    if not docs:
        return PlainTextResponse(
            "No approved lease records available for export.",
            status_code=404,
        )

    excel_bytes = build_excel(docs)
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=approved_leases.xlsx"},
    )


@router.get("/export/approved/count")
async def approved_count():
    count = await documents.count_documents({"status": "approved"})
    return {"approved": count}
