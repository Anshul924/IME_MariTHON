# SoF Event Extractor (Backend)

FastAPI service that ingests Statement of Facts (PDF/Word/Images), extracts text (OCR if needed), detects events/times/delays, and returns structured JSON, CSV, and a short summary with KPIs.

## Quickstart

```bash
# 1) Create venv & install requirements
pip install -r backend/requirements.txt

# 2) System deps (outside pip):
# - Tesseract OCR (binary)
# - Poppler (for pdf2image)
# Install via your OS package manager (apt, brew, choco)

# 3) Run API
uvicorn backend.main:app --reload
```

Open http://localhost:8000/docs for Swagger UI.

## Endpoints

- `GET /health`
- `POST /upload-sof` (multipart file) → returns events + summary + download links
- `GET /sof/{file_id}/download/json`
- `GET /sof/{file_id}/download/csv`

## Notes
- If a custom spaCy model is available, place it under `backend/models/sof_event_model/`. Otherwise, the service falls back to keyword rules.
- OCR heuristics: digital PDFs use `pdfplumber`, scanned PDFs use `pdf2image` + Tesseract with OpenCV preprocessing.
