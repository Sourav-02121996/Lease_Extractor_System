# Lease Abstraction Assistant

An internal web app for a real estate company to **upload lease PDFs, extract the core lease
abstraction fields with AI (Gemini), review & correct the results, approve the final record, and
export approved records as CSV or Excel.**

---

## What the app does

1. Upload a commercial lease PDF.
2. The backend stores the document and extracts its text (with OCR fallback for scans).
3. The extracted text is sent to the **Gemini Flash** model, which returns strict JSON for the
   **10 Phase 1 lease fields**.
4. A human reviewer verifies/corrects every field in an editable, grouped table.
5. The reviewer **saves a draft** or **approves** the record.
6. **Approved records only** can be exported as CSV or Excel (one row per document).

### The 10 Phase 1 fields
| # | Field | Section |
|---|-------|---------|
| 1 | Landlord / Property Owner Name | Parties |
| 2 | Tenant / Business Name | Parties |
| 3 | Guarantor Name(s) | Parties |
| 4 | Mailing Addresses for all parties | Contact & Address |
| 5 | Contact Information (phone & email) | Contact & Address |
| 6 | Effective Date / Lease Start Date | Lease Dates |
| 7 | Lease End Date | Lease Dates |
| 8 | Lease Length | Lease Dates |
| 9 | Renewal Option Details | Options & Terms |
| 10 | Holdover Terms | Options & Terms |

---

## Pages
- **Upload & Dashboard** — summary cards (total / processed / needs review / approved),
  drag-and-drop PDF upload, recent uploads table.
- **Document History** — all uploaded documents with status, extraction method and text quality.
- **Document Review** — metadata, summary, warning banners, editable extraction table grouped
  into 4 sections, a **Needs Review** panel, and action buttons (Save Draft, Approve Record,
  Back to History, Export Approved Data).
- **Export Data** — download approved lease records as CSV or Excel.

---

## Architecture

```
backend/
  server.py                 FastAPI app (mounts routers, /api/health)
  db.py                     Mongo connection + ObjectId helpers
  fields.py                 10 canonical fields, sections, normalize_fields()
  processing.py             upload pipeline: extract text -> AI -> persist
  serializers.py            Mongo doc -> JSON (no ObjectId leakage)
  seed.py                   seeds 6 realistic demo documents
  routes/
    upload.py               POST /api/upload
    documents.py            list / stats / get / draft / approve
    export.py               GET /api/export/approved (CSV) and /excel (XLSX)
  services/
    extraction.py           pdfplumber text extraction + OCR fallback (modular)
    ai_extraction.py        Gemini (active) + Claude placeholder (modular)
    csv_export.py           builds the shared 14-column export rows and CSV
    excel_export.py         builds the XLSX workbook
frontend/
  src/pages/                Dashboard, History, Review, ExportData
  src/components/           Layout (sidebar+header), ui (badges/buttons/etc.)
  src/lib/api.js            axios client (uses REACT_APP_BACKEND_URL)
```

### Data model (MongoDB, `documents` collection)
- `file_name`, `upload_date`, `status`, `extraction_method`, `text_quality_score`,
  `char_count`, `summary`, `raw_text`, `overall_status`, `warnings[]`
- `fields[]` — embedded array, one per canonical field:
  `{ fieldName, value, confidence, evidence, status, section }`

---

## Running locally

The app is pre-wired for the Emergent environment (supervisor-managed). Services:
- Backend: FastAPI on `:8001` (all routes prefixed `/api`)
- Frontend: React (CRA) on `:3000`
- Database: MongoDB

```bash
# Backend deps
pip install -r backend/requirements.txt

# Frontend deps
cd frontend && yarn install

# Seed demo data
cd backend && python seed.py

# Restart services (Emergent)
sudo supervisorctl restart backend frontend
```

Environment variables:
- `backend/.env`: `MONGO_URL`, `DB_NAME`, `AI_PROVIDER=gemini`, `GEMINI_MODEL`,
  `GEMINI_API_KEY`, `ANTHROPIC_API_KEY` (future)
- `frontend/.env`: `REACT_APP_BACKEND_URL`

---

## Upload → Review → Approval → Export flow
1. **Upload** a PDF on the dashboard (drag-drop or click). The app processes it and routes you to
   the Review page.
2. **Review**: edit any value. Each field shows value, confidence, evidence snippet and status.
   Missing fields are **blank** with confidence `0` — the app never invents values.
3. **Save Draft** stores your corrections; **Approve Record** locks the record (read-only) and
   marks it `approved`.
4. **Export Data** → choose CSV or Excel and download. Only approved records are included; one row
   per document with these columns: *File Name, Upload Date, Status, Extraction Method,* and the
   10 lease fields.

---

## How Gemini extraction works
- All AI calls happen **in the backend only** — API keys are never exposed to the frontend.
- `services/ai_extraction.py` builds a strict prompt and calls **Gemini Flash**
  (`gemini-2.5-flash`) via Google's official `google-genai` SDK.
- Prompt rules: strict JSON only, no markdown, no guessing/inventing, use only the lease text,
  include short evidence snippets, and mark unfound fields as `missing`.
- Response is validated against the required schema. If Gemini returns invalid JSON or fails, the
  app does **not crash** — all fields fall back to `missing` and the document is marked
  `needs_review`. Provider, text length and number of fields returned are logged.

### Where to add `GEMINI_API_KEY`
Set it in `backend/.env`:
```
GEMINI_API_KEY=your-key-here
AI_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-flash
```
If `GEMINI_API_KEY` is empty, the backend returns a clear error:
**"Gemini API key is not configured."**

---

## Replacing Gemini with Claude (future)
The AI layer is modular. `services/ai_extraction.py` already contains a `_claude_extract`
placeholder that will:
- read `ANTHROPIC_API_KEY` from the environment,
- call **Claude Sonnet** from the backend,
- send the extracted lease text and request strict JSON,
- reuse the **same JSON schema** as Gemini.

Gemini remains the active provider by default. Claude extraction is not implemented yet and does
not block the app.

---

## Future Azure Document Intelligence OCR
OCR is isolated in `services/extraction.py::extract_text_ocr` (currently Tesseract-based and
optional). It can be swapped for **Azure Document Intelligence** without touching the rest of the
pipeline — the function just needs to return extracted text for the given PDF bytes.

---

## Limitations of OCR and AI extraction
- **OCR**: Tesseract is a basic MVP OCR. Scanned/low-quality PDFs may yield low text quality —
  these documents are flagged with an *"OCR was used. Please review extracted values carefully."*
  banner and routed to `needs_review`. (Tesseract is not installed by default in this build; the
  service degrades gracefully and marks such documents `failed` → `needs_review`.)
- **AI extraction**: The model only uses the provided lease text and will not invent values.
  Ambiguous or unusual lease language can produce `needs_review` items or lower confidence —
  **human review is always required before approval**. Extraction is bounded to the first ~30k
  characters of text per document.
```
```
