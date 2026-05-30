"""Seed realistic sample lease abstraction records for demo purposes.

Run: python seed.py   (from /app/backend)
Idempotent: clears and reseeds the demo dataset.
"""
import asyncio
from datetime import datetime, timedelta, timezone

from db import documents
from fields import FIELD_NAMES, SECTION_OF, empty_field


def f(name, value, confidence, evidence, status):
    return {
        "fieldName": name,
        "value": value,
        "confidence": confidence,
        "evidence": evidence,
        "status": status,
        "section": SECTION_OF[name],
    }


def iso(days_ago):
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


def full_fields(values):
    """values: dict fieldName -> (value, confidence, evidence, status). Missing => empty."""
    out = []
    for name in FIELD_NAMES:
        if name in values:
            v, c, e, s = values[name]
            out.append(f(name, v, c, e, s))
        else:
            out.append(empty_field(name))
    return out


SAMPLES = [
    {
        "file_name": "Maple Plaza Retail Lease.pdf",
        "upload_date": iso(12),
        "status": "approved",
        "extraction_method": "text_pdf",
        "text_quality_score": "high",
        "char_count": 8420,
        "summary": "Retail lease between Maple Plaza Holdings LLC and Brewline Coffee Co. for a 5-year term commencing January 1, 2024, with one 5-year renewal option.",
        "overall_status": "processed",
        "warnings": [],
        "values": {
            "Landlord / Property Owner Name": ("Maple Plaza Holdings LLC", 0.97, "\"Landlord: Maple Plaza Holdings LLC, a Delaware limited liability company\"", "approved"),
            "Tenant / Business Name": ("Brewline Coffee Co.", 0.96, "\"Tenant: Brewline Coffee Co., an Oregon corporation\"", "approved"),
            "Guarantor Name(s)": ("Daniel R. Whitmore", 0.9, "\"personally guaranteed by Daniel R. Whitmore\"", "approved"),
            "Mailing Addresses for all parties": ("Landlord: 100 Commerce Way, Portland, OR 97201; Tenant: 455 Maple Plaza, Suite 5, Portland, OR 97201", 0.92, "\"notices shall be sent to 100 Commerce Way... and to the Premises at 455 Maple Plaza, Suite 5\"", "approved"),
            "Contact Information": ("Phone: (503) 555-0192; Email: leasing@mapleplaza.com", 0.88, "\"Landlord contact: (503) 555-0192, leasing@mapleplaza.com\"", "approved"),
            "Effective Date / Lease Start Date": ("January 1, 2024", 0.98, "\"Commencement Date: January 1, 2024\"", "approved"),
            "Lease End Date": ("December 31, 2028", 0.97, "\"expiring December 31, 2028\"", "approved"),
            "Lease Length": ("5 years (60 months)", 0.97, "\"for a term of five (5) years\"", "approved"),
            "Renewal Option Details": ("One (1) option to renew for an additional 5 years at fair market rent, with 6 months written notice.", 0.9, "\"Tenant shall have one option to extend for five (5) years\"", "approved"),
            "Holdover Terms": ("Holdover rent equal to 150% of the then-current base rent on a month-to-month basis.", 0.91, "\"holdover... 150% of the Base Rent\"", "approved"),
        },
    },
    {
        "file_name": "Downtown Office Suite 400.pdf",
        "upload_date": iso(8),
        "status": "needs_review",
        "extraction_method": "text_pdf",
        "text_quality_score": "high",
        "char_count": 6110,
        "summary": "Commercial office lease for Suite 400 between Harbor Point Properties and Verdant Analytics Inc. Renewal and holdover terms are ambiguous and require review.",
        "overall_status": "needs_review",
        "warnings": [],
        "values": {
            "Landlord / Property Owner Name": ("Harbor Point Properties, L.P.", 0.95, "\"Landlord: Harbor Point Properties, L.P.\"", "extracted"),
            "Tenant / Business Name": ("Verdant Analytics Inc.", 0.94, "\"Tenant: Verdant Analytics Inc.\"", "extracted"),
            "Mailing Addresses for all parties": ("Landlord: 200 Harbor Blvd, Seattle, WA 98101; Tenant: Suite 400, 200 Harbor Blvd, Seattle, WA 98101", 0.85, "\"All notices to 200 Harbor Blvd...\"", "extracted"),
            "Contact Information": ("Email: admin@harborpoint.com", 0.6, "\"admin@harborpoint.com\"", "needs_review"),
            "Effective Date / Lease Start Date": ("March 15, 2024", 0.93, "\"effective as of March 15, 2024\"", "extracted"),
            "Lease End Date": ("March 14, 2027", 0.9, "\"through March 14, 2027\"", "extracted"),
            "Lease Length": ("3 years (36 months)", 0.92, "\"a term of thirty-six (36) months\"", "extracted"),
            "Renewal Option Details": ("Renewal terms referenced but specific notice period unclear in document.", 0.55, "\"Tenant may renew subject to Section 14\"", "needs_review"),
        },
    },
    {
        "file_name": "Riverside Warehouse Lease.pdf",
        "upload_date": iso(20),
        "status": "approved",
        "extraction_method": "text_pdf",
        "text_quality_score": "high",
        "char_count": 9300,
        "summary": "Industrial warehouse lease between Riverside Logistics Trust and Northgate Distribution LLC for a 7-year term with two renewal options.",
        "overall_status": "processed",
        "warnings": [],
        "values": {
            "Landlord / Property Owner Name": ("Riverside Logistics Trust", 0.98, "\"Landlord: Riverside Logistics Trust\"", "approved"),
            "Tenant / Business Name": ("Northgate Distribution LLC", 0.97, "\"Tenant: Northgate Distribution LLC\"", "approved"),
            "Guarantor Name(s)": ("Northgate Holdings Inc.", 0.93, "\"Guaranty by Northgate Holdings Inc.\"", "approved"),
            "Mailing Addresses for all parties": ("Landlord: 12 River Rd, Sacramento, CA 95814; Tenant: 800 Industrial Pkwy, Sacramento, CA 95826", 0.94, "\"notices to 12 River Rd... and 800 Industrial Pkwy\"", "approved"),
            "Contact Information": ("Phone: (916) 555-0144; Email: ops@riversidelogistics.com", 0.9, "\"(916) 555-0144 / ops@riversidelogistics.com\"", "approved"),
            "Effective Date / Lease Start Date": ("June 1, 2023", 0.98, "\"Commencement: June 1, 2023\"", "approved"),
            "Lease End Date": ("May 31, 2030", 0.97, "\"expires May 31, 2030\"", "approved"),
            "Lease Length": ("7 years (84 months)", 0.97, "\"seven (7) year term\"", "approved"),
            "Renewal Option Details": ("Two (2) consecutive options to renew for 5 years each at 95% of fair market rent.", 0.92, "\"two options to renew for five (5) years each\"", "approved"),
            "Holdover Terms": ("Month-to-month holdover at 125% of base rent.", 0.9, "\"holdover at one hundred twenty-five percent (125%)\"", "approved"),
        },
    },
    {
        "file_name": "Sunset Strip Mall Unit 12.pdf",
        "upload_date": iso(3),
        "status": "needs_review",
        "extraction_method": "ocr",
        "text_quality_score": "low",
        "char_count": 740,
        "summary": "Scanned retail lease processed via OCR. Text quality is low; extracted values should be verified carefully.",
        "overall_status": "needs_review",
        "warnings": ["OCR was used. Please review extracted values carefully."],
        "values": {
            "Landlord / Property Owner Name": ("Sunset Strip Mall Associates", 0.62, "\"Landlord Sunset Strip Mall Assoc...\" (OCR)", "needs_review"),
            "Tenant / Business Name": ("Bella Nails & Spa", 0.58, "\"Tenant Bella Nails Spa\" (OCR)", "needs_review"),
            "Effective Date / Lease Start Date": ("September 1, 2024", 0.5, "\"commenc... Sept 1 2024\" (OCR, partial)", "needs_review"),
            "Lease Length": ("3 years", 0.45, "\"term of 3 years\" (OCR)", "needs_review"),
        },
    },
    {
        "file_name": "Greenfield Industrial Park.pdf",
        "upload_date": iso(5),
        "status": "processed",
        "extraction_method": "text_pdf",
        "text_quality_score": "medium",
        "char_count": 2400,
        "summary": "Ground lease between Greenfield Park Authority and Apex Manufacturing Co. for a 10-year term. All core fields extracted with good confidence.",
        "overall_status": "processed",
        "warnings": [],
        "values": {
            "Landlord / Property Owner Name": ("Greenfield Park Authority", 0.95, "\"Landlord: Greenfield Park Authority\"", "extracted"),
            "Tenant / Business Name": ("Apex Manufacturing Co.", 0.94, "\"Tenant: Apex Manufacturing Co.\"", "extracted"),
            "Mailing Addresses for all parties": ("Landlord: 1 Greenfield Way, Columbus, OH 43215; Tenant: 45 Apex Dr, Columbus, OH 43219", 0.9, "\"notices to 1 Greenfield Way... 45 Apex Dr\"", "extracted"),
            "Contact Information": ("Phone: (614) 555-0178", 0.82, "\"(614) 555-0178\"", "extracted"),
            "Effective Date / Lease Start Date": ("February 1, 2024", 0.93, "\"effective February 1, 2024\"", "extracted"),
            "Lease End Date": ("January 31, 2034", 0.92, "\"through January 31, 2034\"", "extracted"),
            "Lease Length": ("10 years (120 months)", 0.93, "\"ten (10) year term\"", "extracted"),
            "Renewal Option Details": ("One 10-year renewal option at market rent.", 0.8, "\"option to renew for ten (10) years\"", "extracted"),
            "Holdover Terms": ("Holdover at 150% base rent.", 0.81, "\"holdover at 150%\"", "extracted"),
        },
    },
    {
        "file_name": "Scanned-Lease-Illegible.pdf",
        "upload_date": iso(1),
        "status": "needs_review",
        "extraction_method": "failed",
        "text_quality_score": "low",
        "char_count": 0,
        "summary": "Text could not be extracted from this document. Manual review required.",
        "overall_status": "failed",
        "warnings": ["Text extraction failed. This document needs manual review."],
        "values": {},
    },
]


async def main():
    await documents.delete_many({})
    docs = []
    for s in SAMPLES:
        doc = {k: v for k, v in s.items() if k != "values"}
        doc["fields"] = full_fields(s["values"])
        doc["raw_text"] = s.get("summary", "")
        docs.append(doc)
    result = await documents.insert_many(docs)
    print(f"Seeded {len(result.inserted_ids)} documents.")


if __name__ == "__main__":
    asyncio.run(main())
