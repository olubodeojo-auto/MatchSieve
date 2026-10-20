from services.match_builder import MatchBuilder
from services.data_fusion import DataFusion
from services.extractor_pipeline import ExtractorPipeline

from models.analysis_context import AnalysisContext

from engines.master_engine import MasterEngine


class PipelineRunner:

    def __init__(self):

        self.builder = MatchBuilder()

        self.fusion = DataFusion()

        self.extractors = ExtractorPipeline()

        self.master = MasterEngine()

    # --------------------------------------------------
    # Analyze Today's Fixtures
    # --------------------------------------------------

    def analyze_today(self):

        matches = self.builder.build_today()

        results = []

        for match in matches:

            context = self.analyze_match(match)

            results.append(context)

        return results

    # --------------------------------------------------
    # Analyze One Match
    # --------------------------------------------------

    def analyze_match(self, match):

        # --------------------------------------
        # Data Fusion
        # --------------------------------------

        match = self.fusion.merge(match)

        # --------------------------------------
        # Feature Pipeline
        # --------------------------------------

        features = self.extractors.process(match)

        # --------------------------------------
        # Build Analysis Context
        # --------------------------------------

        context = AnalysisContext()

        context.match = match

        context.features = features

        # --------------------------------------
        # AI Engine Pipeline
        # --------------------------------------

        context.results = self.master.analyze(context)

        return context