from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_env_file(path: Path | None = None) -> None:
    """Load a small .env file without overriding explicit environment variables.

    This intentionally supports the original Sentinel variable names through config
    fallbacks below. Secrets are never loaded from key.txt files automatically.
    """
    path = path or ROOT / ".env"
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


def _env(name: str, default: str, legacy_name: str | None = None) -> str:
    value = os.getenv(name)
    if value is not None:
        return value
    if legacy_name:
        legacy = os.getenv(legacy_name)
        if legacy is not None:
            return legacy
    return default


def env_bool(name: str, default: bool = False, legacy_name: str | None = None) -> bool:
    val = _env(name, "true" if default else "false", legacy_name)
    return val.strip().lower() in {"1", "true", "yes", "on"}


def data_path(value: str | None, default: str) -> Path:
    candidate = Path(value or default).expanduser()
    return candidate if candidate.is_absolute() else ROOT / candidate


load_env_file()
DB_PATH = data_path(_env("MATCHSIEVE_DB_PATH", "data/matchsieve.sqlite3", "SENTINEL_DB_PATH"), "data/matchsieve.sqlite3")
HOST = _env("MATCHSIEVE_HOST", "127.0.0.1", "SENTINEL_HOST")
PORT = int(_env("MATCHSIEVE_PORT", "8765", "SENTINEL_PORT"))
REQUEST_TIMEOUT = float(_env("MATCHSIEVE_REQUEST_TIMEOUT", "12", "SENTINEL_REQUEST_TIMEOUT"))
_enabled = _env("MATCHSIEVE_ENABLED_PROVIDERS", "", "SENTINEL_ENABLED_PROVIDERS")
ENABLED_PROVIDERS = [x.strip().lower() for x in _enabled.split(",") if x.strip()]
OLLAMA_ENABLED = env_bool("OLLAMA_ENABLED", False)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "90"))
