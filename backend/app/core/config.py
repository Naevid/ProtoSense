from functools import lru_cache
import os
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _candidate_env_files() -> list[Path]:
    backend_dir = Path(__file__).resolve().parents[2]
    project_root = backend_dir.parent
    return [
        Path.cwd() / ".env",
        project_root / ".env",
        backend_dir / ".env",
    ]


def _load_env() -> None:
    seen: set[Path] = set()
    for path in _candidate_env_files():
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        _load_dotenv(resolved)


class Settings:
    def __init__(self) -> None:
        _load_env()
        self.app_name = os.getenv("APP_NAME", "Protocol Feasibility Copilot")
        self.database_path = Path(os.getenv("DATABASE_PATH", "backend/data/protocolrisk.sqlite3"))
        self.upload_dir = Path(os.getenv("UPLOAD_DIR", "backend/data/uploads"))
        self.cache_dir = Path(os.getenv("CACHE_DIR", "backend/data/cache"))
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or None
        self.gemini_model = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
        self.enable_gemini = os.getenv("ENABLE_GEMINI", "true").lower() in {"1", "true", "yes"}
        self.cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.cache_dir.mkdir(parents=True, exist_ok=True)
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
