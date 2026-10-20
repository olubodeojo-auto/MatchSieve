from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any
from .config import ROOT
from .db import connect
from .normalise import utc_now
from .repository import Repository
from .importers import import_csv, import_json
from .kb_writer import refresh_indexes


def infer_source_key(path: Path) -> str:
    name = path.name.lower()
    if 'football-data' in name or 'football_data' in name or 'fdata' in name:
        return 'football_data_co_uk'
    if 'openligadb' in name:
        return 'openligadb_import'
    return 'inbox_csv' if path.suffix.lower() == '.csv' else 'inbox_json'


def _previously_ingested(repo: Repository, rel: str, digest: str) -> bool:
    conn = connect(repo.db_path)
    try:
        return conn.execute(
            'SELECT 1 FROM ingested_files WHERE relative_path=? AND sha256=?', (rel, digest)
        ).fetchone() is not None
    finally:
        conn.close()


def _record_file(repo: Repository, rel: str, digest: str, source_key: str,
                 file_type: str, result: dict[str, Any]) -> None:
    conn = connect(repo.db_path)
    try:
        conn.execute('''INSERT OR IGNORE INTO ingested_files
            (relative_path,sha256,source_key,file_type,imported_at,imported_records,error_count,errors_json)
            VALUES(?,?,?,?,?,?,?,?)''',
            (rel, digest, source_key, file_type, utc_now(), int(result.get('imported', 0)),
             len(result.get('errors', [])), json.dumps(result.get('errors', []), ensure_ascii=False)))
        conn.commit()
    finally:
        conn.close()


def sync_inbox(repo: Repository | None = None, inbox: Path | None = None,
               include_processed: bool = False) -> dict[str, Any]:
    """Import new CSV/JSON inbox files; unchanged file hashes are skipped. Makes no web/API calls."""
    repo = repo or Repository()
    inbox = Path(inbox or (ROOT / 'data' / 'inbox'))
    inbox.mkdir(parents=True, exist_ok=True)
    scanned = skipped = 0
    results: list[dict[str, Any]] = []
    files = sorted([*inbox.glob('*.csv'), *inbox.glob('*.json')])
    for path in files:
        scanned += 1
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rel = path.name
        source_key = infer_source_key(path)
        if not include_processed and _previously_ingested(repo, rel, digest):
            skipped += 1
            continue
        try:
            result = import_csv(path, repo, source_key) if path.suffix.lower() == '.csv' else import_json(path, repo, source_key)
            _record_file(repo, rel, digest, source_key, path.suffix.lower().lstrip('.'), result)
            results.append({'file': path.name, 'status': 'imported', 'imported': result['imported'],
                            'error_count': len(result['errors'])})
        except Exception as exc:
            results.append({'file': path.name, 'status': 'failed', 'error': str(exc)})
    try:
        indexes = refresh_indexes(repo)
    except Exception as exc:
        indexes = {'warning': str(exc)}
    return {'inbox': str(inbox), 'scanned': scanned, 'skipped_unchanged': skipped,
            'results': results, 'knowledge_base': indexes}
