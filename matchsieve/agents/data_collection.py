from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from typing import Any, Callable, Iterable
from urllib.parse import urlparse

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class DataCollectionAgent:
    """Capture source records and raw snapshots only; never recommend a market."""
    name = "data_collection"

    def collect_records(self, source_name: str, source_url: str, fetcher: Callable[[], Iterable[dict[str, Any]]]) -> dict[str, Any]:
        parsed = urlparse(source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("source_url must be an absolute HTTP(S) URL")
        captured = utc_now()
        records, errors = [], []
        try:
            for index, row in enumerate(fetcher()):
                if not isinstance(row, dict):
                    errors.append(f"Record {index} was not an object and was skipped.")
                    continue
                raw = dict(row)
                raw_text = json.dumps(raw, sort_keys=True, ensure_ascii=False, default=str)
                record_id = hashlib.sha256(f"{source_name}|{source_url}|{raw_text}".encode()).hexdigest()
                records.append({"record_id":record_id,"source":source_name,"source_url":source_url,
                                "captured_at":captured,"raw_payload":raw,"facts":self.extract_facts(raw)})
        except Exception as exc:
            errors.append(f"Collection failed: {type(exc).__name__}: {exc}")
        return {"agent":self.name,"source":source_name,"source_url":source_url,"captured_at":captured,
                "records":records,"records_collected":len(records),"errors":errors,
                "status":"success" if records and not errors else ("partial" if records else "failed"),
                "authority":"source_capture_only"}

    @staticmethod
    def extract_facts(payload: dict[str, Any]) -> dict[str, Any]:
        aliases = {
            "home_team":("home_team","home","home_name"), "away_team":("away_team","away","away_name"),
            "competition":("competition","league","tournament"), "kickoff":("kickoff_utc","kickoff","date","starting_at"),
            "status":("status","state","match_status"), "home_score":("home_score","home_goals","score_home"),
            "away_score":("away_score","away_goals","score_away"), "venue":("venue","stadium"),
            "source_ref":("source_ref","url","match_url","id")}
        facts = {}
        for target, keys in aliases.items():
            for key in keys:
                value = payload.get(key)
                if isinstance(value, dict):
                    value = value.get("name") or value.get("short_name") or value.get("id")
                if value is not None and value != "":
                    facts[target] = value
                    break
        return facts

    def collect_soccerway_page(self, url: str, timeout_ms: int = 30000) -> dict[str, Any]:
        """Capture visible match-page text and likely same-host detail tabs with Playwright.
        Does not bypass access controls, logins, CAPTCHAs or rate limits. Raw text is not verified data.
        """
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("url must be an absolute HTTP(S) URL")
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError("Playwright is optional; install playwright and its Chromium browser locally.") from exc
        pages, errors = [], []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(timeout_ms)
            try:
                response = page.goto(url, wait_until="domcontentloaded")
                pages.append({"url":page.url,"http_status":response.status if response else None,
                              "captured_at":utc_now(),"title":page.title(),
                              "text":page.locator("body").inner_text()[:150000]})
                host = urlparse(url).netloc
                links = page.locator("a[href]")
                seen = {page.url}
                for i in range(min(links.count(), 250)):
                    link = links.nth(i)
                    try:
                        href = link.get_attribute("href") or ""
                        label = (link.inner_text(timeout=1200) or "").strip()
                        absolute = page.evaluate("(href) => new URL(href, location.href).href", href)
                        purl = urlparse(absolute)
                        token = (label + " " + purl.path).lower()
                        relevant = any(x in token for x in ("lineup","line-up","statistics","head-to-head","h2h","commentary","events","match"))
                        if purl.netloc != host or absolute in seen or not relevant:
                            continue
                        seen.add(absolute)
                        r = page.goto(absolute, wait_until="domcontentloaded")
                        pages.append({"url":page.url,"http_status":r.status if r else None,"captured_at":utc_now(),
                                      "title":page.title(),"link_label":label,"text":page.locator("body").inner_text()[:100000]})
                        if len(pages) >= 12:
                            break
                    except Exception as exc:
                        errors.append(f"Tab capture skipped: {type(exc).__name__}: {exc}")
            finally:
                browser.close()
        return {"agent":self.name,"source":"soccerway_playwright","source_url":url,"captured_at":utc_now(),
                "pages":pages,"records_collected":len(pages),"errors":errors,
                "status":"success" if pages else "failed","authority":"raw_page_capture_only"}
