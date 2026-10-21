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


PAGE_LIMIT = 16
TEXT_LIMIT = 60_000
FIXTURE_LINK_LIMIT = 500
TEAM_FORM_TARGET = 30
H2H_TARGET = 15
HISTORY_EXPANSION_CLICKS = 4
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
    def validate_match_list_url(url: str) -> str:
        """Validate a Soccerway day/matches/fixtures/results list URL."""
        parsed = urlparse((url or "").strip())
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in {"http", "https"} or not host:
            raise ValueError("Soccerway fixture-list URL must be an absolute HTTP(S) URL.")
        if host != "soccerway.com" and not host.endswith(".soccerway.com"):
            raise ValueError("Only Soccerway fixture-list URLs are accepted.")
        lowered = parsed.path.lower()
        looks_like_list = (
            parsed.path.rstrip("/") == ""
            or any(word in lowered for word in ("matches", "fixtures", "results"))
        )
        if not looks_like_list:
            raise ValueError("URL must point to a Soccerway date/matches/fixtures/results listing.")
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", parsed.query, ""))

    @staticmethod
    def _label_kind(label: str) -> str | None:
        value = re.sub(r"\s+", " ", (label or "")).strip().lower()
        team_form_patterns = (
            "home form", "away form", "home & away", "overall", "last matches",
            "previous matches", "recent matches", "last games", "recent form",
        )
        h2h_patterns = (
            "last meetings", "previous meetings", "head-to-head", "head to head",
            "h2h meetings", "direct meetings", "previous encounters",
        )
        # Classify a clear section before broad "show more" controls.
        if any(word in value for word in h2h_patterns):
            return "h2h_meetings"
        if any(word in value for word in team_form_patterns):
            return "team_form"
        if any(word in value for word in ("show more", "load more", "more matches", "view more", "see more")):
            return "expand_history"
        return None

    @staticmethod
    def _expand_control_text(node: Any) -> str:
        parts = []
        for attribute in ("aria-label", "title", "data-testid", "data-qa"):
            try:
                value = node.get_attribute(attribute)
                if value:
                    parts.append(value)
            except Exception:
                pass
        try:
            value = node.inner_text(timeout=350)
            if value:
                parts.append(value)
        except Exception:
            pass
        return re.sub(r"\s+", " ", " ".join(parts)).strip().lower()

    @classmethod
    def _expand_control_section_kind(cls, node: Any, page: Any) -> str | None:
        """Classify expansion controls by nearest section and, where possible, team."""
        home_team = away_team = ""
        try:
            pair = cls._teams_from_title(page.title() or "")
            if pair:
                home_team, away_team = pair[0].lower(), pair[1].lower()
        except Exception:
            pass
        for depth in range(1, 9):
            try:
                ancestor = node.locator(f"xpath=ancestor::*[{depth}]")
                text_value = re.sub(r"\s+", " ", (ancestor.inner_text(timeout=350) or "")).strip().lower()
                if not text_value or len(text_value) > 10_000:
                    continue
                has_home = bool(home_team and home_team in text_value)
                has_away = bool(away_team and away_team in text_value)
                has_team_label = any(word in text_value for word in ("last matches", "previous matches", "recent matches", "home form", "away form", "recent form"))
                has_h2h_label = any(word in text_value for word in ("last meetings", "previous meetings", "head-to-head", "head to head", "direct meetings", "previous encounters"))
                if has_h2h_label and not has_team_label:
                    return "h2h_meetings"
                if has_team_label and not has_h2h_label:
                    if has_home and not has_away:
                        return "home_team_last_matches"
                    if has_away and not has_home:
                        return "away_team_last_matches"
                    return "team_form"
            except Exception:
                continue
        return None

    @classmethod
    def _expand_history_panels(cls, page: Any, page_type: str, max_clicks: int = HISTORY_EXPANSION_CLICKS) -> dict[str, Any]:
        """Expand each team's recent matches and direct H2H meetings separately."""
        clicks = {
            "home_team_last_matches": 0,
            "away_team_last_matches": 0,
            "team_form": 0,
            "h2h_meetings": 0,
            "unclassified": 0,
        }
        warnings: list[str] = []
        if page_type != "h2h":
            return {"clicks": clicks, "warnings": warnings}

        targets = ("home_team_last_matches", "away_team_last_matches", "team_form", "h2h_meetings")
        click_limit = max(0, min(int(max_clicks), HISTORY_EXPANSION_CLICKS))
        for target in targets:
            for _ in range(click_limit):
                clicked = False
                for selector in ("button", "a", "[role='button']", "summary"):
                    nodes = page.locator(selector)
                    for index in range(min(nodes.count(), 500)):
                        node = nodes.nth(index)
                        label = cls._expand_control_text(node)
                        if cls._label_kind(label) != "expand_history":
                            continue
                        section_kind = cls._expand_control_section_kind(node, page)
                        if section_kind != target:
                            continue
                        try:
                            node.scroll_into_view_if_needed(timeout=800)
                            node.click(timeout=1000)
                            page.wait_for_timeout(350)
                            clicks[target] += 1
                            clicked = True
                            break
                        except Exception as exc:
                            warnings.append(f"{target} expand control did not open: {type(exc).__name__}")
                    if clicked:
                        break
                if not clicked:
                    break

        if clicks["home_team_last_matches"] == 0 and clicks["away_team_last_matches"] == 0 and clicks["team_form"] == 0:
            warnings.append("No section-specific team-form expansion could be verified; available form history may be limited.")
        if clicks["h2h_meetings"] == 0:
            warnings.append("No section-specific direct-meetings expansion could be verified; available H2H history may be limited.")
        return {"clicks": clicks, "warnings": warnings}

    @staticmethod
    def validate_url(url: str) -> str:
        """Validate a visible match URL. Accept locale-prefixed and /football/match/ routes."""
        parsed = urlparse((url or "").strip())
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in {"http", "https"} or not host:
            raise ValueError("Match URL must be an absolute HTTP(S) URL.")
        if host != "soccerway.com" and not host.endswith(".soccerway.com"):
            raise ValueError("Only Soccerway match URLs are accepted.")
        segments = [part for part in parsed.path.split("/") if part]
        lower = [part.lower() for part in segments]
        try:
            index = max(i for i, value in enumerate(lower) if value in {"match", "game"})
        except ValueError:
            raise ValueError("URL must point to a Soccerway match/game page.") from None
        if len(segments) < index + 3:
            raise ValueError("Soccerway match URL does not contain both team identifiers.")
        match_segments = segments[:index + 3]
        base_path = "/" + "/".join(match_segments) + "/"
        return urlunparse((parsed.scheme, parsed.netloc, base_path, "", parsed.query, ""))

    @staticmethod
    def _base_and_identity(url: str) -> tuple[str, str]:
        base = SoccerwayAdapter.validate_url(url)
        p = urlparse(base)
        parts = [part for part in p.path.split("/") if part]
        match_index = max(i for i, part in enumerate(parts) if part.lower() in {"match", "game"})
        return base, "/".join(parts[match_index:match_index + 3]).lower()

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
            # Keep the actual tab href including its query/session identifiers.
            # Guessed route patterns are added only when the current page exposes no tab.
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

    def collect_fixtures_for_date(self, url: str, *, max_fixtures: int = FIXTURE_LINK_LIMIT) -> dict[str, Any]:
        """Collect a date's complete accessible fixture list, preserving visible competition groups."""
        list_url = self.validate_match_list_url(url)
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError(
                "The Soccerway adapter requires Playwright. Run 'python -m pip install playwright' "
                "and 'python -m playwright install chromium'."
            ) from exc

        warnings: list[str] = []
        errors: list[str] = []
        fixtures: list[dict[str, Any]] = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=self.headless)
            context = browser.new_context(locale="en-GB")
            page = context.new_page()
            page.set_default_timeout(self.timeout_ms)
            try:
                response = page.goto(list_url, wait_until="domcontentloaded")
                try:
                    page.locator("a[href*='/match/'], a[href*='/game/']").first.wait_for(
                        state="attached", timeout=min(self.timeout_ms, 6500)
                    )
                except Exception:
                    # Some match-list dates genuinely have no fixtures; continue to capture
                    # the visible page and report the gap rather than guessing.
                    page.wait_for_timeout(500)
                status = response.status if response else None
                body = ""
                try:
                    body = page.locator("body").inner_text(timeout=self.timeout_ms)
                except Exception:
                    pass
                blocked = status in {403, 429} or any(
                    token in (page.title() + "\n" + body[:10000]).lower()
                    for token in ("verify you are human", "checking your browser", "captcha", "access denied", "unusual traffic")
                )
                if blocked:
                    return {
                        "agent": "data_collection", "adapter": self.name, "source": "Soccerway",
                        "source_url": list_url, "captured_at": utc_now(), "records": [],
                        "records_collected": 0, "status": "blocked",
                        "errors": [], "warnings": ["Fixture-list collection stopped on access denial/challenge; no bypass attempted."],
                        "authority": self.authority,
                    }
                # Prefer the actual match-list content region so unrelated footer/sidebar
                # "Matches" and "Live Scores" links are not mistaken for this day's fixtures.
                list_scope = page
                list_scope_name = "full-page fallback"
                for scope_selector in ("main", "#mc", "[role='main']"):
                    try:
                        candidate_scope = page.locator(scope_selector).first
                        if candidate_scope.count() and candidate_scope.locator("a[href*='/match/'],a[href*='/game/']").count():
                            list_scope = candidate_scope
                            list_scope_name = scope_selector
                            break
                    except Exception:
                        continue
                if list_scope_name == "full-page fallback":
                    warnings.append("No clear main match-list container was identified; footer/sidebar filtering is applied as a fallback.")

                # Bounded scrolling allows pages that lazy-load more of the daily list to render.
                stable_counts = 0
                previous_count = -1
                for _ in range(20):
                    try:
                        current_count = list_scope.locator("a[href*='/match/'],a[href*='/game/']").count()
                        if current_count == previous_count:
                            stable_counts += 1
                        else:
                            stable_counts = 0
                        previous_count = current_count
                        if stable_counts >= 2 or current_count >= max_fixtures * 4:
                            break
                        page.evaluate("window.scrollBy(0, Math.max(500, window.innerHeight * 0.8))")
                        page.wait_for_timeout(350)
                    except Exception:
                        break
                fixtures = self._extract_fixture_rows(list_scope, list_url, max_fixtures=max_fixtures)
                if not fixtures:
                    warnings.append("No structured fixture links were extracted. Check date/list page and the current page DOM.")
                if status is not None and status >= 400:
                    errors.append(f"Fixture listing returned HTTP {status}.")
                page_snapshot = {
                    "page_type": "fixture_list",
                    "source_url": page.url,
                    "captured_at": utc_now(),
                    "http_status": status,
                    "title": page.title(),
                    "body_text": body[:TEXT_LIMIT],
                    "fixtures": fixtures,
                    "fixture_count": len(fixtures),
                }
            except Exception as exc:
                errors.append(f"Fixture-list collection failed: {type(exc).__name__}: {exc}")
                page_snapshot = {"page_type":"fixture_list","source_url":list_url,"captured_at":utc_now(),"fixtures":[]}
            finally:
                context.close()
                browser.close()

        captured_at = utc_now()
        digest = hashlib.sha256(f"{list_url}|{json.dumps(fixtures,sort_keys=True)}".encode()).hexdigest()
        record = {
            "record_id": digest,
            "source": "Soccerway",
            "source_url": list_url,
            "captured_at": captured_at,
            "facts": {
                "fixture_date": parse_qs(urlparse(list_url).query).get("date", [None])[0],
                "fixture_count": len(fixtures),
            },
            "fixtures": fixtures,
            "raw_payload": {"page": page_snapshot, "warnings": warnings},
        }
        return {
            "agent": "data_collection", "adapter": self.name, "source": "Soccerway",
            "source_url": list_url, "captured_at": captured_at, "records": [record],
            "fixtures": fixtures, "records_collected": 1,
            "fixture_count": len(fixtures),
            "status": "success" if fixtures else ("partial" if not errors else "failed"),
            "errors": errors, "warnings": warnings, "authority": self.authority,
        }

    @staticmethod
    def _extract_fixture_rows(page: Any, source_url: str, *, max_fixtures: int = FIXTURE_LINK_LIMIT) -> list[dict[str, Any]]:
        """Group links by canonical match URL so home/away labels are not lost or mixed."""
        grouped: dict[str, dict[str, Any]] = {}
        selectors = ("a[href*='/match/']", "a[href*='/game/']")
        for selector in selectors:
            links = page.locator(selector)
            for index in range(min(links.count(), max_fixtures * 8)):
                node = links.nth(index)
                try:
                    if page is None:
                        continue
                    # Footer and navigation recommendations are not the selected date's fixture list.
                    in_non_fixture_region = False
                    for excluded in ("xpath=ancestor::footer[1]", "xpath=ancestor::nav[1]", "xpath=ancestor::aside[1]"):
                        try:
                            if node.locator(excluded).count():
                                in_non_fixture_region = True
                                break
                        except Exception:
                            pass
                    if in_non_fixture_region:
                        continue
                    href = (node.get_attribute("href") or "").strip()
                    absolute = urljoin(source_url, href)
                    if not SoccerwayAdapter._is_match_url(absolute):
                        continue
                    canonical = SoccerwayAdapter.validate_url(absolute)
                    label = re.sub(r"\s+", " ", (node.inner_text(timeout=500) or "").strip())
                    if canonical not in grouped:
                        grouped[canonical] = {"url": canonical, "nodes": [], "labels": [], "container": None}
                    grouped[canonical]["nodes"].append(node)
                    if label and label not in grouped[canonical]["labels"]:
                        grouped[canonical]["labels"].append(label)
                except Exception:
                    continue

        fixtures: list[dict[str, Any]] = []
        for canonical, group in grouped.items():
            nodes = group["nodes"]
            labels = group["labels"]
            row_locator = None
            row_text = " | ".join(labels)
            # Find the smallest ancestor that contains links for just this fixture.
            for depth in range(1, 9):
                if not nodes:
                    break
                try:
                    candidate = nodes[0].locator(f"xpath=ancestor::*[{depth}]")
                    text_value = re.sub(r"\s+", " ", (candidate.inner_text(timeout=450) or "").strip())
                    if not text_value or len(text_value) > 1_200:
                        continue
                    descendant_links = candidate.locator("a[href*='/match/'],a[href*='/game/']")
                    descendant_ids: set[str] = set()
                    for j in range(min(descendant_links.count(), 80)):
                        try:
                            link_url = urljoin(source_url, descendant_links.nth(j).get_attribute("href") or "")
                            if SoccerwayAdapter._is_match_url(link_url):
                                descendant_ids.add(SoccerwayAdapter.validate_url(link_url))
                        except Exception:
                            continue
                    # Exactly one unique match URL in the block means we haven't crossed
                    # into the surrounding list or a sidebar containing other fixtures.
                    if descendant_ids == {canonical}:
                        has_fixture_marker = (
                            bool(re.search(r"\b\d{1,2}:\d{2}\b", text_value))
                            or bool(re.search(r"(?<!\d)\d{1,2}\s*[-–:]\s*\d{1,2}(?!\d)", text_value))
                            or len(labels) >= 2
                            or bool(SoccerwayAdapter._teams_from_title(text_value))
                        )
                        if has_fixture_marker:
                            row_locator = candidate
                            row_text = text_value
                            break
                except Exception:
                    continue

            if not labels and not row_text:
                continue
            home_team = away_team = None
            for label in labels:
                pair = SoccerwayAdapter._teams_from_title(label)
                if pair:
                    home_team, away_team = pair
                    break
            if not (home_team and away_team):
                # If Soccerway renders separate linked team labels for one match,
                # use the distinct labels associated with that same canonical URL.
                candidates = []
                for label in labels:
                    cleaned = re.sub(r"\s+", " ", label).strip(" -|")
                    if (cleaned and len(cleaned) <= 90
                            and not re.search(r"\b(?:live|full-time|finished|scheduled|half-time|show more|stats|lineups?|odds)\b", cleaned, re.I)
                            and not re.search(r"\b\d{1,2}:\d{2}\b", cleaned)):
                        if cleaned not in candidates:
                            candidates.append(cleaned)
                if len(candidates) >= 2:
                    home_team, away_team = candidates[0], candidates[1]

            if not (home_team and away_team) and row_locator is not None:
                # Source-specific team anchors in the selected row/card are another
                # explicit option; never scan team names from the whole page.
                for selector in ("a[href*='/team/']", "[class*='team-name' i]", "[data-testid*='team-name' i]"):
                    try:
                        team_nodes = row_locator.locator(selector)
                        names = []
                        for k in range(min(team_nodes.count(), 4)):
                            text_name = re.sub(r"\s+", " ", (team_nodes.nth(k).inner_text(timeout=350) or "").strip())
                            if text_name and text_name not in names:
                                names.append(text_name)
                        if len(names) >= 2:
                            home_team, away_team = names[0], names[1]
                            break
                    except Exception:
                        continue

            if not (home_team and away_team):
                # No reliable team pair: don't create a misleading fixture object.
                continue
            # Preserve each canonical fixture link only once, even if nested duplicate
            # anchors are rendered in more than one place inside the selected row.
            if any(item["source_url"] == canonical for item in fixtures):
                continue

            kickoff_match = re.search(r"\b(\d{1,2}:\d{2})\b", row_text)
            score_match = re.search(r"(?<!\d)(\d{1,2})\s*[-–:]\s*(\d{1,2})(?!\d)", row_text)
            status = next((
                value for value in ("Full-time", "Finished", "Live", "Half-time", "Postponed", "Scheduled")
                if re.search(r"\b" + re.escape(value) + r"\b", row_text, re.I)
            ), None)

            competition = None
            if row_locator is not None:
                try:
                    previous_heading = row_locator.locator("xpath=preceding::*[self::h1 or self::h2 or self::h3 or self::h4 or @role='heading'][1]")
                    heading_text = re.sub(r"\s+", " ", (previous_heading.first.inner_text(timeout=350) or "").strip())
                    if heading_text and re.search(r"\b(league|cup|championship|division|round|group|premier|bundesliga|serie a|laliga)\b", heading_text, re.I):
                        competition = heading_text[:200]
                except Exception:
                    pass
                if not competition:
                    try:
                        row_competition = row_locator.locator("[class*='competition' i],[data-testid*='competition' i]")
                        value = re.sub(r"\s+", " ", (row_competition.first.inner_text(timeout=350) or "").strip())
                        if value and len(value) <= 160:
                            competition = value
                    except Exception:
                        pass

            fixtures.append({
                "source": "Soccerway",
                "source_url": canonical,
                "page_identity": "/".join([part for part in urlparse(canonical).path.split("/") if part][-3:]),
                "competition": competition,
                "home_team": home_team,
                "away_team": away_team,
                "kickoff_display": kickoff_match.group(1) if kickoff_match else None,
                "score": {"home": int(score_match.group(1)), "away": int(score_match.group(2))} if score_match else None,
                "status": status,
                "visible_text": row_text[:1000],
            })
            if len(fixtures) >= max_fixtures:
                break
        return fixtures

    @staticmethod
    def _is_match_url(url: str) -> bool:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        path = [part for part in parsed.path.split("/") if part]
        return (parsed.scheme in {"http","https"}
                and (host == "soccerway.com" or host.endswith(".soccerway.com"))
                and len(path) >= 3 and path[0].lower() in {"match","game"})

    def collect(self, url: str) -> dict[str, Any]:
        """Collect selected fixture detail pages and the expanded history panels on H2H."""
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
                            history_expansion = self._expand_history_panels(page, item["page_type"])
                            captured = self._capture_page(page, response, item["page_type"], item["link_label"])
                            captured["history_expansion"] = history_expansion
                            if item["page_type"] == "h2h":
                                warnings.extend(history_expansion.get("warnings", []))
                            if captured["access_blocked"]:
                                blocked = True
                                warnings.append("A challenge/access-control page was detected; collection stopped.")
                                break
                            pages.append(captured)
                            if item["page_type"] == "stats":
                                period_pages, period_warnings = self._capture_stat_period_variants(
                                    page, candidate, base_url
                                )
                                pages.extend(period_pages)
                                warnings.extend(period_warnings)
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
        h2h_page = next((item for item in pages if item.get("page_type") == "h2h"), None)
        history_clicks = {"home_team_last_matches": 0, "away_team_last_matches": 0, "team_form": 0, "h2h_meetings": 0, "unclassified": 0}
        if h2h_page is not None:
            # Only report click evidence captured while collecting the visible H2H page.
            history_clicks = h2h_page.get("history_expansion", {}).get("clicks", history_clicks)
        raw_payload = {
            "adapter": self.name,
            "page_types_seen": [x["page_type"] for x in pages],
            "pages": pages,
            "statistics": aggregate["statistics"],
            "statistics_by_period": aggregate.get("statistics_by_period", {}),
            "history": aggregate.get("history", {}),
            "lineups": aggregate["lineups"],
            "events": aggregate["events"],
            "player_links": aggregate["player_links"],
            "missing_fields": aggregate["missing_fields"],
            "history_expansion": history_clicks,
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
            "captured_at": utc_now(),
            "records": [{
                "record_id": record_id,
                "source": "Soccerway",
                "source_url": base_url,
                "captured_at": utc_now(),
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

    def _capture_stat_period_variants(
        self, page: Any, stats_url: str, base_match_url: str
    ) -> tuple[list[dict[str, Any]], list[str]]:
        """Capture first-half and second-half statistics only when explicit controls exist."""
        captured: list[dict[str, Any]] = []
        warnings: list[str] = []
        periods = (
            ("first_half", {"first half", "1st half", "first half stats", "1st half stats"}),
            ("second_half", {"second half", "2nd half", "second half stats", "2nd half stats"}),
        )
        for period, labels in periods:
            found = False
            for selector in ("button", "[role='tab']", "a", "[role='button']"):
                nodes = page.locator(selector)
                for index in range(min(nodes.count(), 400)):
                    node = nodes.nth(index)
                    label = self._expand_control_text(node)
                    normalised = re.sub(r"[\s\-_]+", " ", label).strip().lower()
                    if normalised not in labels:
                        continue
                    try:
                        node.scroll_into_view_if_needed(timeout=800)
                        node.click(timeout=1200)
                        page.wait_for_timeout(350)
                        if not self._same_match(page.url, base_match_url):
                            warnings.append(f"Stats {period.replace('_', ' ')} control navigated outside the selected match; ignored.")
                            page.goto(stats_url, wait_until="domcontentloaded")
                            page.wait_for_timeout(350)
                            found = True
                            break
                        item = self._capture_page(page, None, f"stats_{period}", f"Stats period: {label}")
                        item["period"] = period
                        captured.append(item)
                        found = True
                        # Restore the known Stats URL before trying the next period.
                        page.goto(stats_url, wait_until="domcontentloaded")
                        page.wait_for_timeout(300)
                        break
                    except Exception as exc:
                        warnings.append(f"Stats {period.replace('_', ' ')} control failed: {type(exc).__name__}")
                if found:
                    break
            if not found:
                warnings.append(f"No explicit {period.replace('_', ' ')} selector found on the Stats page.")
        return captured, warnings

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
        history_sections = self._history_section_rows(page, page_type)
        return {
            "page_type": page_type,
            "link_label": link_label,
            "url": page.url,
            "http_status": status,
            "captured_at": utc_now(),
            "title": title[:500],
            "headings": headings[:30],
            "dom_fields": dom_fields,
            "history_sections": history_sections,
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
            cells = [str(cell).strip() for cell in (row.get("cells") or [])]
            if len(cells) < 3:
                continue
            label_index: int | None = None
            key: str | None = None
            for index, cell in enumerate(cells):
                normalised = re.sub(r"\s+", " ", cell).lower()
                candidate_key = STAT_ALIASES.get(normalised)
                if candidate_key:
                    label_index, key = index, candidate_key
                    break
            if label_index is None or key is None:
                continue
            # Soccerway-like tables may put the metric in the centre (home | label | away)
            # or at one edge (label | home | away). Parse only explicit adjacent side values.
            if label_index == 0:
                home, away = cells[1], cells[2]
            elif label_index == len(cells) - 1:
                home, away = cells[-3], cells[-2]
            else:
                home, away = cells[label_index - 1], cells[label_index + 1]
            if home and away:
                stats[key] = {
                    "home": home,
                    "away": away,
                    "source_label": cells[label_index],
                }
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
    def _history_section_rows(page: Any, page_type: str) -> dict[str, Any]:
        """Separate each side's recent matches from direct H2H meetings where boundaries are clear."""
        empty = lambda target: {"heading": None, "rows": [], "target_rows": target}
        sections: dict[str, Any] = {
            "home_team_last_matches": empty(TEAM_FORM_TARGET),
            "away_team_last_matches": empty(TEAM_FORM_TARGET),
            "team_form": empty(TEAM_FORM_TARGET),
            "h2h_meetings": empty(H2H_TARGET),
            "unassigned_visible_history_rows": [],
        }
        if page_type != "h2h":
            return sections

        home_team = away_team = ""
        try:
            pair = SoccerwayAdapter._teams_from_title(page.title() or "")
            if pair:
                home_team, away_team = pair[0].lower(), pair[1].lower()
        except Exception:
            pass

        heading_nodes = page.locator("h1,h2,h3,h4,[role='heading']")
        for i in range(min(heading_nodes.count(), 100)):
            heading = heading_nodes.nth(i)
            try:
                label = re.sub(r"\s+", " ", (heading.inner_text(timeout=350) or "").strip())
                initial_kind = SoccerwayAdapter._label_kind(label)
                if initial_kind not in {"team_form", "h2h_meetings"}:
                    continue

                chosen_key = initial_kind
                label_lower = label.lower()
                if initial_kind == "team_form":
                    has_home = bool(home_team and home_team in label_lower)
                    has_away = bool(away_team and away_team in label_lower)
                    if has_home and not has_away:
                        chosen_key = "home_team_last_matches"
                    elif has_away and not has_home:
                        chosen_key = "away_team_last_matches"

                if sections[chosen_key]["heading"] is None:
                    sections[chosen_key]["heading"] = label

                chosen_container = None
                for depth in range(1, 9):
                    try:
                        ancestor = heading.locator(f"xpath=ancestor::*[{depth}]")
                        ancestor_text = re.sub(r"\s+", " ", (ancestor.inner_text(timeout=350) or "")).strip().lower()
                        if not ancestor_text or len(ancestor_text) > 12_000:
                            continue
                        has_team_label = any(term in ancestor_text for term in (
                            "last matches", "previous matches", "recent matches", "home form", "away form", "recent form"
                        ))
                        has_h2h_label = any(term in ancestor_text for term in (
                            "last meetings", "previous meetings", "head-to-head", "head to head", "direct meetings", "previous encounters"
                        ))
                        if chosen_key in {"home_team_last_matches", "away_team_last_matches", "team_form"}:
                            if has_h2h_label:
                                continue
                            if not has_team_label and initial_kind != "team_form":
                                continue
                            has_home = bool(home_team and home_team in ancestor_text)
                            has_away = bool(away_team and away_team in ancestor_text)
                            if has_home and not has_away:
                                chosen_key = "home_team_last_matches"
                            elif has_away and not has_home:
                                chosen_key = "away_team_last_matches"
                        elif chosen_key == "h2h_meetings":
                            if has_team_label:
                                continue
                            if not has_h2h_label and initial_kind != "h2h_meetings":
                                continue
                        tables = ancestor.locator("table")
                        if tables.count():
                            chosen_container = ancestor
                            break
                    except Exception:
                        continue
                if chosen_container is None:
                    continue

                max_rows = H2H_TARGET if chosen_key == "h2h_meetings" else TEAM_FORM_TARGET
                local_rows: list[dict[str, Any]] = []
                tables = chosen_container.locator("table")
                for table_index in range(min(tables.count(), 5)):
                    table = tables.nth(table_index)
                    trs = table.locator("tr")
                    for row_index in range(min(trs.count(), max_rows + 3)):
                        try:
                            tr = trs.nth(row_index)
                            cells = [re.sub(r"\s+", " ", cell.strip()) for cell in tr.locator("th,td").all_inner_texts()]
                            cells = [cell for cell in cells if cell]
                            if len(cells) >= 3:
                                local_rows.append({
                                    "cells": cells[:12],
                                    "text": " | ".join(cells)[:600],
                                    "section": chosen_key,
                                    "source_heading": label,
                                })
                        except Exception:
                            continue

                existing = {row.get("text") for row in sections[chosen_key]["rows"]}
                for row in local_rows:
                    if row.get("text") not in existing and len(sections[chosen_key]["rows"]) < max_rows:
                        sections[chosen_key]["rows"].append(row)
                        existing.add(row.get("text"))
            except Exception:
                continue

        # When headings are absent/ambiguous, preserve visible rows without guessing their meaning.
        if not any(sections[key]["rows"] for key in (
            "home_team_last_matches", "away_team_last_matches", "team_form", "h2h_meetings"
        )):
            tables = page.locator("table")
            for table_index in range(min(tables.count(), 20)):
                trs = tables.nth(table_index).locator("tr")
                for row_index in range(min(trs.count(), TEAM_FORM_TARGET * 2 + H2H_TARGET + 10)):
                    try:
                        tr = trs.nth(row_index)
                        cells = [re.sub(r"\s+", " ", cell.strip()) for cell in tr.locator("th,td").all_inner_texts()]
                        cells = [cell for cell in cells if cell]
                        if len(cells) >= 3:
                            sections["unassigned_visible_history_rows"].append({
                                "cells": cells[:12],
                                "text": " | ".join(cells)[:600],
                                "section": "unassigned",
                            })
                    except Exception:
                        continue
        return sections

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
        stats_by_period: dict[str, dict[str, dict[str, str]]] = {
            "full_match": {},
            "first_half": {},
            "second_half": {},
        }
        lineups: list[dict[str, str]] = []
        events: list[dict[str, str]] = []
        players: list[dict[str, str]] = []
        history = {
            "home_team_last_matches": {"heading": None, "rows": [], "target_rows": TEAM_FORM_TARGET},
            "away_team_last_matches": {"heading": None, "rows": [], "target_rows": TEAM_FORM_TARGET},
            "team_form": {"heading": None, "rows": [], "target_rows": TEAM_FORM_TARGET},
            "h2h_meetings": {"heading": None, "rows": [], "target_rows": H2H_TARGET},
            "unassigned_visible_history_rows": [],
        }
        for item in pages:
            page_type = item.get("page_type")
            page_stats = item.get("statistics") or {}
            if page_type == "stats_first_half":
                stats_by_period["first_half"].update(page_stats)
            elif page_type == "stats_second_half":
                stats_by_period["second_half"].update(page_stats)
            elif page_type == "stats":
                stats.update(page_stats)
                stats_by_period["full_match"].update(page_stats)
            for key in ("home_team_last_matches", "away_team_last_matches", "team_form", "h2h_meetings"):
                section = (item.get("history_sections") or {}).get(key) or {}
                if section.get("heading") and not history[key]["heading"]:
                    history[key]["heading"] = section["heading"]
                existing = {row.get("text") for row in history[key]["rows"]}
                history[key]["rows"].extend(row for row in section.get("rows", []) if row.get("text") not in existing)
            history["unassigned_visible_history_rows"].extend(
                (item.get("history_sections") or {}).get("unassigned_visible_history_rows", [])
            )
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
            "statistics_by_period": stats_by_period,
            "lineups": lineups,
            "events": event_items[:100],
            "player_links": deduped_players[:120],
            "history": history,
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
