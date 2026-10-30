from __future__ import annotations
from statistics import mean
from typing import Any
from .repository import Repository

MARKETS={
    "UNDER_4_5":{"label":"Under 4.5 Goals","question":"How often do recent results stay below five total goals?","metric":"total goals <= 4; specifically inspect five-or-more-goal results"},
    "UNDER_3_5":{"label":"Under 3.5 Goals","question":"How often do recent results finish with three or fewer total goals?","metric":"total goals <= 3"},
    "OVER_2_5":{"label":"Over 2.5 Goals","question":"How often do recent results produce at least three total goals?","metric":"total goals >= 3"},
    "BTTS":{"label":"Both Teams To Score","question":"How often have both teams scored in the same match?","metric":"both teams score at least once"},
    "DOUBLE_CHANCE":{"label":"Double Chance","question":"Review result distribution and home/away context without forcing a selection.","metric":"W/D/L distribution in recent results"},
    "RESULT_1X2":{"label":"Match Result (1X2)","question":"Review recent result distribution and context.","metric":"W/D/L distribution in recent results"},
    "RESEARCH_BRIEF":{"label":"General Research Brief","question":"What is known, what supports each side, and what is missing?","metric":"balanced contextual evidence"},
}


def _summary(results: list[dict[str, Any]], team: str) -> dict[str, Any]:
    if not results:
        return {"team":team,"sample_size":0,"matches":[],"goals_for_avg":None,"goals_against_avg":None,"total_goals_avg":None,
                "under_4_5_count":0,"five_plus_goals_count":0,"over_2_5_count":0,"btts_count":0,"clean_sheets":0,"wdl":{"W":0,"D":0,"L":0}}
    wdl={"W":0,"D":0,"L":0}
    for r in results:
        gf,ga=int(r['goals_for']),int(r['goals_against'])
        wdl["W" if gf>ga else "D" if gf==ga else "L"]+=1
    n=len(results)
    return {"team":team,"sample_size":n,"matches":[{k:r.get(k) for k in ("kickoff_utc","home_team","away_team","home_score","away_score","total_goals","goals_for","goals_against")} for r in results],
            "goals_for_avg":round(mean([r['goals_for'] for r in results]),2),
            "goals_against_avg":round(mean([r['goals_against'] for r in results]),2),
            "total_goals_avg":round(mean([r['total_goals'] for r in results]),2),
            "under_4_5_count":sum(r['total_goals']<=4 for r in results),
            "five_plus_goals_count":sum(r['total_goals']>=5 for r in results),
            "over_2_5_count":sum(r['total_goals']>=3 for r in results),
            "btts_count":sum(r['btts'] for r in results),
            "clean_sheets":sum(r['clean_sheet'] for r in results),"wdl":wdl}



def _summary_from_section(records: list[dict[str, Any]], team: str) -> dict[str, Any]:
    prepared: list[dict[str, Any]] = []
    for row in records:
        home_score, away_score = int(row["home_score"]), int(row["away_score"])
        if str(row["home_team"]).casefold() == team.casefold():
            goals_for, goals_against = home_score, away_score
        elif str(row["away_team"]).casefold() == team.casefold():
            goals_for, goals_against = away_score, home_score
        else:
            continue
        total = home_score + away_score
        prepared.append({
            "kickoff_utc": row["date"], "home_team": row["home_team"], "away_team": row["away_team"],
            "home_score": home_score, "away_score": away_score, "goals_for": goals_for,
            "goals_against": goals_against, "total_goals": total,
            "btts": int(home_score > 0 and away_score > 0),
            "clean_sheet": int(goals_against == 0),
        })
    prepared.sort(key=lambda item: item["kickoff_utc"], reverse=True)
    return _summary(prepared, team)


def _h2h_from_section(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "kickoff_utc": row["date"], "home_team": row["home_team"], "away_team": row["away_team"],
        "competition": row["competition"], "home_score": row["home_score"], "away_score": row["away_score"],
    } for row in records]

