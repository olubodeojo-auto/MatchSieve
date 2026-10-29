from __future__ import annotations
from typing import Any

class ReportWritingAgent:
    """Presents a structured QQR brief; it cannot add facts or change recommendation status."""
    name = "report_writing"

    def write(self, research: dict[str, Any]) -> dict[str, Any]:
        fixture = research.get("fixture") or {}
        home, away = fixture.get("home_team","Home team not verified"), fixture.get("away_team","Away team not verified")
        market = str(research.get("market") or "market not specified").replace("_"," ").title()
        supporting, opposing, context = (research.get("supporting_evidence") or [],
            research.get("counter_evidence") or [], research.get("context_and_sources") or [])
        gaps, rec = research.get("evidence_gaps") or [], research.get("recommendation") or {}
        lines = [f"# MatchSieve Research Report: {home} vs {away}","",f"**Market question:** {market}",
                 "**Evidence status:** "+str(rec.get("status","REVIEW_REQUIRED")).replace("_"," ").title(),
                 "","## What supports the market"]
        lines += self._items(supporting,"No explicit supporting signal was verified.")
        lines += ["","## What challenges it"] + self._items(opposing,"No explicit counter-signal was supplied. That is a data gap, not confirmation.")
        lines += ["","## Match context and source notes"] + self._items(context,"No quality-approved context records were available.")
        lines += ["","## Missing evidence and limitations"] + ([f"- {x}" for x in gaps] if gaps else ["- No gaps were recorded; this does not guarantee completeness."])
        lines += ["","## MatchSieve's view",str(rec.get("reason") or "No final recommendation was supplied."),
                  "","This report organises evidence; it does not guarantee an outcome or profit. No probability figures are displayed."]
        sources = {x.get("source_url") for x in supporting+opposing+context if x.get("source_url")}
        return {"agent":self.name,"title":f"{home} vs {away} — {market}","markdown":"\n".join(lines),
                "source_count":len(sources),"recommendation_status":rec.get("status","REVIEW_REQUIRED"),"authority":"presentation_only"}

    @staticmethod
    def _items(items: list[dict[str, Any]], empty: str) -> list[str]:
        if not items: return [f"- {empty}"]
        lines = []
        for item in items:
            label = str(item.get("field","observation")).replace("_"," ").title()
            line = f"- **{label}:** {item.get('value')} _(source: {item.get('source') or 'not labelled'}"
            if item.get("captured_at"): line += f", captured: {item['captured_at']}"
            line += ")_"
            if item.get("source_url"): line += f" — {item['source_url']}"
            lines.append(line)
        return lines
