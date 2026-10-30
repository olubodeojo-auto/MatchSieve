from __future__ import annotations

import hashlib
import re
from datetime import datetime
from typing import Any

MAX_PASTE_CHARS = 200_000
MAX_MATCHES_PER_SECTION = 35
DATE_RE = re.compile(r"(?<!\d)(\d{1,2})[./-](\d{1,2})[./-](\d{4})(?!\d)")
SCORE_RE = re.compile(r"(?<!\d)(\d{1,2})\s*[-:–]\s*(\d{1,2})(?!\d)")
NOISE_RE = re.compile(r"(?i)\b(?:odds?|bet9ja|1xbet|betking|advertisement|sponsored|casino|bonus)\b")


def _normalise_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _section_for(line: str, home_team: str, away_team: str) -> str | None:
    value = re.sub(r"\s+", " ", line.strip().lower())
    compact = _normalise_label(value)
    if any(token in value for token in ("head-to-head", "head to head", "h2h")):
        return "h2h"
    home = _normalise_label(home_team)
    away = _normalise_label(away_team)
    if home and home in compact and ("home" in value or "last matches" in value):
        return "home_form"
    if away and away in compact and ("away" in value or "last matches" in value):
        return "away_form"
    if value in {"last matches: home", "last matches home", "home form", "overall - home"}:
        return "home_form"
    if value in {"last matches: away", "last matches away", "away form", "overall - away"}:
        return "away_form"
    return None


def _clean(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"(?i)\b(?:W|D|L|FT|AET|PEN)\s*$", "", value).strip()
    return value.strip(" |·•")


def _parse_record(line: str, section: str) -> dict[str, Any] | None:
    if NOISE_RE.search(line):
        return None
    date_match = DATE_RE.search(line)
    score_match = SCORE_RE.search(line)
    if not date_match or not score_match or score_match.start() < date_match.end():
        return None
    day, month, year = map(int, date_match.groups())
    try:
        match_date = datetime(year, month, day).date().isoformat()
    except ValueError:
        return None

    parts = [part.strip() for part in line.split("|") if part.strip()]
    competition = ""
    home = away = ""
    if len(parts) >= 5:
        # date | competition | home | score | away
        competition, home, away = parts[1], parts[2], parts[4]
    elif len(parts) == 4:
        # date | competition | home - away | score
        competition = parts[1]
        teams = re.split(r"\s+[-–]\s+", parts[2], maxsplit=1)
        if len(teams) == 2:
            home, away = teams
        else:
            return None
    else:
        # date competition | home - away | score (or date | competition | home - away | score)
        middle = line[date_match.end():score_match.start()].strip(" |·")
        teams = re.split(r"\s+[-–]\s+", middle, maxsplit=1)
        if len(teams) != 2:
            return None
        home, away = teams
        competition = line[:date_match.start()].strip(" |·")

    home, away, competition = _clean(home), _clean(away), _clean(competition)
    if not home or not away or home.casefold() == away.casefold():
        return None
    home_score, away_score = map(int, score_match.groups())
    if home_score > 30 or away_score > 30:
        return None
    return {
        "date": match_date,
        "competition": competition or "Unknown competition",
        "home_team": home,
        "away_team": away,
        "home_score": home_score,
        "away_score": away_score,
        "section": section,
        "venue_context": "home" if section == "home_form" else "away" if section == "away_form" else "head_to_head",
        "result": "W" if home_score > away_score else "D" if home_score == away_score else "L",
        "raw_line": line.strip(),
    }



