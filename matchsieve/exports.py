from __future__ import annotations
import csv
from pathlib import Path
from typing import Any
from .db import connect
from .config import ROOT
from .normalise import utc_now

EXPORT_FIELDS = [
    'fixture_id','external_id','competition','season','kickoff_utc','home_team','away_team','status','venue',
    'home_score','away_score','halftime_home_score','halftime_away_score','source_primary','source_ref',
    'created_at','updated_at','result_captured_at'
]


def export_fixtures_csv(repo, path: Path | str | None = None) -> dict[str, Any]:
    """Export the complete canonical fixture/result archive for Excel review; snapshots remain in SQLite."""
    target = Path(path) if path else ROOT / 'data' / 'exports' / f"fixtures_{utc_now()[:10]}.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(repo.db_path)
    try:
        rows = conn.execute('''SELECT f.id AS fixture_id,f.external_id,f.competition,f.season,f.kickoff_utc,
            f.home_team,f.away_team,f.status,f.venue,r.home_score,r.away_score,r.halftime_home_score,
            r.halftime_away_score,f.source_primary,f.source_ref,f.created_at,f.updated_at,
            r.captured_at AS result_captured_at
            FROM fixtures f LEFT JOIN match_results r ON r.fixture_id=f.id ORDER BY f.kickoff_utc,f.competition,f.home_team''').fetchall()
        with target.open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=EXPORT_FIELDS, extrasaction='ignore')
            writer.writeheader()
            for row in rows:
                writer.writerow(dict(row))
    finally:
        conn.close()
    return {'path': str(target), 'exported_rows': len(rows), 'format': 'csv',
            'note': 'Canonical fixture/results export. Raw source snapshots and field-level observations remain in SQLite.'}


def export_archive_jsonl(repo, path: Path | str | None = None) -> dict[str, Any]:
    """Stream all fixture, result, source, observation, report, knowledge and provider-run rows to JSONL.

    JSONL is used instead of one huge JSON array so even very large archives can be exported without
    loading the entire database into RAM. Each line is an independent typed record.
    """
    target = Path(path) if path else ROOT / 'data' / 'exports' / f"archive_{utc_now().replace(':','').replace('-','')}.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    tables = [
        ('fixtures','id'), ('match_results','fixture_id'), ('source_snapshots','id'),
        ('field_observations','id'), ('provider_runs','id'), ('ingested_files','id'),
        ('research_reports','id'), ('knowledge_documents','id')
    ]
    total = 0
    conn = connect(repo.db_path)
    try:
        with target.open('w',encoding='utf-8',newline='\n') as handle:
            handle.write(__import__('json').dumps({'record_type':'archive_export_metadata','exported_at_utc':utc_now(),'format':'matchsieve-jsonl-v1'},ensure_ascii=False)+'\n')
            for table, order_col in tables:
                cur = conn.execute(f'SELECT * FROM {table} ORDER BY {order_col}')
                while True:
                    row = cur.fetchone()
                    if row is None: break
                    handle.write(__import__('json').dumps({'record_type':table,'data':dict(row)},ensure_ascii=False,default=str,separators=(',',':'))+'\n')
                    total += 1
    finally:
        conn.close()
    return {'path':str(target),'records_exported':total,'format':'jsonl','streaming':True,
            'note':'One typed JSON record per line plus export metadata; suitable for archival handoff and later re-import tooling.'}