def build_evidence(repo: Repository, fixture_id: int, market_code: str, sample_size: int=10) -> dict[str, Any]:
    if market_code not in MARKETS: raise ValueError(f"Unknown market {market_code}. Choose one of: {', '.join(MARKETS)}")
    fixture=repo.get_fixture(fixture_id)
    if not fixture: raise ValueError(f"Fixture ID {fixture_id} not found")
    kickoff=fixture['kickoff_utc']
    observations=repo.observations(fixture_id)
    pasted_rows = observations.get("pasted_match_history", [])
    pasted = pasted_rows[0].get("value") if pasted_rows else None
    pasted_sections = (pasted or {}).get("sections", {}) if isinstance(pasted, dict) else {}
    if pasted_sections:
        home_records = pasted_sections.get("home_form", [])
        away_records = pasted_sections.get("away_form", [])
        h2h_records = pasted_sections.get("h2h", [])
        home = _summary_from_section(home_records, fixture["home_team"])
        away = _summary_from_section(away_records, fixture["away_team"])
        h2h = _h2h_from_section(h2h_records)
        sample_size = 35
        history_coverage = (pasted or {}).get("coverage", {})
    else:
        home=_summary(repo.recent_team_results(fixture['home_team'],kickoff,sample_size),fixture['home_team'])
        away=_summary(repo.recent_team_results(fixture['away_team'],kickoff,sample_size),fixture['away_team'])
        h2h=repo.h2h_results(fixture['home_team'],fixture['away_team'],kickoff,10)
        history_coverage = {}
    missing=[]
    if home['sample_size']<5: missing.append(f"Only {home['sample_size']} prior completed match(es) found for {fixture['home_team']}; five-match form comparison is incomplete.")
    if away['sample_size']<5: missing.append(f"Only {away['sample_size']} prior completed match(es) found for {fixture['away_team']}; five-match form comparison is incomplete.")
    if history_coverage:
        for section_key, section_label in (("home_form", "home-team form"), ("away_form", "away-team form"), ("h2h", "head-to-head")):
            section_count = int(history_coverage.get(section_key, {}).get("records_found", 0))
            if section_count < 35:
                missing.append(f"Only {section_count} of up to 35 {section_label} records were captured; the available sample is incomplete.")
    for wanted,label in (("injuries","current injury information"),("suspensions","current suspension information"),("lineups","confirmed line-ups")):
        if wanted not in observations: missing.append(f"{label.capitalize()} not captured for this fixture.")
    source_count=0
    import sqlite3
    from .db import connect
    conn=connect(repo.db_path)
    try:
        source_count=int(conn.execute("SELECT COUNT(*) FROM source_snapshots WHERE fixture_id=?",(fixture_id,)).fetchone()[0])
        snap=conn.execute("SELECT source_key,source_ref,source_url,captured_at,quality_label FROM source_snapshots WHERE fixture_id=? ORDER BY captured_at DESC",(fixture_id,)).fetchall()
        sources=[dict(x) for x in snap]
    finally: conn.close()
    if not sources: missing.append("No source snapshot is linked to this fixture.")
    if home['sample_size']>=5 and away['sample_size']>=5 and sources:
        status="READY_FOR_REVIEW"
    else: status="LIMITED_EVIDENCE"
    market=MARKETS[market_code]
    supportive=[]; counter=[]
    if market_code.startswith("UNDER_"):
        threshold=4 if market_code=="UNDER_4_5" else 3
        for summary in (home,away):
            n=summary['sample_size']
            if n:
                below=sum(m['total_goals']<=threshold for m in summary['matches'])
                above=sum(m['total_goals']>threshold for m in summary['matches'])
                supportive.append(f"{summary['team']}: {below}/{n} available prior matches finished at {threshold} or fewer total goals.")
                counter.append(f"{summary['team']}: {above}/{n} available prior matches exceeded {threshold} total goals.")
        if market_code=="UNDER_4_5":
            for summary in (home,away):
                if summary['five_plus_goals_count']:
                    counter.append(f"{summary['team']}: {summary['five_plus_goals_count']} of {summary['sample_size']} available prior matches had 5+ total goals.")
    elif market_code=="OVER_2_5":
        for summary in (home,away):
            if summary['sample_size']:
                supportive.append(f"{summary['team']}: {summary['over_2_5_count']}/{summary['sample_size']} available prior matches had 3+ total goals.")
                counter.append(f"{summary['team']}: {summary['sample_size']-summary['over_2_5_count']}/{summary['sample_size']} available prior matches had 0–2 total goals.")
    elif market_code=="BTTS":
        for summary in (home,away):
            if summary['sample_size']:
                supportive.append(f"{summary['team']}: both teams scored in {summary['btts_count']}/{summary['sample_size']} available prior matches.")
                counter.append(f"{summary['team']}: at least one team failed to score in {summary['sample_size']-summary['btts_count']}/{summary['sample_size']} available prior matches.")
    elif market_code in ("DOUBLE_CHANCE","RESULT_1X2"):
        for summary in (home,away):
            supportive.append(f"{summary['team']} W/D/L in available sample: {summary['wdl']['W']}/{summary['wdl']['D']}/{summary['wdl']['L']} from {summary['sample_size']} matches.")
        counter.append("Recent W/D/L counts do not account by themselves for opponent strength, lineup changes or current match context.")
    else:
        supportive.append("Use recent form, goals, H2H and verified contextual observations together; do not treat any one indicator as decisive.")
        counter.append("The current archive cannot establish a forecast when key context or sample sizes are missing.")
    return {"fixture":fixture,"market_code":market_code,"market":market,"status":status,"generated_at":__import__('matchsieve.normalise',fromlist=['utc_now']).utc_now(),
            "home_form":home,"away_form":away,"h2h":h2h,"history_coverage":history_coverage,"supporting_signals":supportive,"counter_signals":counter,
            "missing_information":missing,"observations":observations,"sources":sources,"source_snapshot_count":source_count,
            "method_note":"Counts describe only records currently stored in the local archive. They are not probabilities, predictions, or a guarantee of future outcomes."}