def _parse_multiline_record(lines: list[str], section: str) -> dict[str, Any] | None:
    if not lines:
        return None
    joined = " | ".join(line.strip() for line in lines if line.strip())
    inline = _parse_record(joined, section)
    if inline:
        return inline
    date_match = DATE_RE.search(lines[0])
    if not date_match:
        return None
    day, month, year = map(int, date_match.groups())
    try:
        match_date = datetime(year, month, day).date().isoformat()
    except ValueError:
        return None
    score: tuple[int, int] | None = None
    score_index = -1
    for index, line in enumerate(lines[1:], start=1):
        value = line.strip()
        combined = re.fullmatch(r"(\d{1,2})\s*[-:–]\s*(\d{1,2})", value)
        if combined:
            score = (int(combined.group(1)), int(combined.group(2)))
            score_index = index
            break
        if value.isdigit() and index + 1 < len(lines) and lines[index + 1].strip().isdigit():
            first, second = int(value), int(lines[index + 1].strip())
            if first <= 30 and second <= 30:
                score = (first, second)
                score_index = index
                break
    if score is None or score[0] > 30 or score[1] > 30:
        return None
    candidates: list[str] = []
    for raw in lines[1:score_index]:
        value = _clean(raw)
        if not value or DATE_RE.search(value) or re.fullmatch(r"\d{1,2}:\d{2}", value):
            continue
        if value.casefold() in {"w", "d", "l", "ft", "aet", "pen", "home", "away", "overall"}:
            continue
        if value.isdigit():
            continue
        if candidates and candidates[-1].casefold() == value.casefold():
            continue
        candidates.append(value)
    if len(candidates) < 2:
        return None
    home, away = candidates[-2], candidates[-1]
    competition = " ".join(candidates[:-2]).strip() or "Unknown competition"
    if home.casefold() == away.casefold():
        return None
    return {
        "date": match_date, "competition": competition,
        "home_team": home, "away_team": away,
        "home_score": score[0], "away_score": score[1],
        "section": section,
        "venue_context": "home" if section == "home_form" else "away" if section == "away_form" else "head_to_head",
        "result": "W" if score[0] > score[1] else "D" if score[0] == score[1] else "L",
        "raw_line": joined,
    }

def parse_match_history_paste(
    text: str, *, source_name: str = "manual-paste", home_team: str = "", away_team: str = ""
) -> dict[str, Any]:
    """Parse manually copied match-history text; never accesses a website."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Paste the copied match page text first.")
    if len(text) > MAX_PASTE_CHARS:
        raise ValueError(f"Paste is too large. Limit: {MAX_PASTE_CHARS:,} characters.")

    sections: dict[str, list[dict[str, Any]]] = {
        "home_form": [], "away_form": [], "h2h": []
    }
    seen: dict[str, set[tuple[Any, ...]]] = {key: set() for key in sections}
    observed_scores: dict[tuple[Any, ...], tuple[int, int, str]] = {}
    errors: list[str] = []
    current: str | None = None
    ignored_noise = 0

    pending: list[str] = []

    def flush_pending() -> None:
        nonlocal pending
        if not pending or current is None:
            pending = []
            return
        record = _parse_multiline_record(pending, current)
        pending = []
        if not record:
            return
        match_key = (record["date"], record["home_team"].casefold(), record["away_team"].casefold())
        score = (record["home_score"], record["away_score"])
        previous = observed_scores.get(match_key)
        if previous and previous[:2] != score:
            errors.append(
                f"Conflicting scores for {record['home_team']} v {record['away_team']} on {record['date']}: "
                f"{previous[0]}-{previous[1]} in {previous[2]} versus {score[0]}-{score[1]} in {current}."
            )
        else:
            observed_scores[match_key] = (score[0], score[1], current)
        identity = (*match_key, *score)
        if identity in seen[current]:
            return
        seen[current].add(identity)
        if record["competition"] == "Unknown competition":
            errors.append(
                f"{current}: competition is not present for {record['home_team']} v {record['away_team']} on {record['date']}."
            )
        if len(sections[current]) == MAX_MATCHES_PER_SECTION:
            errors.append(f"{current}: more than 35 records were present; only the first 35 were retained.")
            return
        sections[current].append(record)

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        detected = _section_for(line, home_team, away_team)
        if detected:
            flush_pending()
            current = detected
            continue
        if current is None:
            continue
        if NOISE_RE.search(line):
            ignored_noise += 1
            continue
        if DATE_RE.search(line):
            flush_pending()
            pending = [line]
        elif pending and len(pending) < 18:
            pending.append(line)
    flush_pending()

    coverage = {}
    for key, records in sections.items():
        count = len(records)
        coverage[key] = {
            "records_found": count,
            "target": MAX_MATCHES_PER_SECTION,
            "complete_to_target": count == MAX_MATCHES_PER_SECTION,
            "status": "complete" if count == MAX_MATCHES_PER_SECTION else "incomplete_or_not_supplied",
        }
        if count == 0:
            errors.append(f"{key}: no records recognised. The section may be missing or its clipboard layout is unsupported.")

    return {
        "source_name": source_name,
        "source_type": "manual_clipboard_text",
        "source_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "sections": sections,
        "coverage": coverage,
        "total_records": sum(len(records) for records in sections.values()),
        "ignored_noise_lines": ignored_noise,
        "errors": errors,
        "status": "success" if all(coverage[key]["complete_to_target"] for key in sections) and not errors
                  else "partial" if any(sections.values()) else "failed",
        "excluded_fields": ["odds", "bookmaker_names", "betting_links", "advertisements"],
    }
