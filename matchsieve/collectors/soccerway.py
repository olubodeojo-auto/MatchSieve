from __future__ import annotations

"""First-class Soccerway match-page adapter.

The adapter discovers the known tabs for one match, extracts structured fields
where a stable DOM structure is present, preserves source snapshots, and records
missing fields rather than inferring them. It does not bypass access controls.
"""

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


PAGE_LIMIT = 9
TEXT_LIMIT = 60_000
KNOWN_ROUTES: tuple[tuple[str, str], ...] = (
    ("summary", ""),
    ("report", "report/"),
    ("odds", "odds/"),
    ("h2h", "h2h/"),
    ("standings", "standings/"),
    ("stats", "summary/stats/"),
    ("lineups", "summary/lineups/"),
    ("player_stats", "summary/player-stats/"),
    ("commentary", "summary/commentary/"),
)
SECTION_WORDS = {
    "stats": ("stats", "statistics"),
    "lineups": ("lineup", "line-up", "team sheet"),
    "player_stats": ("player stats", "player-stat", "player statistics"),
    "commentary": ("commentary", "events", "timeline"),
    "h2h": ("h2h", "head-to-head", "head to head"),
    "odds": ("odds",),
    "standings": ("standings", "table"),
    "report": ("report", "match report"),
    "summary": ("summary", "overview", "match"),
}
# Explicit, source-specific DOM selector families. Soccerway may change its
# classes; each result stores the selector that produced it so extraction can
# be audited instead of silently trusting a generic body-text scrape.
DOM_SELECTOR_GROUPS = {
    "home_team": (
        "[data-testid*='home-team' i]", "[class*='home-team-name' i]",
        "[class*='homeTeam' i] [class*='name' i]", ".home .team-name",
        ".home-team a[href*='/team/']",
    ),
    "away_team": (
        "[data-testid*='away-team' i]", "[class*='away-team-name' i]",
        "[class*='awayTeam' i] [class*='name' i]", ".away .team-name",
        ".away-team a[href*='/team/']",
    ),
    "team_names": ("[class*='team-name' i]", "[data-testid*='team-name' i]"),
    "home_score": ("[data-testid*='home-score' i]", "[class*='home-score' i]", "[class*='homeScore' i]"),
    "away_score": ("[data-testid*='away-score' i]", "[class*='away-score' i]", "[class*='awayScore' i]"),
    "score": ("[data-testid*='score' i]", "[class*='score' i]", "[class*='result' i]"),
    "kickoff": ("time[datetime]", "[data-testid*='kickoff' i]", "[class*='kickoff' i]", "[class*='match-date' i]"),
    "competition": (
        "nav[aria-label*='breadcrumb' i] a", "ol[class*='breadcrumb' i] a",
        "[class*='competition' i] a", "a[href*='/competition/']",
    ),
    "venue": ("[data-testid*='venue' i]", "[class*='venue' i]", "[class*='stadium' i]"),
}
STAT_ALIASES = {
    "expected goals": "xg",
    "expected goals (xg)": "xg",
    "xg": "xg",
    "expected goals on target": "xgot",
    "xgot": "xgot",
    "ball possession": "possession",
    "possession": "possession",
    "total shots": "shots",
    "shots": "shots",
    "shots on target": "shots_on_target",
    "shots off target": "shots_off_target",
    "corner kicks": "corners",
    "corners": "corners",
    "fouls": "fouls",
    "yellow cards": "yellow_cards",
    "red cards": "red_cards",
    "offsides": "offsides",
    "goalkeeper saves": "saves",
    "saves": "saves",
}
EVENT_WORDS = re.compile(
    r"\b(goal|penalty|own goal|yellow card|red card|substitution|substituted|"
    r"booking|sent off|missed penalty)\b",
    re.IGNORECASE,
)
MINUTE_MARK = re.compile(r"\b\d{1,3}(?:\+\d{1,2})?\s*['’′]")


