from __future__ import annotations
from typing import Any

ALLOWED_MARKETS = {"RESULT_1X2","DOUBLE_CHANCE","DRAW_NO_BET","OVER_UNDER_MATCH_GOALS","OVER_UNDER_TEAM_GOALS"}

class QQRResearchAgent:
    """Synthesises traceable evidence for a requested market; never displays probabilities."""
    name = "qqr_research"

    def research(self, fixture: dict[str, Any], market: str, evidence: list[dict[str, Any]],
                 quality: dict[str, Any], advice_requested: bool = False) -> dict[str, Any]:
        market = market.strip().upper()
        if market not in ALLOWED_MARKETS:
            raise ValueError(f"Unsupported market {market}. Allowed markets: {', '.join(sorted(ALLOWED_MARKETS))}")
        quality_by_id = {x.get("record_id"):x for x in quality.get("assessments",[])}
        supporting, opposing, context, excluded = [], [], [], []
        for item in evidence:
            assessment = quality_by_id.get(item.get("record_id"), {})
            if assessment.get("quality_label") != "usable":
                excluded.append({"record_id":item.get("record_id"),"source":item.get("source"),
                                 "reason":assessment.get("quality_label","not_assessed")})
                continue
            facts, payload = item.get("facts") or {}, item.get("raw_payload") or {}
            source = {"source":item.get("source"),"source_url":item.get("source_url"),
                      "captured_at":item.get("captured_at"),"record_id":item.get("record_id")}
            for key in ("home_team","away_team","competition","kickoff","status","home_score","away_score","venue"):
                if facts.get(key) is not None:
                    context.append({**source,"field":key,"value":facts[key]})
            for key in ("supporting_signals","against_signals","notes","form_summary","h2h_summary","home_away_summary","goal_summary"):
                value = payload.get(key)
                if value:
                    target = opposing if key == "against_signals" else supporting if key == "supporting_signals" else context
                    target.append({**source,"field":key,"value":value})
        gaps = []
        if not any(quality_by_id.get(x.get("record_id"),{}).get("quality_label") == "usable" for x in evidence):
            gaps.append("No records passed the evidence-quality gate.")
        if not supporting:
            gaps.append("No explicit market-specific supporting signals were supplied by quality-approved evidence.")
        if not opposing:
            gaps.append("No explicit counter-evidence was supplied; that absence is not proof of safety.")
        return {"agent":self.name,"fixture":fixture,"market":market,"advice_requested":bool(advice_requested),
            "supporting_evidence":supporting,"counter_evidence":opposing,"context_and_sources":context,
            "excluded_evidence":excluded,"evidence_gaps":gaps,
            "recommendation":{"status":"PASS_INSUFFICIENT_EVIDENCE" if gaps else "RESEARCH_ONLY","lean":None,
              "reason":"No lean is invented. A lean requires explicit market-specific evidence and counter-evidence review."},
            "probabilities_displayed":False,"authority":"market_evidence_synthesis_not_final_betting_authority"}
