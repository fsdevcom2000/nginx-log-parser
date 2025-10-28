# config.py
from pathlib import Path

BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"txt", "log", "json", "jsonl", "gz"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB