import unittest

from engines.master_engine import MasterEngine
from models.analysis_context import AnalysisContext
from models.football_features import FootballFeatures


class DependencyStub:
    def __init__(self, name, result, required=()):
        self.name = name
        self.result = result
        self.required = required

    def calculate(self, context):
        for dependency in self.required:
            if dependency not in context.results:
                raise AssertionError(f"{self.name} ran before {dependency}")
        return self.result


class MasterEngineOrderTests(unittest.TestCase):
    def test_dependent_engines_run_after_their_inputs(self):
        engine = MasterEngine()
        engine.nbs = DependencyStub("NBS Engine", {"score": 90, "risk": "LOW"})
        engine.trap = DependencyStub(
            "Trap Engine", {"score": 0, "level": "LOW"},
            ("NBS Engine", "Explosion Engine"),
        )
        engine.value = DependencyStub(
            "Value Engine", {"score": 50, "value": "FAIR"},
            ("Trap Engine",),
        )
        engine.evidence = DependencyStub(
            "Evidence Engine", {"confidence": 50},
            ("NBS Engine",),
        )

        context = AnalysisContext(features=FootballFeatures())
        results = engine.analyze(context)

        self.assertIn("NBS Engine", results)
        self.assertIn("Trap Engine", results)
        self.assertIn("Value Engine", results)
        self.assertIn("Evidence Engine", results)
        self.assertIn("Final Decision Engine", results)


if __name__ == "__main__":
    unittest.main()
