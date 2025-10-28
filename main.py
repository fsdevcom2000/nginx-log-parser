# main.py
from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
from pathlib import Path
from parsers import parse_log_file
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE

app = FastAPI(
    title="Log Parser",
    description="Парсер логов NGINX/Apache",
    version="1.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    if not allowed_file(file.filename):
        raise HTTPException(400, detail="Недопустимый формат файла")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, detail="Файл слишком большой (>50MB)")

    filepath = Path(UPLOAD_FOLDER) / file.filename
    with open(filepath, "wb") as f:
        f.write(contents)

    try:
        logs = parse_log_file(str(filepath))
    except Exception as e:
        raise HTTPException(500, detail=f"Ошибка парсинга: {e}")

    limit = 100
    display_logs = logs[:limit]

    # return HTML-template
    return templates.TemplateResponse(
        "logs.html",
        {
            "request": request,
            "logs": display_logs,
            "total": len(logs),
            "filename": file.filename,
            "truncated": len(logs) > 100,
            "limit": limit,
            "page": 1,
            "level": "",   # blank default filter
            "q": ""        # blank search
        }
    )


@app.get("/api/filter")
async def filter_logs(
    request: Request,
    level: str = "",
    q: str = "",
    page: int = 1,
    limit: int = 100
):
    upload_dir = Path(UPLOAD_FOLDER)
    files = list(upload_dir.glob("*.log")) + list(upload_dir.glob("*.txt"))
    if not files:
        return HTMLResponse("")

    latest_file = max(files, key=lambda p: p.stat().st_mtime)
    logs = parse_log_file(str(latest_file))

    # filtering
    filtered = logs
    if level:
        filtered = [l for l in filtered if l.get("level") == level]
    if q:
        q_lower = q.lower()
        filtered = [
            l for l in filtered
            if q_lower in str(l.get("ip", "")).lower()
            or q_lower in str(l.get("request", "")).lower()
            or q_lower in str(l.get("raw", "")).lower()
        ]

    # pagination
    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit
    page_logs = filtered[start:end]

    # return to template
    return templates.TemplateResponse(
        "logs_table.html",
        {
            "request": request,
            "logs": page_logs,
            "total": total,
            "page": page,
            "limit": limit,
            "level": level,
            "q": q
        }
    )


@app.get("/logs", response_class=HTMLResponse)
async def view_logs(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})

# Swagger: http://localhost:8000/docs