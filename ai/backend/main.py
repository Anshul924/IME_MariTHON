from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import shutil, os, uuid, pathlib

from backend.services.ocr import extract_text
from backend.services.structuring import process_line, export_json, export_csv
from backend.services.summarizer import generate_summary

app = FastAPI(title="SoF Event Extractor API", version="1.0.0")

# CORS (open by default; restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "backend/data/uploads"
OUT_DIR = "backend/data"
pathlib.Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/upload-sof")
async def upload_sof(file: UploadFile = File(...)):
    # Save upload
    file_id = str(uuid.uuid4())
    ext = pathlib.Path(file.filename).suffix.lower() or ".pdf"
    filepath = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1) OCR / parsing → plain text
    text = extract_text(filepath)

    # 2) Process line by line into structured events
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    structured = [process_line(ln) for ln in lines]

    # 3) Summary + metrics
    summary = generate_summary(structured)

    # 4) Persist JSON/CSV
    json_path = export_json(structured, file_id)
    csv_path = export_csv(structured, file_id)

    return {
        "file_id": file_id,
        "events": structured,
        "summary": summary,
        "downloads": {
            "json": f"/sof/{file_id}/download/json",
            "csv": f"/sof/{file_id}/download/csv"
        }
    }

@app.get("/sof/{file_id}/download/json")
async def download_json(file_id: str):
    path = os.path.join(OUT_DIR, f"{file_id}.json")
    if not os.path.exists(path):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(path, media_type="application/json", filename=f"{file_id}.json")

@app.get("/sof/{file_id}/download/csv")
async def download_csv(file_id: str):
    path = os.path.join(OUT_DIR, f"{file_id}.csv")
    if not os.path.exists(path):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(path, media_type="text/csv", filename=f"{file_id}.csv")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
