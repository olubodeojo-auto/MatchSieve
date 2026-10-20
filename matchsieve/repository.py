from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .config import DB_PATH
from .db import connect, initialize
from .normalise import normalise_name, parse_datetime, utc_now

CORE_FIELDS = {"external_id", "competition", "season", "kickoff", "kickoff_utc", "home_team", "away_team", "status", "venue", "home_score", "away_score", "halftime_home_score", "halftime_away_score", "source_key", "source_ref", "source_url", "is_synthetic", "provider_payload", "quality_label", "result_type"}


def canonical_key(item: dict[str, Any]) -> str:
    kickoff = parse_datetime(item.get("kickoff_utc") or item.get("kickoff"))
    # Same-day, same competition/team order maps to one canonical fixture.
    day = kickoff[:10]
    parts = [normalise_name(item.get("competition", "unknown")), day, normalise_name(item["home_team"]), normalise_name(item["away_team"])]
    return "|".join(parts)


class Repository:
    def __init__(self, db_path: Path | str | None = None):
        self.db_path = Path(db_path or DB_PATH)
        initialize(self.db_path)

    def add_fixture(self, item: dict[str, Any], source_key: str | None = None, source_ref: str | None = None,
                    source_url: str | None = None, raw_payload: Any | None = None) -> int:
        home = str(item.get("home_team") or "").strip()
        away = str(item.get("away_team") or "").strip()
        competition = str(item.get("competition") or item.get("league") or "Unknown competition").strip()
        if not home or not away:
            raise ValueError("Both home_team and away_team are required")
        if normalise_name(home) == normalise_name(away):
            raise ValueError("Home and away teams must be different")
        kickoff = parse_datetime(item.get("kickoff_utc") or item.get("kickoff"))
        source_key = source_key or item.get("source_key") or "manual"
        source_ref = source_ref or item.get("source_ref")
        source_url = source_url or item.get("source_url")
        now = utc_now()
        key = canonical_key({**item, "competition": competition, "kickoff_utc": kickoff, "home_team": home, "away_team": away})
        payload = raw_payload if raw_payload is not None else item
        payload_text = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
        digest = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
        status = str(item.get("status") or ("finished" if item.get("home_score") is not None and item.get("away_score") is not None else "scheduled")).lower()
        conn = connect(self.db_path)
        try:
            existing = conn.execute("SELECT id FROM fixtures WHERE canonical_key=?", (key,)).fetchone()
            if existing:
                fixture_id = int(existing["id"])
                conn.execute("""UPDATE fixtures SET external_id=COALESCE(?,external_id), season=COALESCE(?,season),
                    status=CASE WHEN ? IN ('finished','complete','completed','ft') THEN 'finished' ELSE status END,
                    venue=COALESCE(?,venue), source_primary=?, source_ref=COALESCE(?,source_ref),
                    updated_at=? WHERE id=?""",
                    (str(item.get("external_id")) if item.get("external_id") is not None else None,
                     item.get("season"), status, item.get("venue"), source_key, source_ref, now, fixture_id))
            else:
                cur = conn.execute("""INSERT INTO fixtures(canonical_key,external_id,competition,season,kickoff_utc,home_team,away_team,
                    status,venue,source_primary,source_ref,is_synthetic,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (key, str(item.get("external_id")) if item.get("external_id") is not None else None,
                     competition, item.get("season"), kickoff, home, away, status, item.get("venue"),
                     source_key, source_ref, int(bool(item.get("is_synthetic", False))), now, now))
                fixture_id = int(cur.lastrowid)
            conn.execute("""INSERT OR IGNORE INTO source_snapshots(fixture_id,source_key,source_ref,source_url,captured_at,
                payload_sha256,payload_json,quality_label) VALUES(?,?,?,?,?,?,?,?)""",
                (fixture_id, source_key, source_ref, source_url, now, digest, payload_text,
                 str(item.get("quality_label") or "unreviewed")))
            # Keep meaningful non-core fields as individually traceable observations.
            extra = {k: v for k, v in item.items() if k not in CORE_FIELDS and v not in (None, "", [], {})}
            for field, value in extra.items():
                value_json = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
                # Do not multiply identical observations when the same source file is re-imported.
                conn.execute("""INSERT INTO field_observations(fixture_id,field_name,value_json,source_key,source_ref,source_url,captured_at,verification_status)
                    SELECT ?,?,?,?,?,?,?,? WHERE NOT EXISTS (
                        SELECT 1 FROM field_observations WHERE fixture_id=? AND field_name=? AND value_json=?
                          AND source_key=? AND source_ref IS ?
                    )""",
                    (fixture_id, field, value_json, source_key, source_ref, source_url, now,
                     "source-reported" if source_url else "unverified",
                     fixture_id, field, value_json, source_key, source_ref))
            if item.get("home_score") is not None and item.get("away_score") is not None:
                conn.execute("""INSERT INTO match_results(fixture_id,home_score,away_score,halftime_home_score,halftime_away_score,
                    result_type,captured_at,source_key) VALUES(?,?,?,?,?,?,?,?)
                    ON CONFLICT(fixture_id) DO UPDATE SET home_score=excluded.home_score,away_score=excluded.away_score,
                    halftime_home_score=COALESCE(excluded.halftime_home_score,match_results.halftime_home_score),
                    halftime_away_score=COALESCE(excluded.halftime_away_score,match_results.halftime_away_score),
                    captured_at=excluded.captured_at,source_key=excluded.source_key""",
                    (fixture_id, int(item["home_score"]), int(item["away_score"]), item.get("halftime_home_score"),
                     item.get("halftime_away_score"), str(item.get("result_type") or "full_time"), now, source_key))
                conn.execute("UPDATE fixtures SET status='finished',updated_at=? WHERE id=?", (now, fixture_id))
            conn.commit()
            return fixture_id
        finally:
            conn.close()

    def get_fixture(self, fixture_id: int) -> dict[str, Any] | None:
        conn = connect(self.db_path)
        try:
            row = conn.execute("""SELECT f.*,r.home_score,r.away_score,r.halftime_home_score,r.halftime_away_score,
                r.captured_at AS result_captured_at FROM fixtures f LEFT JOIN match_results r ON r.fixture_id=f.id WHERE f.id=?""", (fixture_id,)).fetchone()
            return dict(row) if row else None
        finally: conn.close()

    def list_fixtures(self, query: str = "", limit: int = 50) -> list[dict[str, Any]]:
        conn = connect(self.db_path)
        try:
            q = f"%{query.strip()}%"
            rows = conn.execute("""SELECT f.*,r.home_score,r.away_score FROM fixtures f LEFT JOIN match_results r ON r.fixture_id=f.id
                WHERE (?='' OR f.home_team LIKE ? OR f.away_team LIKE ? OR f.competition LIKE ?)
                ORDER BY f.kickoff_utc ASC LIMIT ?""", (query.strip(), q, q, q, max(1,min(int(limit),500)))).fetchall()
            return [dict(x) for x in rows]
        finally: conn.close()

    def recent_team_results(self, team: str, before: str, limit: int = 10) -> list[dict[str, Any]]:
        conn = connect(self.db_path)
        try:
            rows = conn.execute("""SELECT f.id,f.competition,f.kickoff_utc,f.home_team,f.away_team,
                r.home_score,r.away_score,r.captured_at AS result_captured_at,
                CASE WHEN lower(f.home_team)=lower(?) THEN r.home_score ELSE r.away_score END AS goals_for,
                CASE WHEN lower(f.home_team)=lower(?) THEN r.away_score ELSE r.home_score END AS goals_against
                FROM fixtures f JOIN match_results r ON r.fixture_id=f.id
                WHERE (lower(f.home_team)=lower(?) OR lower(f.away_team)=lower(?)) AND f.kickoff_utc < ?
                ORDER BY f.kickoff_utc DESC LIMIT ?""", (team,team,team,team,before,limit)).fetchall()
            out=[]
            for row in rows:
                d=dict(row); total=int(d['home_score'])+int(d['away_score']); d['total_goals']=total
                d['btts']=int(d['home_score']>0 and d['away_score']>0); d['clean_sheet']=int(d['goals_against']==0)
                out.append(d)
            return out
        finally: conn.close()

    def h2h_results(self, home: str, away: str, before: str, limit: int = 10) -> list[dict[str, Any]]:
        conn = connect(self.db_path)
        try:
            rows=conn.execute("""SELECT f.id,f.kickoff_utc,f.home_team,f.away_team,f.competition,r.home_score,r.away_score
                FROM fixtures f JOIN match_results r ON r.fixture_id=f.id
                WHERE ((lower(f.home_team)=lower(?) AND lower(f.away_team)=lower(?)) OR
                       (lower(f.home_team)=lower(?) AND lower(f.away_team)=lower(?))) AND f.kickoff_utc < ?
                ORDER BY f.kickoff_utc DESC LIMIT ?""",(home,away,away,home,before,limit)).fetchall()
            return [dict(r) for r in rows]
        finally: conn.close()

    def observations(self, fixture_id: int) -> dict[str, list[dict[str, Any]]]:
        conn=connect(self.db_path)
        try:
            rows=conn.execute("SELECT * FROM field_observations WHERE fixture_id=? ORDER BY captured_at DESC",(fixture_id,)).fetchall()
            out={}
            for row in rows:
                d=dict(row); d['value']=json.loads(d.pop('value_json'))
                out.setdefault(d['field_name'],[]).append(d)
            return out
        finally: conn.close()

    def save_report(self, fixture_id: int, market: str, status: str, request: dict[str, Any], report: dict[str, Any], markdown: str, llm_used: bool=False) -> int:
        conn=connect(self.db_path)
        try:
            version=int(conn.execute("SELECT COALESCE(MAX(report_version),0)+1 FROM research_reports WHERE fixture_id=? AND market_code=?",(fixture_id,market)).fetchone()[0])
            cur=conn.execute("""INSERT INTO research_reports(fixture_id,market_code,report_version,evidence_status,request_json,report_json,markdown,llm_used,created_at)
                VALUES(?,?,?,?,?,?,?,?,?)""",(fixture_id,market,version,status,json.dumps(request,ensure_ascii=False),json.dumps(report,ensure_ascii=False,default=str),markdown,int(llm_used),utc_now()))
            conn.commit(); return int(cur.lastrowid)
        finally: conn.close()

    def add_knowledge_document(self, key: str, title: str, doc_type: str, markdown: str, tags: list[str] | None=None, sources: list[dict[str,Any]]|None=None) -> int:
        conn=connect(self.db_path)
        try:
            now=utc_now(); old=conn.execute("SELECT id,version FROM knowledge_documents WHERE doc_key=?",(key,)).fetchone()
            if old:
                version=int(old['version'])+1
                conn.execute("UPDATE knowledge_documents SET title=?,doc_type=?,markdown=?,tags_json=?,source_json=?,version=?,updated_at=? WHERE id=?",
                    (title,doc_type,markdown,json.dumps(tags or []),json.dumps(sources or [],ensure_ascii=False),version,now,old['id']))
                doc_id=int(old['id'])
                conn.execute("DELETE FROM knowledge_fts WHERE doc_key=?",(key,))
            else:
                cur=conn.execute("INSERT INTO knowledge_documents(doc_key,title,doc_type,markdown,tags_json,source_json,version,created_at,updated_at) VALUES(?,?,?,?,?,?,1,?,?)",
                    (key,title,doc_type,markdown,json.dumps(tags or []),json.dumps(sources or [],ensure_ascii=False),now,now))
                doc_id=int(cur.lastrowid)
            conn.execute("INSERT INTO knowledge_fts(doc_key,title,markdown,tags) VALUES(?,?,?,?)",(key,title,markdown," ".join(tags or [])))
            conn.commit(); return doc_id
        finally: conn.close()

    def list_reports(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return recent saved report records, including their structured evidence payload."""
        conn = connect(self.db_path)
        try:
            rows = conn.execute("""SELECT r.id, r.fixture_id, r.market_code, r.report_version,
                r.evidence_status, r.report_json, r.markdown, r.llm_used, r.created_at,
                f.competition, f.kickoff_utc, f.home_team, f.away_team, f.status AS fixture_status,
                f.source_primary, f.source_ref, mr.home_score, mr.away_score
                FROM research_reports r JOIN fixtures f ON f.id=r.fixture_id LEFT JOIN match_results mr ON mr.fixture_id=f.id
                ORDER BY r.created_at DESC, r.id DESC LIMIT ?""", (max(1, min(int(limit), 100)),)).fetchall()
            out = []
            for row in rows:
                item = dict(row)
                try:
                    item["report"] = json.loads(item.pop("report_json"))
                except (TypeError, json.JSONDecodeError):
                    item["report"] = {}
                item["llm_used"] = bool(item.get("llm_used"))
                out.append(item)
            return out
        finally:
            conn.close()

    def get_report(self, report_id: int) -> dict[str, Any] | None:
        """Return one saved report with its joined fixture data and decoded evidence."""
        conn = connect(self.db_path)
        try:
            row = conn.execute("""SELECT r.id, r.fixture_id, r.market_code, r.report_version,
                r.evidence_status, r.report_json, r.markdown, r.llm_used, r.created_at,
                f.competition, f.kickoff_utc, f.home_team, f.away_team, f.status AS fixture_status,
                f.source_primary, f.source_ref, mr.home_score, mr.away_score
                FROM research_reports r JOIN fixtures f ON f.id=r.fixture_id LEFT JOIN match_results mr ON mr.fixture_id=f.id WHERE r.id=?""", (int(report_id),)).fetchone()
            if not row:
                return None
            item = dict(row)
            try:
                item["report"] = json.loads(item.pop("report_json"))
            except (TypeError, json.JSONDecodeError):
                item["report"] = {}
            item["llm_used"] = bool(item.get("llm_used"))
            return item
        finally:
            conn.close()

    def search_knowledge(self, query: str, limit: int=10) -> list[dict[str, Any]]:
        conn=connect(self.db_path)
        try:
            terms=[x for x in query.split() if x.strip()]
            if not terms: return []
            # FTS syntax is quoted to avoid user input breaking the query.
            expression=' AND '.join('"'+t.replace('"','')+'"' for t in terms)
            try:
                rows=conn.execute("SELECT d.* FROM knowledge_fts x JOIN knowledge_documents d ON d.doc_key=x.doc_key WHERE knowledge_fts MATCH ? ORDER BY rank LIMIT ?",(expression,limit)).fetchall()
            except Exception:
                rows=conn.execute("SELECT * FROM knowledge_documents WHERE title LIKE ? OR markdown LIKE ? LIMIT ?",(f'%{query}%',f'%{query}%',limit)).fetchall()
            return [dict(r) for r in rows]
        finally: conn.close()
