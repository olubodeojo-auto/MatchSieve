from __future__ import annotations
from typing import Any
from .data_collection import DataCollectionAgent
from .data_quality import DataQualityAgent
from .qqr_research import QQRResearchAgent
from .report_writing import ReportWritingAgent

class MatchSieveAgentPipeline:
    """Explicit staged pipeline; quality filtering cannot be skipped."""
    def __init__(self):
        self.collector = DataCollectionAgent()
        self.quality_agent = DataQualityAgent()
        self.research_agent = QQRResearchAgent()
        self.writer = ReportWritingAgent()

    def run(self, collection: dict[str, Any], fixture: dict[str, Any], market: str,
            advice_requested: bool = False) -> dict[str, Any]:
        quality = self.quality_agent.assess(collection)
        research = self.research_agent.research(fixture, market, collection.get("records",[]), quality, advice_requested)
        report = self.writer.write(research)
        return {"collection":collection,"quality":quality,"research":research,"report":report,
                "pipeline_status":"ready_for_human_review" if report["recommendation_status"] == "RESEARCH_ONLY" else "insufficient_evidence"}
