# PRD — Lease Abstraction Assistant

## Original Problem Statement
Internal web app for a real estate company: upload lease PDFs, extract 10 core lease abstraction
fields with Gemini API, human reviewer verifies/corrects in an editable table, approves the
record, and exports approved records as CSV. AI layer modular so Claude can replace Gemini later.
OCR fallback (Tesseract) kept modular for future Azure Document Intelligence.

## Tech / Architecture
- Backend: FastAPI (modular routes + services), MongoDB (motor). AI via Google's official
  `google-genai` SDK (`gemini-2.5-flash`) using `GEMINI_API_KEY`.
- Frontend: React (CRA) + Tailwind, react-router, axios, lucide-react. Swiss/high-contrast light
  theme (Chivo + IBM Plex Sans).
- Services: extraction (pdfplumber + OCR fallback), ai_extraction (gemini active / claude
  placeholder), CSV and Excel export. Pipeline in processing.py.
- Data: single `documents` collection with embedded `fields[]` (10 canonical fields).

## User Personas
- Lease abstraction reviewer (verifies & approves AI-extracted lease data).

## Core Requirements (static)
- 10 Phase 1 fields, 4 review sections (Parties, Contact & Address, Lease Dates, Options & Terms).
- Statuses: extracted, missing, needs_review, approved, failed.
- Never invent values; missing => blank, confidence 0, evidence "Not found in extracted text".
- OCR fallback when text < 500 chars; quality high/medium/low by char count.
- Approved-only CSV and Excel export with 14 columns.
- All AI/API keys backend-only.

## Implemented (2026-01)
- [x] Backend: upload, documents (list/stats/get/draft/approve), export CSV and Excel, health.
- [x] Gemini extraction verified end-to-end on a real text PDF (all 10 fields correct).
- [x] PDF text extraction + modular OCR fallback (graceful when Tesseract absent).
- [x] Modular AI layer with Claude placeholder (AI_PROVIDER switch).
- [x] Frontend: Dashboard+Upload, History, Review (editable, banners, needs-review panel), Export.
- [x] 6 seeded demo docs (2 approved, 3 needs_review, 1 processed).
- [x] README.md (full). Testing: 15/15 backend + frontend smoke = 100% pass.

## Backlog (prioritized)
- P1: Install Tesseract + pdf2image to enable real OCR for scanned PDFs.
- P1: Per-document delete / re-process action.
- P2: PDF preview pane alongside extraction table on Review page.
- P2: Filter/search on Document History; pagination for large volumes.
- P2: Wire Claude provider once ANTHROPIC_API_KEY is available; Azure Doc Intelligence OCR.
- P2: Auth (currently none) if exposed beyond internal network.

## Next Tasks
- Awaiting user feedback / next feature request.