class SoccerwayAdapter:
    """Collect one Soccerway match and its known tabs into one provenance record."""

    name = "soccerway"
    authority = "source_capture_and_extraction_only"

    def __init__(
        self,
        *,
        timeout_ms: int = 25_000,
        max_pages: int = PAGE_LIMIT,
        delay_seconds: float = 0.8,
        headless: bool = True,
    ) -> None:
        self.timeout_ms = max(1_000, int(timeout_ms))
        self.max_pages = max(1, min(int(max_pages), PAGE_LIMIT))
        self.delay_seconds = max(0.0, float(delay_seconds))
        self.headless = bool(headless)

    @staticmethod
    def validate_url(url: str) -> str:
        """Validate a match/game URL and return the base URL for this fixture."""
        parsed = urlparse((url or "").strip())
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in {"http", "https"} or not host:
            raise ValueError("Soccerway URL must be an absolute HTTP(S) URL.")
        if host != "soccerway.com" and not host.endswith(".soccerway.com"):
            raise ValueError("Only Soccerway URLs are accepted by this adapter.")
        segments = [part for part in parsed.path.split("/") if part]
        if len(segments) < 3 or segments[0].lower() not in {"match", "game"}:
            raise ValueError("URL must point to a Soccerway match/game page.")
        base_segments = segments[:3]
        base_path = "/" + "/".join(base_segments) + "/"
        return urlunparse((parsed.scheme, parsed.netloc, base_path, "", parsed.query, ""))

    @staticmethod
    def _base_and_identity(url: str) -> tuple[str, str]:
        base = SoccerwayAdapter.validate_url(url)
        p = urlparse(base)
        return base, "/".join([part for part in p.path.split("/") if part][:3]).lower()

    @staticmethod
    def _same_match(candidate_url: str, base_url: str) -> bool:
        try:
            base, identity = SoccerwayAdapter._base_and_identity(base_url)
            candidate_base, candidate_identity = SoccerwayAdapter._base_and_identity(candidate_url)
            if urlparse(candidate_url).hostname != urlparse(base).hostname:
                # Keep link discovery on the exact locale host supplied by the caller.
                return False
            if candidate_identity == identity:
                return True
            source_mid = parse_qs(urlparse(base).query).get("mid", [None])[0]
            candidate_mid = parse_qs(urlparse(candidate_url).query).get("mid", [None])[0]
            return bool(source_mid and candidate_mid and source_mid == candidate_mid)
        except ValueError:
            return False

    @staticmethod
    def _page_type(label: str, url: str, base_url: str) -> str | None:
        p, bp = urlparse(url), urlparse(base_url)
        if p.hostname != bp.hostname:
            return None
        label_path = (label + " " + p.path).lower()
        base_path = bp.path.rstrip("/")
        candidate_path = p.path.rstrip("/")
        if candidate_path == base_path:
            return "summary"
        # More specific labels/paths must win before broad "stats" matches.
        priorities = ("player_stats", "lineups", "commentary", "stats", "h2h", "odds", "standings", "report", "summary")
        for page_type in priorities:
            if any(word in label_path for word in SECTION_WORDS[page_type]):
                if SoccerwayAdapter._same_match(url, base_url):
                    return page_type
        return None

    @classmethod
    def discover_page_urls(cls, base_url: str, anchors: list[dict[str, str]]) -> list[dict[str, str]]:
        """Return deduplicated known tabs in a stable order, then known route fallbacks."""
        base, _ = cls._base_and_identity(base_url)
        found: dict[str, dict[str, str]] = {
            "summary": {"page_type": "summary", "url": base, "link_label": "Match overview"}
        }
        for anchor in anchors:
            href = (anchor.get("href") or "").strip()
            label = (anchor.get("label") or anchor.get("text") or "").strip()
            if not href:
                continue
            absolute = urljoin(base, href)
            if not cls._same_match(absolute, base):
                continue
            ptype = cls._page_type(label, absolute, base)
            if ptype and ptype not in found:
                found[ptype] = {"page_type": ptype, "url": absolute, "link_label": label or ptype}
        parsed = urlparse(base)
        query = parsed.query
        for ptype, route in KNOWN_ROUTES:
            if ptype in found or not route:
                continue
            candidate = urlunparse(
                (parsed.scheme, parsed.netloc, parsed.path + route, "", query, "")
            )
            found[ptype] = {"page_type": ptype, "url": candidate, "link_label": "Known-route fallback"}
        ordered = [found[k] for k, _ in KNOWN_ROUTES if k in found]
        return ordered

    def collect(self, url: str) -> dict[str, Any]:
        base_url = self.validate_url(url)
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError(
                "The Soccerway adapter requires Playwright. Run 'python -m pip install playwright' "
                "and 'python -m playwright install chromium'. The adapter is part of MatchSieve."
            ) from exc

        pages: list[dict[str, Any]] = []
        errors: list[str] = []
        warnings: list[str] = []
        blocked = False
        root_anchors: list[dict[str, str]] = []
        seen_urls: set[str] = set()
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=self.headless)
            context = browser.new_context(locale="en-GB")
            page = context.new_page()
            page.set_default_timeout(self.timeout_ms)
            try:
                try:
                    response = page.goto(base_url, wait_until="domcontentloaded")
                    first = self._capture_page(page, response, "summary", "Match overview")
                    pages.append(first)
                    seen_urls.add(self._normalise_url(page.url))
                    if first["http_status"] in {403, 429} or first["access_blocked"]:
                        blocked = True
                        warnings.append("Soccerway denied or rate-limited the request; collection stopped without retries.")
                    else:
                        root_anchors = self._anchors(page)
                except Exception as exc:
                    errors.append(f"Match overview navigation failed: {type(exc).__name__}: {exc}")

                if not blocked and pages:
                    candidates = self.discover_page_urls(base_url, root_anchors)
                    for item in candidates:
                        if len(pages) >= self.max_pages:
                            break
                        candidate = item["url"]
                        normalised = self._normalise_url(candidate)
                        if normalised in seen_urls:
                            continue
                        if not self._same_match(candidate, base_url):
                            warnings.append(f"Rejected out-of-match route: {candidate}")
                            continue
                        if self.delay_seconds:
                            time.sleep(self.delay_seconds)
                        try:
                            response = page.goto(candidate, wait_until="domcontentloaded")
                            status = response.status if response else None
                            if status in {403, 429}:
                                blocked = True
                                warnings.append(
                                    f"Collection stopped after HTTP {status} on {candidate}; no access-control bypass attempted."
                                )
                                break
                            if status is not None and status >= 400:
                                warnings.append(f"Tab unavailable (HTTP {status}): {candidate}")
                                continue
                            captured = self._capture_page(page, response, item["page_type"], item["link_label"])
                            if captured["access_blocked"]:
                                blocked = True
                                warnings.append("A challenge/access-control page was detected; collection stopped.")
                                break
                            pages.append(captured)
                            seen_urls.add(self._normalise_url(page.url))
                        except Exception as exc:
                            errors.append(f"{item['page_type']} tab failed: {type(exc).__name__}: {exc}")
                else:
                    if not pages:
                        errors.append("No match page could be captured.")
            finally:
                context.close()
                browser.close()

        aggregate = self._aggregate(pages, base_url)
        captured_at = utc_now()
        raw_payload = {
            "adapter": self.name,
            "page_types_seen": [x["page_type"] for x in pages],
            "pages": pages,
            "statistics": aggregate["statistics"],
            "lineups": aggregate["lineups"],
            "events": aggregate["events"],
            "player_links": aggregate["player_links"],
            "missing_fields": aggregate["missing_fields"],
            "warnings": warnings,
        }
        facts = {k: v for k, v in aggregate["match"].items() if v not in (None, "", [], {})}
        facts["source_ref"] = base_url
        serialised = json.dumps({"facts": facts, "payload": raw_payload}, sort_keys=True, ensure_ascii=False, default=str)
        record_id = hashlib.sha256(f"{base_url}|{serialised}".encode("utf-8")).hexdigest()
        status = "blocked" if blocked else ("success" if pages and facts.get("home_team") and facts.get("away_team") else ("partial" if pages else "failed"))
        return {
            "agent": "data_collection",
            "adapter": self.name,
            "source": "Soccerway",
            "source_url": base_url,
            "captured_at": captured_at,
            "records": [{
                "record_id": record_id,
                "source": "Soccerway",
                "source_url": base_url,
                "captured_at": captured_at,
                "facts": facts,
                "raw_payload": raw_payload,
            }] if pages else [],
            "pages": pages,
            "records_collected": 1 if pages else 0,
            "errors": errors,
            "warnings": warnings,
            "status": status,
            "authority": self.authority,
        }

    @staticmethod
    def _normalise_url(url: str) -> str:
        p = urlparse(url)
        query = urlencode(sorted(parse_qs(p.query, keep_blank_values=True).items()), doseq=True)
        return urlunparse((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/") + "/", "", query, ""))

    @staticmethod
    def _anchors(page: Any) -> list[dict[str, str]]:
        output: list[dict[str, str]] = []
        links = page.locator("a[href]")
        for index in range(min(links.count(), 400)):
            link = links.nth(index)
            try:
                href = link.get_attribute("href") or ""
                label = (link.inner_text(timeout=700) or "").strip()
                if href:
                    output.append({"href": href, "label": label[:100]})
            except Exception:
                continue
        return output

    def _capture_page(self, page: Any, response: Any, page_type: str, link_label: str) -> dict[str, Any]:
        # Some tabs hydrate after DOMContentLoaded. A short, bounded settling
        # period is safer than waiting for network-idle on a busy scores site.
        try:
            page.wait_for_timeout(650)
        except Exception:
            pass
        text = ""
        try:
            text = page.locator("body").inner_text(timeout=self.timeout_ms)
        except Exception:
            pass
        text = text[:TEXT_LIMIT]
        title = ""
        try:
            title = page.title() or ""
        except Exception:
            pass
        status = response.status if response else None
        lowered = (title + "\n" + text[:12_000]).lower()
        access_blocked = any(token in lowered for token in (
            "verify you are human", "checking your browser", "captcha", "access denied",
            "unusual traffic", "temporarily blocked"
        ))
        tables = self._table_rows(page)
        stats = self._stats_from_rows(tables)
        players = self._player_links(page) if page_type in {"lineups", "player_stats", "summary"} else []
        events = self._event_rows(page, text) if page_type in {"commentary", "summary", "report"} else []
        structured = self._json_ld(page)
        headings = self._headings(page)
        dom_fields = self._dom_fields(page)
        return {
            "page_type": page_type,
            "link_label": link_label,
            "url": page.url,
            "http_status": status,
            "captured_at": utc_now(),
            "title": title[:500],
            "headings": headings[:30],
            "dom_fields": dom_fields,
            "text": text,
            "table_rows": tables[:300],
            "statistics": stats,
            "players": players[:80],
            "events": events[:100],
            "json_ld": structured[:10],
            "access_blocked": access_blocked,
        }

    @staticmethod
    def _dom_fields(page: Any) -> dict[str, list[dict[str, str]]]:
        """Extract field candidates via explicit selector families, with provenance."""
        output: dict[str, list[dict[str, str]]] = {}
        for field, selectors in DOM_SELECTOR_GROUPS.items():
            candidates: list[dict[str, str]] = []
            seen: set[str] = set()
            for selector in selectors:
                loc = page.locator(selector)
                for index in range(min(loc.count(), 12)):
                    try:
                        node = loc.nth(index)
                        value = node.get_attribute("datetime") if field == "kickoff" else None
                        value = value or (node.inner_text(timeout=450) or "").strip()
                        value = re.sub(r"\s+", " ", value).strip()
                        if not value or value in seen:
                            continue
                        seen.add(value)
                        candidates.append({"value": value[:240], "selector": selector})
                    except Exception:
                        continue
                if field in {"home_team", "away_team", "kickoff", "venue"} and candidates:
                    break
            if candidates:
                output[field] = candidates
        return output

    @staticmethod
    def _headings(page: Any) -> list[str]:
        result: list[str] = []
        for selector in ("h1", "h2", "h3"):
            loc = page.locator(selector)
            for i in range(min(loc.count(), 30)):
                try:
                    value = (loc.nth(i).inner_text(timeout=500) or "").strip()
                    if value and value not in result:
                        result.append(value[:240])
                except Exception:
                    continue
        return result

    @staticmethod
    def _table_rows(page: Any) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        rows = page.locator("table tr")
        for i in range(min(rows.count(), 500)):
            row = rows.nth(i)
            try:
                cells = [x.strip() for x in row.locator("th,td").all_inner_texts()]
                cells = [x for x in cells if x]
                if cells:
                    result.append({"cells": cells[:12], "text": " | ".join(cells)[:500]})
            except Exception:
                continue
        return result

    @staticmethod
    def _stats_from_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
        stats: dict[str, dict[str, str]] = {}
        for row in rows:
            cells = row.get("cells") or []
            if len(cells) < 3:
                continue
            label = re.sub(r"\s+", " ", str(cells[0]).strip()).lower()
            key = STAT_ALIASES.get(label)
            if not key:
                continue
            # Only a row containing a label plus two explicit side values is accepted.
            home, away = str(cells[-2]).strip(), str(cells[-1]).strip()
            if home and away:
                stats[key] = {"home": home, "away": away, "source_label": str(cells[0])}
        return stats

    @staticmethod
    def _player_links(page: Any) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        links = page.locator('a[href*="/player/"], a[href*="/players/"]')
        seen: set[str] = set()
        for i in range(min(links.count(), 250)):
            link = links.nth(i)
            try:
                name = re.sub(r"\s+", " ", (link.inner_text(timeout=500) or "").strip())
                href = link.get_attribute("href") or ""
                if not name or not href:
                    continue
                absolute = urljoin(page.url, href)
                if absolute not in seen:
                    seen.add(absolute)
                    result.append({"name": name[:120], "url": absolute})
            except Exception:
                continue
        return result

    @staticmethod
    def _event_rows(page: Any, body_text: str) -> list[dict[str, str]]:
        candidates: list[str] = []
        for selector in ("table tr", "li", '[class*="event"]', '[class*="incident"]', '[class*="timeline"]'):
            nodes = page.locator(selector)
            for i in range(min(nodes.count(), 300)):
                try:
                    value = re.sub(r"\s+", " ", (nodes.nth(i).inner_text(timeout=350) or "").strip())
                    if value and len(value) <= 500 and MINUTE_MARK.search(value) and EVENT_WORDS.search(value):
                        candidates.append(value)
                except Exception:
                    continue
        result: list[dict[str, str]] = []
        seen: set[str] = set()
        for line in candidates:
            if line not in seen:
                seen.add(line)
                kind = "goal" if re.search(r"\b(?:goal|own goal|penalty|missed penalty)\b", line, re.I) else (
                    "card" if re.search(r"\b(?:yellow card|red card|booking|sent off)\b", line, re.I) else (
                    "substitution" if re.search(r"\bsubstitut(?:ion|ed)\b", line, re.I) else "event"))
                result.append({"kind": kind, "text": line})
        if not result:
            for line in body_text.splitlines():
                value = re.sub(r"\s+", " ", line.strip())
                if value and len(value) < 220 and MINUTE_MARK.search(value) and EVENT_WORDS.search(value):
                    result.append({"kind": "event", "text": value})
                    if len(result) >= 100:
                        break
        return result[:100]

    @staticmethod
    def _json_ld(page: Any) -> list[Any]:
        result: list[Any] = []
        scripts = page.locator('script[type="application/ld+json"]')
        for i in range(min(scripts.count(), 30)):
            try:
                raw = (scripts.nth(i).inner_text(timeout=500) or "").strip()
                if not raw or len(raw) > 500_000:
                    continue
                parsed = json.loads(raw)
                result.append(parsed)
            except Exception:
                continue
        return result

    @staticmethod
    def _from_json_ld(pages: list[dict[str, Any]]) -> dict[str, Any]:
        output: dict[str, Any] = {}

        def walk(value: Any) -> None:
            if isinstance(value, dict):
                kind = value.get("@type")
                types = kind if isinstance(kind, list) else [kind]
                if any(str(t).lower() in {"sportsEvent".lower(), "event"} for t in types if t):
                    home = value.get("homeTeam") or value.get("competitor")
                    away = value.get("awayTeam")
                    for key, item in (("home_team", home), ("away_team", away)):
                        if isinstance(item, dict):
                            item = item.get("name")
                        if isinstance(item, str) and item.strip():
                            output.setdefault(key, item.strip())
                    start = value.get("startDate")
                    if start:
                        output.setdefault("kickoff", start)
                    location = value.get("location")
                    if isinstance(location, dict) and location.get("name"):
                        output.setdefault("venue", location["name"])
                    league = value.get("superEvent")
                    if isinstance(league, dict) and league.get("name"):
                        output.setdefault("competition", league["name"])
                for nested in value.values():
                    walk(nested)
            elif isinstance(value, list):
                for item in value:
                    walk(item)

        for page in pages:
            for item in page.get("json_ld", []):
                walk(item)
        return output

    @classmethod
    def _aggregate(cls, pages: list[dict[str, Any]], source_url: str) -> dict[str, Any]:
        match: dict[str, Any] = cls._from_json_ld(pages)
        for item in pages:
            title = item.get("title") or ""
            headings = item.get("headings") or []
            body_text = item.get("text") or ""
            dom = item.get("dom_fields") or {}
            if not match.get("home_team"):
                exact = dom.get("home_team") or []
                if exact:
                    match["home_team"] = exact[0]["value"]
            if not match.get("away_team"):
                exact = dom.get("away_team") or []
                if exact:
                    match["away_team"] = exact[0]["value"]
            team_candidates = [x["value"] for x in (dom.get("team_names") or [])]
            if not (match.get("home_team") and match.get("away_team")) and len(team_candidates) >= 2:
                if not match.get("home_team"):
                    match["home_team"] = team_candidates[0]
                if not match.get("away_team"):
                    match["away_team"] = team_candidates[1]
            for candidate in [*headings, title]:
                pair = cls._teams_from_title(str(candidate))
                if pair and not (match.get("home_team") and match.get("away_team")):
                    match["home_team"], match["away_team"] = pair
                    break
            if not match.get("competition"):
                comp = dom.get("competition") or []
                exact_competition = next(
                    (x["value"] for x in comp if "/competition/" in x.get("selector", "")),
                    None,
                )
                match["competition"] = exact_competition or (comp[-1]["value"] if comp else cls._competition_from_page(item))
            if not match.get("kickoff"):
                times = dom.get("kickoff") or []
                if times:
                    match["kickoff"] = times[0]["value"]
                    match["kickoff_time_basis"] = "Soccerway DOM datetime/display value; timezone not confirmed"
            if not match.get("venue"):
                venues = dom.get("venue") or []
                if venues:
                    match["venue"] = venues[0]["value"]
            for score_field in ("home_score", "away_score"):
                if match.get(score_field) is None:
                    for candidate in (dom.get(score_field) or []):
                        score_value = re.fullmatch(r"\s*(\d{1,2})\s*", candidate["value"])
                        if score_value:
                            match[score_field] = int(score_value.group(1))
                            break
            if match.get("home_score") is None and match.get("away_score") is None:
                for candidate in (dom.get("score") or []):
                    score = re.search(r"(?<!\d)(\d{1,2})\s*[-–:]\s*(\d{1,2})(?!\d)", candidate["value"])
                    if score:
                        if match.get("home_score") is None:
                            match["home_score"] = int(score.group(1))
                        if match.get("away_score") is None:
                            match["away_score"] = int(score.group(2))
                        if match.get("home_score") is not None and match.get("away_score") is not None:
                            break
            if not match.get("kickoff"):
                kickoff = re.search(
                    r"\b(\d{1,2}[./-]\d{1,2}[./-]\d{4}(?:\s+\d{1,2}:\d{2})?)\b",
                    title + "\n" + body_text,
                )
                if kickoff:
                    # Keep the site-displayed time as-is; don't silently relabel it UTC.
                    match["kickoff"] = kickoff.group(1)
                    match["kickoff_time_basis"] = "Soccerway displayed local/site time; timezone not confirmed"
            if not match.get("status"):
                for status in ("Full-time", "Finished", "Live", "Half-time", "Postponed", "Cancelled", "Not started", "Scheduled"):
                    if re.search(r"\b" + re.escape(status) + r"\b", body_text, re.I):
                        match["status"] = status
                        break
            if not match.get("venue"):
                venue = re.search(r"\b(?:Venue|Stadium)\s*:?\s*([^\n]{2,100})", body_text, re.I)
                if venue:
                    match["venue"] = venue.group(1).strip()
            if match.get("home_score") is None and match.get("away_score") is None:
                for row in item.get("table_rows", []):
                    cells = row.get("cells") or []
                    if len(cells) == 1:
                        score = re.fullmatch(r"\s*(\d{1,2})\s*[-–:]\s*(\d{1,2})\s*", str(cells[0]))
                        if score:
                            match["home_score"], match["away_score"] = int(score.group(1)), int(score.group(2))
                            break
        stats: dict[str, dict[str, str]] = {}
        lineups: list[dict[str, str]] = []
        events: list[dict[str, str]] = []
        players: list[dict[str, str]] = []
        for item in pages:
            stats.update(item.get("statistics") or {})
            if item.get("page_type") == "lineups":
                lineups = item.get("players") or []
            players.extend(item.get("players") or [])
            events.extend(item.get("events") or [])
        deduped_players, seen_players = [], set()
        for player in players:
            key = (player.get("name"), player.get("url"))
            if key not in seen_players:
                seen_players.add(key)
                deduped_players.append(player)
        event_items, seen_events = [], set()
        for event in events:
            key = event.get("text")
            if key and key not in seen_events:
                seen_events.add(key)
                event_items.append(event)
        missing = [field for field in ("home_team", "away_team", "competition", "kickoff") if not match.get(field)]
        if not stats:
            missing.append("statistics_not_published_or_not_extracted")
        if not lineups:
            missing.append("lineups_not_published_or_not_extracted")
        if not event_items:
            missing.append("events_not_published_or_not_extracted")
        match["source_time_basis"] = "site_display_value; not assumed UTC" if match.get("kickoff") else None
        match["source_url"] = source_url
        return {
            "match": match,
            "statistics": stats,
            "lineups": lineups,
            "events": event_items[:100],
            "player_links": deduped_players[:120],
            "missing_fields": missing,
        }

    @staticmethod
    def _teams_from_title(text: str) -> tuple[str, str] | None:
        value = re.sub(r"\s+", " ", text).strip()
        if not value:
            return None
        value = re.split(r"\s*[|]\s*", value, maxsplit=1)[0]
        value = re.sub(r"\s+(?:live scores?|live score|lineups?|stats|statistics|commentary|head-to-head|h2h|match info|game info).*$", "", value, flags=re.I)
        value = re.sub(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b", "", value).strip(" -–|")
        pair = re.search(r"^(.+?)\s+(?:v|vs\.?|versus)\s+(.+?)$", value, re.I)
        if not pair:
            return None
        home, away = pair.group(1).strip(" -–|"), pair.group(2).strip(" -–|")
        if not home or not away or len(home) > 100 or len(away) > 100:
            return None
        return home, away

    @staticmethod
    def _competition_from_page(item: dict[str, Any]) -> str | None:
        for row in item.get("table_rows", []):
            text = row.get("text", "")
            if re.search(r"\b(league|cup|championship|premier|bundesliga|liga|serie a|division)\b", text, re.I) and len(text) < 120:
                return text
        for heading in item.get("headings", []):
            if re.search(r"\b(league|cup|championship|premier|bundesliga|liga|serie a|division)\b", heading, re.I):
                return heading
        return None
