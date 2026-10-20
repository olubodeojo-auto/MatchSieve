from engines.confidence_engine import ConfidenceEngine
from engines.nbs_engine import NBSEngine


class EnginePipeline:

    def __init__(self):

        self.engines = [

            ConfidenceEngine(),

            NBSEngine()

        ]

    def analyze(self, context):

        results = {}

        for engine in self.engines:

            results[engine.name] = engine.calculate(context)

        return results