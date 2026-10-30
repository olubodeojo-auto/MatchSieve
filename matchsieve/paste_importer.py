from __future__ import annotations

import hashlib
import re
from datetime import datetime
from typing import Any

MAX_PASTE_CHARS = 200_000
MAX_MATCHES_PER_SECTION = 35
SECTION_ALIASES = {
    "home_form": ("last matches: home", "last matches home", "home team last matches", "home form", "overall - home"),
    "away_form": ("last matches: away", "last matches away", "away team last matches", "away form", "overall - away"),
    "h2h": ("head-to-head matches", "head to head matches", "head-to-head", "h2h"),
}
DATE_RE = re.compile(r"(?<!\\d)(\\d{1,2})[./-](\\d{1,2})[./-](\\d{4})(?!\\d)")
SCORE_RE = re.compile(r"(?<!\\d)(\\d{1,2})\\s*[-:–]\\s*(\\d{1,2})(?!\\d)")
NOISE_RE = re.compile(r"(?i)\\b(?:odds?|bet9ja|1xbet|betking|advertisement|sponsored|casino|bonus)\\b")


def _section_for(line: str) -> str | None:
    value = re.sub(r"\\s+", " ", line.strip().lower())
    for section, aliases in SECTION_ALIASES.items():
        if any(alias in value for alias in aliases):
            return section
    return None


def _clean_line(line: str) -> str:
    line = re.sub(r"\\s+", " ", line).strip()
    line = re.sub(r"(?i)\\b(?:W|D|L|FT|AET|PEN)\\s*$", "", line).strip()
    return line.strip(" |·•")


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
    prefix = line[:date_match.start()].strip(" |·")
    middle = line[date_match.end():score_match.start()].strip(" |·")
    suffix = line[score_match.end():].strip(" |·")
    # Supported clipboard row shapes:
    # date | competition | home | score | away
    # date competition | home - away | score
    # date | competition | home - away | score
    parts = [part.strip() for part in line.split("|") if part.strip()]
    competition = ""
    home = away = ""
    if len(parts) >= 5:
        competition = parts[1]
        home = parts[2]
        away = parts[4].split()[0] if parts[4].split() else ""
    elif len(parts) >= 4:
        competition = parts[1]
        teams = parts[2]
        split = re.split(r"\\s+[-–]\\s+", teams, maxsplit=1)
        if len(split) == 2:
            home, away = split
        else:
            home = teams
            away = parts[3]
    else:
        # Inline text is accepted only when the teams are explicitly separated by " - ".
        team_text = middle
        split = re.split(r"\\s+[-–]\\s+", team_text, maxsplit=1)
        if len(split) == 2:
            home, away = split
            competition = prefix
        else:
            # "date competition home score away" is ambiguous; do not guess team boundaries.
            return None
    home = _clean_line(home)
    away = _clean_line(away)
    competition = _clean_line(competition) or "Unknown competition"
    if not home or not away or home.lower() == away.lower():
        return None
    hs, aws = map(int, score_match.groups())
    if hs > 30 or aws > 30:
        return None
    return {
        "date": match_date,
        "competition": competition,
        "home_team": home,
        "away_team": away,
        "home_score": hs,
        "away_score": aws,
        "section": section,
        "venue_context": "home" if section == "home_form" else "away" if section == "away_form" else "head_to_head",
        "result": "W" if hs > aws else "D" if hs == aws else "L",
        "raw_line": line.strip(),
    }


def parse_match_history_paste(text: str, *, source_name: str = "manual-paste") -> dict[str, Any]:
    """Parse manually copied match-history sections. No network access or website scraping."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Paste the copied match page text first.")
    if len(text) > MAX_PASTE_CHARS:
        raise ValueError(f"Paste is too large. Limit: {MAX_PASTE_CHARS:,} characters.")
    sections: dict[str, list[dict[str, Any]]] = {key: [] for key in SECTION_ALIASES}
    errors: list[str] = []
    current: str | None = None
    ignored_noise = 0
    seen: dict[str, set[tuple[str, str, str, int, int]]] = {key: set() for key in sections}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        detected = _section_for(line)
        if detected:
            current = detected
            continue
        if current is None:
            continue
        if NOISE_RE.search(line):
            ignored_noise += 1
            continue
        record = _parse_record(line, current)
        if not record:
            continue
        identity = (record["date"], record["home_team"].casefold(), record["away_team"].casefold(),
                    record["home_score"], record["away_score"])
        if identity in seen[current]:
            continue
        seen[current].add(identity)
        sections[current].append(record)
        if len(sections[current]) > MAX_MATCHES_PER_SECTION:
            sections[current] = sections[current][:MAX_MATCHES_PER_SECTION]
            errors.append(f"{current}: more than 35 records were present; only the first 35 were retained.")
            break
    coverage = {}
    for key, records in sections.items():
        count = len(records)
        coverage[key] = {
            "records_found": count,
            "target": MAX_MATCHES_PER_SECTION,
            "complete_to_target": count >= MAX_MATCHES_PER_SECTION,
            "status": "complete" if count >= MAX_MATCHES_PER_SECTION else "incomplete_or_not_supplied",
        }
        if count == 0:
            errors.append(f"{key}: no records recognised. The section may be missing or its clipboard layout is not supported.")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return {
        "source_name": source_name,
        "source_type": "manual_clipboard_text",
        "source_sha256": digest,
        "sections": sections,
        "coverage": coverage,
        "total_records": sum(map(len, sections.values())),
        "ignored_noise_lines": ignored_noise,
        "errors": errors,
        "status": "success" if all(sections.values()) and not errors else "partial" if any(sections.values()) else "failed",
        "excluded_fields": ["odds", "bookmaker_names", "betting_links", "advertisements"],
    }
