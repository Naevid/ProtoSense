from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings
from app.models.schemas import ProtocolPage


class ProtocolIngestionService:
    async def ingest_upload(self, file: UploadFile) -> tuple[str, str, list[ProtocolPage]]:
        settings = get_settings()
        protocol_id = uuid.uuid4().hex[:12]
        suffix = Path(file.filename or "protocol.pdf").suffix or ".pdf"
        safe_filename = f"{protocol_id}{suffix}"
        destination = settings.upload_dir / safe_filename
        content = await file.read()
        destination.write_bytes(content)
        pages = self.extract_pages(destination)
        return protocol_id, file.filename or safe_filename, pages

    def extract_pages(self, path: Path) -> list[ProtocolPage]:
        if path.suffix.lower() == ".txt":
            text = path.read_text(encoding="utf-8", errors="ignore")
            chunks = [text[i : i + 3500] for i in range(0, len(text), 3500)] or [""]
            return [ProtocolPage(page=index + 1, text=chunk) for index, chunk in enumerate(chunks)]

        try:
            import fitz
        except ImportError as exc:
            raise RuntimeError("PyMuPDF is required to parse PDFs") from exc

        pages: list[ProtocolPage] = []
        with fitz.open(path) as doc:
            for index, page in enumerate(doc, start=1):
                pages.append(ProtocolPage(page=index, text=page.get_text("text").strip()))
        return pages
