"""Canonical Phase 1 lease fields and their section grouping."""

# Each tuple: (fieldName, section)
FIELD_DEFINITIONS = [
    ("Landlord / Property Owner Name", "Parties"),
    ("Tenant / Business Name", "Parties"),
    ("Guarantor Name(s)", "Parties"),
    ("Mailing Addresses for all parties", "Contact & Address"),
    ("Contact Information", "Contact & Address"),
    ("Effective Date / Lease Start Date", "Lease Dates"),
    ("Lease End Date", "Lease Dates"),
    ("Lease Length", "Lease Dates"),
    ("Renewal Option Details", "Options & Terms"),
    ("Holdover Terms", "Options & Terms"),
]

FIELD_NAMES = [name for name, _ in FIELD_DEFINITIONS]
SECTION_OF = {name: section for name, section in FIELD_DEFINITIONS}
SECTIONS = ["Parties", "Contact & Address", "Lease Dates", "Options & Terms"]

NOT_FOUND_EVIDENCE = "Not found in extracted text"


def empty_field(field_name: str) -> dict:
    """A field with no extracted value (missing)."""
    return {
        "fieldName": field_name,
        "value": "",
        "confidence": 0,
        "evidence": NOT_FOUND_EVIDENCE,
        "status": "missing",
        "section": SECTION_OF[field_name],
    }


def normalize_fields(ai_fields: list) -> list:
    """Ensure all 10 canonical fields exist exactly once and are well-formed."""
    by_name = {}
    for f in ai_fields or []:
        name = (f.get("fieldName") or "").strip()
        if name in FIELD_NAMES and name not in by_name:
            by_name[name] = f

    result = []
    for name in FIELD_NAMES:
        f = by_name.get(name)
        if not f:
            result.append(empty_field(name))
            continue

        value = (f.get("value") or "").strip()
        try:
            confidence = float(f.get("confidence", 0) or 0)
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))
        evidence = (f.get("evidence") or "").strip()
        status = (f.get("status") or "").strip()

        if not value:
            result.append(empty_field(name))
            continue

        if status not in ("extracted", "missing", "needs_review", "approved"):
            status = "needs_review" if confidence < 0.75 else "extracted"

        if not evidence:
            evidence = "(no evidence snippet provided)"

        result.append({
            "fieldName": name,
            "value": value,
            "confidence": round(confidence, 2),
            "evidence": evidence,
            "status": status,
            "section": SECTION_OF[name],
        })
    return result
