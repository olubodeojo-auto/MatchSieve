from __future__ import annotations
import csv, json
from pathlib import Path
from typing import Any, Iterable
from .repository import Repository


def _refresh_kb(repo: Repository) -> dict[str, Any]:
    try:
        from .kb_writer import refresh_indexes
        return {"status": "refreshed", "paths": refresh_indexes(repo)}
    except Exception as exc:
        # Keep imported data even if generating human-readable indexes fails.
        return {"status": "failed", "error": str(exc)}

ALIASES={
    "date":"kickoff", "datetime":"kickoff", "matchdate":"kickoff", "matchdatetimeutc":"kickoff", "kickoff":"kickoff", "kickoff_utc":"kickoff_utc",
    "home":"home_team", "hometeam":"home_team", "home_team":"home_team", "away":"away_team", "awayteam":"away_team", "away_team":"away_team",
    "league":"competition", "div":"competition", "competition":"competition", "season":"season", "status":"status", "venue":"venue",
    "fthg":"home_score", "homescore":"home_score", "home_score":"home_score", "ftag":"away_score", "awayscore":"away_score", "away_score":"away_score",
    "hthg":"halftime_home_score", "halftime_home_score":"halftime_home_score", "htag":"halftime_away_score", "halftime_away_score":"halftime_away_score",
    "fixtureid":"external_id", "fixture_id":"external_id", "id":"external_id", "source_url":"source_url", "source_ref":"source_ref"
}


def _int_or_none(value: Any) -> int | None:
    if value is None or str(value).strip()=="": return None
    try: return int(float(value))
    except (TypeError,ValueError): return None


def normalize_row(row: dict[str, Any], default_source: str="csv_import") -> dict[str, Any]:
    out={}
    for k,v in row.items():
        key=str(k or "").strip().replace(" ","").replace("-","").lower()
        mapped=ALIASES.get(key)
        if mapped and v not in (None,""):
            out[mapped]=v.strip() if isinstance(v,str) else v
    # Football-Data.co.uk uses FTR and many extra stat columns; preserve useful fields.
    for k,v in row.items():
        if v not in (None,"") and str(k).strip().lower() not in {"div","date","hometeam","awayteam","fthg","ftag","ftr","hthg","htag"}:
            out.setdefault("source_field_"+str(k).strip().replace(" ","_"), v)
    if not out.get("kickoff") and not out.get("kickoff_utc"): raise ValueError("Missing Date/Kickoff column")
    if not out.get("home_team") or not out.get("away_team"): raise ValueError("Missing HomeTeam/Home Team or AwayTeam/Away Team column")
    out.setdefault("competition","Unknown competition")
    out.setdefault("source_key",default_source)
    if "home_score" in out: out["home_score"]=_int_or_none(out["home_score"])
    if "away_score" in out: out["away_score"]=_int_or_none(out["away_score"])
    if "halftime_home_score" in out: out["halftime_home_score"]=_int_or_none(out["halftime_home_score"])
    if "halftime_away_score" in out: out["halftime_away_score"]=_int_or_none(out["halftime_away_score"])
    if "home_score" in out and "away_score" in out and out["home_score"] is not None and out["away_score"] is not None:
        out["status"]="finished"
    return out


def import_csv(path: Path | str, repo: Repository | None=None, source_key: str="csv_import", source_url: str | None=None) -> dict[str, Any]:
    path=Path(path)
    repo=repo or Repository()
    inserted=0; failed=[]; ids=[]
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        sample=f.read(4096); f.seek(0)
        try: dialect=csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error: dialect=csv.excel
        reader=csv.DictReader(f,dialect=dialect)
        if not reader.fieldnames: raise ValueError("CSV has no header row")
        for line_no,row in enumerate(reader,start=2):
            try:
                item=normalize_row(row,source_key)
                item["source_ref"]=item.get("source_ref") or str(path.name)
                sid=item.get("source_url") or source_url
                fixture_id=repo.add_fixture(item,source_key=source_key,source_ref=item["source_ref"],source_url=sid,raw_payload=row)
                ids.append(fixture_id); inserted+=1
            except Exception as exc:
                failed.append({"line":line_no,"error":str(exc)})
    return {"imported":inserted,"errors":failed,"fixture_ids":ids,"source_file":path.name,"knowledge_base":_refresh_kb(repo)}


def import_json(path: Path | str, repo: Repository | None=None, source_key: str="json_import") -> dict[str, Any]:
    path=Path(path); repo=repo or Repository()
    payload=json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload,dict): payload=payload.get("data",payload.get("fixtures",payload.get("matches",[payload])))
    if not isinstance(payload,list): raise ValueError("JSON must contain a list or an object with data/fixtures/matches")
    imported=0; errors=[]; ids=[]
    for idx,row in enumerate(payload,1):
        try:
            item=normalize_row(row,source_key)
            item["source_ref"]=str(path.name)
            fid=repo.add_fixture(item,source_key=source_key,source_ref=str(path.name),source_url=item.get("source_url"),raw_payload=row)
            imported+=1; ids.append(fid)
        except Exception as exc: errors.append({"row":idx,"error":str(exc)})
    return {"imported":imported,"errors":errors,"fixture_ids":ids,"source_file":path.name,"knowledge_base":_refresh_kb(repo)}
