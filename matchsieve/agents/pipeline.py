from __future__ import annotations

from typing import Any

from .data_collection import DataCollectionAgent
from .data_quality import DataQualityAgent
from .local_llm import LocalOllamaClient
from .qqr_research import QQRResearchAgent
from .report_writing import ReportWritingAgent


class MatchSieveAgentPipeline:
    """Run deterministic quality/research stages, with optional local LLM interpretation."""

    def __init__(self, llm_client: LocalOllamaClient | None = None):
        self.collector = DataCollectionAgent()
        self.quality_agent = DataQualityAgent()
        self.research_agent = QQRResearchAgent()
        self.writer = ReportWritingAgent()
        self.llm_client = llm_client

    def run(
        self,
        collection: dict[str, Any],
        fixture: dict[str, Any],
        market: str,
        advice_requested: bool = False,
    ) -> dict[str, Any]:
        quality = self.quality_agent.assess(collection)
        research = self.research_agent.research(
            fixture, market, collection.get("records", []), quality, advice_requested
        )
        report = self.writer.write(research)
        result: dict[str, Any] = {
            "collection": collection,
            "quality": quality,
            "research": research,
            "report": report,
            "pipeline_status": (
                "ready_for_human_review"
                if report["recommendation_status"] == "RESEARCH_ONLY"
                else "insufficient_evidence"
            ),
            "llm_analysis": None,
        }

        if self.llm_client is not None:
            usable_ids = {
                item.get("record_id")
                for item in quality.get("assessments", [])
                if item.get("quality_label") == "usable"
            }
            usable_evidence = [
                record for record in collection.get("records", [])
                if record.get("record_id") in usable_ids
            ]
            result["llm_analysis"] = self.llm_client.analyse(research, usable_evidence)
            # The LLM never upgrades a deterministic failure or publishes a report itself.
            if result["llm_analysis"].get("status") != "llm_analysis_complete":
                result["pipeline_status"] = "review_required"

        return result
