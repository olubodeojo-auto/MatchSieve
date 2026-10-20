from __future__ import annotations
import sqlite3
from pathlib import Path
from .config import DB_PATH, ROOT

SCHEMA_PATH = ROOT / "migrations" / "001_initial.sql"


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    db_path = Path(path or DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=20000")
    return conn


def initialize(path: Path | str | None = None) -> Path:
    db_path = Path(path or DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(db_path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()
    return db_path


def table_counts(path: Path | str | None = None) -> dict[str, int]:
    conn = connect(path)
    try:
        names = ["fixtures", "match_results", "source_snapshots", "field_observations", "research_reports", "knowledge_documents", "provider_runs", "ingested_files"]
        return {name: int(conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]) for name in names}
    finally:
        conn.close()
