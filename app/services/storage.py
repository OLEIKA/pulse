from pathlib import Path
import shutil
from uuid import uuid4
from fastapi import UploadFile

# Root for storing uploaded MP3 files
UPLOAD_ROOT = Path(__file__).resolve().parent.parent / "static" / "uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)


def save_mp3(file: UploadFile) -> str:
    """Save uploaded MP3 with a unique filename, return stored filename."""
    ext = Path(file.filename).suffix or ".mp3"
    filename = f"{uuid4().hex}{ext}"
    dest = UPLOAD_ROOT / filename
    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return filename


def file_url(filename: str) -> str:
    return f"/static/uploads/{filename}"
