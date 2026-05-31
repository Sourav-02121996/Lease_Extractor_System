"""Spreadsheet export service. Exports approved lease abstraction records only."""
import csv
import io

# Spreadsheet column order per spec
CSV_COLUMNS = [
    "File Name",
    "Upload Date",
    "Status",
    "Extraction Method",
    "Landlord / Property Owner Name",
    "Tenant / Business Name",
    "Guarantor Name(s)",
    "Mailing Addresses for all parties",
    "Contact Information",
    "Effective Date / Lease Start Date",
    "Lease End Date",
    "Lease Length",
    "Renewal Option Details",
    "Holdover Terms",
]


def _field_value_map(doc: dict) -> dict:
    return {f.get("fieldName"): (f.get("value") or "") for f in doc.get("fields", [])}


def build_rows(docs: list) -> list[list[str]]:
    rows = []
    for doc in docs:
        values = _field_value_map(doc)
        row = [
            doc.get("file_name", ""),
            doc.get("upload_date", ""),
            doc.get("status", ""),
            doc.get("extraction_method", ""),
        ]
        # Remaining columns are the 10 extracted fields, in spreadsheet order.
        for col in CSV_COLUMNS[4:]:
            row.append(values.get(col, ""))
        rows.append(row)
    return rows


def build_csv(docs: list) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_COLUMNS)
    for row in build_rows(docs):
        writer.writerow(row)

    return output.getvalue()
