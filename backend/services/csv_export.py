"""CSV export service. Exports approved lease abstraction records only."""
import csv
import io

from fields import FIELD_NAMES

# CSV column order per spec
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


def build_csv(docs: list) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_COLUMNS)

    for doc in docs:
        values = _field_value_map(doc)
        row = [
            doc.get("file_name", ""),
            doc.get("upload_date", ""),
            doc.get("status", ""),
            doc.get("extraction_method", ""),
        ]
        # remaining columns are the 10 fields, in CSV order
        for col in CSV_COLUMNS[4:]:
            row.append(values.get(col, ""))
        writer.writerow(row)

    return output.getvalue()
