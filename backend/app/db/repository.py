from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.models.schemas import ProtocolFeatures, ProtocolPage, ProtocolRecord, ProtocolSection


def _json_default(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    raise TypeError(f"Cannot serialize {type(value)}")


class ProtocolRepository:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or get_settings().database_path
        self.init()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS protocols (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    pages_json TEXT NOT NULL,
                    sections_json TEXT NOT NULL DEFAULT '[]',
                    features_json TEXT,
                    scores_json TEXT,
                    recommendations_json TEXT NOT NULL DEFAULT '[]'
                )
                """
            )

    def create_protocol(self, protocol_id: str, filename: str, pages: list[ProtocolPage]) -> ProtocolRecord:
        record = ProtocolRecord(
            id=protocol_id,
            filename=filename,
            created_at=datetime.now(timezone.utc),
            pages=pages,
        )
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO protocols (id, filename, created_at, pages_json, sections_json, recommendations_json)
                VALUES (?, ?, ?, ?, '[]', '[]')
                """,
                (
                    record.id,
                    record.filename,
                    record.created_at.isoformat(),
                    json.dumps([page.model_dump() for page in pages]),
                ),
            )
        return record

    def get_protocol(self, protocol_id: str) -> ProtocolRecord | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM protocols WHERE id = ?", (protocol_id,)).fetchone()
        if row is None:
            return None
        return ProtocolRecord(
            id=row["id"],
            filename=row["filename"],
            created_at=datetime.fromisoformat(row["created_at"]),
            pages=[ProtocolPage(**item) for item in json.loads(row["pages_json"])],
            section_map=[ProtocolSection(**item) for item in json.loads(row["sections_json"] or "[]")],
            features=ProtocolFeatures(**json.loads(row["features_json"])) if row["features_json"] else None,
            scores=json.loads(row["scores_json"]) if row["scores_json"] else None,
            recommendations=json.loads(row["recommendations_json"] or "[]"),
        )

    def update_sections(self, protocol_id: str, sections: list[ProtocolSection]) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE protocols SET sections_json = ? WHERE id = ?",
                (json.dumps([section.model_dump() for section in sections]), protocol_id),
            )

    def update_features(self, protocol_id: str, features: ProtocolFeatures) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE protocols SET features_json = ? WHERE id = ?",
                (features.model_dump_json(), protocol_id),
            )

    def update_scores(self, protocol_id: str, scores: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE protocols SET scores_json = ? WHERE id = ?",
                (json.dumps(scores, default=_json_default), protocol_id),
            )

    def update_recommendations(self, protocol_id: str, recommendations: list[dict[str, Any]]) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE protocols SET recommendations_json = ? WHERE id = ?",
                (json.dumps(recommendations, default=_json_default), protocol_id),
            )
