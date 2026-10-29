from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LocalLLMError(RuntimeError):
    """Raised when the local model cannot return a usable analysis."""


SYSTEM_PROMPT = """You are MatchSieve's evidence analyst, not a tipster.
Analyse only the supplied structured football evidence. Do not use outside knowledge,
invent injuries, infer missing statistics, or claim that a market is safe.
Separate supporting evidence from counter-evidence. Explain competition and venue
differences. Recent form is not the same as home/away form. Separate league H2H
from cup/friendly/youth matches when the evidence labels them. If the evidence does
not label a competition or venue, say so. Never fabricate a probability or expected
score. Never treat bookmaker odds as proof that an outcome will occur.
Return ONLY a JSON object with this schema:
{
  "summary": "short balanced assessment",
  "supporting_points": [{"claim":"...", "evidence_record_ids":["id"]}],
  "counter_points": [{"claim":"...", "evidence_record_ids":["id"]}],
  "data_quality_concerns": ["..."],
  "market_assessment": "what the evidence does and does not establish",
  "limitations": ["..."],
  "decision": "RESEARCH_ONLY or INSUFFICIENT_EVIDENCE"
}
Every factual supporting_points/counter_points claim must cite one or more record IDs
that exist in the supplied usable evidence. Do not put uncited factual claims there.
If no evidence supports a claim, omit it. Use INSUFFICIENT_EVIDENCE when evidence
is materially incomplete or conflicting. This is research assistance, not a bet command."""


class LocalOllamaClient:
    """Small stdlib-only client for Ollama's local HTTP API; no cloud API key required."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str | None = None,
        timeout_seconds: int = 120,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model or os.environ.get("MATCHSIEVE_OLLAMA_MODEL", "qwen2.5:7b")
        self.timeout_seconds = timeout_seconds

    def analyse(self, research: dict[str, Any], usable_evidence: list[dict[str, Any]]) -> dict[str, Any]:
        evidence_ids = {
            str(record.get("record_id"))
            for record in usable_evidence
            if record.get("record_id") is not None
        }
        if not evidence_ids:
            return {
                "status": "insufficient_evidence",
                "error": "No quality-approved evidence records were available to the local LLM.",
                "analysis": None,
                "unsupported_claims": [],
            }

        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {"research_brief": research, "usable_evidence": usable_evidence},
                        ensure_ascii=False,
                        default=str,
                    ),
                },
            ],
        }
        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            raise LocalLLMError(
                f"Could not obtain a response from local Ollama at {self.base_url}. "
                "Check that Ollama is running and the selected model is installed."
            ) from exc

        try:
            raw_content = response_data["message"]["content"]
            analysis = json.loads(raw_content)
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise LocalLLMError("Ollama returned malformed JSON; refusing to publish the analysis.") from exc

        if not isinstance(analysis, dict):
            raise LocalLLMError("Ollama response must be a JSON object.")

        unsupported_claims: list[dict[str, Any]] = []
        for section in ("supporting_points", "counter_points"):
            points = analysis.get(section, [])
            if not isinstance(points, list):
                raise LocalLLMError(f"Ollama field {section!r} must be a list.")
            for point in points:
                if not isinstance(point, dict) or not isinstance(point.get("claim"), str):
                    raise LocalLLMError(f"Ollama returned an invalid item in {section!r}.")
                cited = point.get("evidence_record_ids", [])
                if not isinstance(cited, list):
                    cited = []
                invalid_ids = [str(item) for item in cited if str(item) not in evidence_ids]
                if not cited or invalid_ids:
                    unsupported_claims.append({
                        "section": section,
                        "claim": point["claim"],
                        "invalid_record_ids": invalid_ids,
                        "reason": "missing or unknown evidence record citation",
                    })

        allowed_decisions = {"RESEARCH_ONLY", "INSUFFICIENT_EVIDENCE"}
        if analysis.get("decision") not in allowed_decisions:
            analysis["decision"] = "INSUFFICIENT_EVIDENCE"
            analysis.setdefault("data_quality_concerns", []).append(
                "The model returned an unsupported decision label; it was downgraded."
            )

        # The LLM can assist interpretation but cannot override the deterministic quality gate.
        return {
            "status": "review_required" if unsupported_claims else "llm_analysis_complete",
            "model": self.model,
            "analysis": analysis,
            "unsupported_claims": unsupported_claims,
            "publication_allowed": False,
            "authority": "local_llm_assistance_requires_human_review",
        }
