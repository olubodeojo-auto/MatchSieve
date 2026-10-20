from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .config import ROOT, DB_PATH
from .db import connect, table_counts
from .normalise import utc_now


def knowledge_base_root(repo) -> Path:
    """Use the project KB for the configured database and isolate test/alternate databases."""
    try:
        if Path(repo.db_path).resolve() == Path(DB_PATH).resolve():
            return ROOT / 'knowledge-base'
    except Exception:
        pass
    return Path(repo.db_path).resolve().parent / 'knowledge-base'


def refresh_indexes(repo) -> dict[str, str]:
    """Regenerate compact Markdown indexes; SQLite records remain the source of truth."""
    outdir=knowledge_base_root(repo); outdir.mkdir(parents=True,exist_ok=True)
    counts=table_counts(repo.db_path)
    conn=connect(repo.db_path)
    try:
        sources=conn.execute("SELECT source_primary,COUNT(*) AS n FROM fixtures GROUP BY source_primary ORDER BY n DESC").fetchall()
        latest=conn.execute("""SELECT f.id,f.kickoff_utc,f.competition,f.home_team,f.away_team,f.status,f.source_primary,
            r.home_score,r.away_score,(SELECT COUNT(*) FROM source_snapshots s WHERE s.fixture_id=f.id) AS snapshots
            FROM fixtures f LEFT JOIN match_results r ON r.fixture_id=f.id ORDER BY f.updated_at DESC LIMIT 100""").fetchall()
        reports=conn.execute("""SELECT r.id,r.market_code,r.evidence_status,r.created_at,r.report_version,f.kickoff_utc,f.competition,f.home_team,f.away_team
            FROM research_reports r JOIN fixtures f ON f.id=r.fixture_id ORDER BY r.created_at DESC LIMIT 100""").fetchall()
    finally: conn.close()
    lines=["# MatchSieve Knowledge Base Index","",f"Last refreshed: {utc_now()}","",
           "## Archive health", "", "| Record type | Count |", "|---|---:|"]
    lines += [f"| {k.replace('_',' ').title()} | {v} |" for k,v in counts.items()]
    lines += ["", "## Records by primary intake source", "", "| Source | Fixtures |", "|---|---:|"]
    lines += [f"| `{r['source_primary']}` | {r['n']} |" for r in sources] or ["| No fixtures imported yet | 0 |"]
    lines += ["", "## Recent research reports", ""]
    if reports:
        for r in reports:
            lines.append(f"- **#{r['id']} — {r['home_team']} vs {r['away_team']}** — {r['market_code']} — `{r['evidence_status']}` — report v{r['report_version']} — generated {r['created_at']}")
    else: lines.append("No research reports yet. Select a fixture and a market to create the first report.")
    lines += ["", "## Recent fixtures", ""]
    if latest:
        for f in latest:
            score=f" — {f['home_score']}–{f['away_score']}" if f['home_score'] is not None and f['away_score'] is not None else ""
            lines.append(f"- **ID {f['id']}** {f['kickoff_utc'][:10]} — {f['competition']}: {f['home_team']} vs {f['away_team']}{score} — `{f['status']}` — source `{f['source_primary']}` — snapshots {f['snapshots']}")
    else: lines.append("No fixtures have been imported.")
    lines += ["", "## Retrieval rule", "", "This index is a navigation aid. Reports, fixture records and source snapshots are stored separately in SQLite and `knowledge-base/reports/`. The AI must retrieve only relevant records and must not treat this index as a complete source of match facts.", ""]
    index_path=outdir/'INDEX.md'; index_path.write_text("\n".join(lines),encoding='utf-8')
    fixture_lines=["# Fixture Archive Index","",f"Generated: {utc_now()}","", "| ID | Kickoff UTC | Competition | Fixture | Score | Status | Source | Snapshot count |", "|---:|---|---|---|---|---|---|---:|"]
    for f in latest:
        score=f"{f['home_score']}–{f['away_score']}" if f['home_score'] is not None and f['away_score'] is not None else "—"
        fixture_lines.append(f"| {f['id']} | {f['kickoff_utc']} | {f['competition']} | {f['home_team']} vs {f['away_team']} | {score} | {f['status']} | `{f['source_primary']}` | {f['snapshots']} |")
    if not latest: fixture_lines.append("| — | — | — | No fixtures yet | — | — | — | 0 |")
    fixture_path=outdir/'fixtures-index.md'; fixture_path.write_text("\n".join(fixture_lines)+"\n",encoding='utf-8')
    week_path=refresh_current_week_digest(repo, outdir)
    return {"index":str(index_path),"fixtures_index":str(fixture_path),"weekly_digest":str(week_path)}


def refresh_current_week_digest(repo, outdir: Path | None=None) -> Path:
    outdir=outdir or (ROOT/'knowledge-base')
    now=datetime.now(timezone.utc)
    monday=(now-timedelta(days=now.weekday())).replace(hour=0,minute=0,second=0,microsecond=0)
    next_monday=monday+timedelta(days=7)
    stamp=monday.isocalendar(); week_path=outdir/'weeks'/f"{stamp.year}-W{stamp.week:02d}.md"; week_path.parent.mkdir(parents=True,exist_ok=True)
    conn=connect(repo.db_path)
    try:
        rows=conn.execute("""SELECT r.id,r.market_code,r.evidence_status,r.created_at,r.report_version,f.kickoff_utc,f.competition,f.home_team,f.away_team,r.markdown
            FROM research_reports r JOIN fixtures f ON f.id=r.fixture_id ORDER BY r.created_at DESC""").fetchall()
    finally: conn.close()
    start=monday.isoformat().replace('+00:00','Z'); end=next_monday.isoformat().replace('+00:00','Z')
    selected=[r for r in rows if start <= str(r['created_at']) < end]
    lines=[f"# MatchSieve Weekly Research Digest — {stamp.year} Week {stamp.week:02d}","",f"Period starts {start} (UTC). Generated: {utc_now()}","",
           "This is an index of research runs created this week. It does not replace the versioned full reports.",""]
    if not selected: lines.append("No research reports were generated this week yet.")
    else:
        for r in selected:
            lines += [f"## Report #{r['id']} — {r['home_team']} vs {r['away_team']}","",
                      f"- Competition: {r['competition']}",f"- Kickoff UTC: {r['kickoff_utc']}",f"- Requested market: {r['market_code']}",
                      f"- Evidence status: `{r['evidence_status']}`",f"- Report version: {r['report_version']}",f"- Generated: {r['created_at']}","",
                      "### Research extract","",str(r['markdown']).split('## Evidence from recent completed matches',1)[-1][:1100],"", "---",""]
    week_path.write_text("\n".join(lines),encoding='utf-8')
    return week_path
