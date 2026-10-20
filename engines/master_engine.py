from engines.form_engine import FormEngine
from engines.goal_probability_engine import GoalProbabilityEngine
from engines.under_engine import UnderEngine
from engines.btts_engine import BTTSEngine
from engines.attack_strength_engine import AttackStrengthEngine
from engines.defence_strength_engine import DefenceStrengthEngine
from engines.league_profile_engine import LeagueProfileEngine
from engines.momentum_engine import MomentumEngine
from engines.explosion_engine import ExplosionEngine
from engines.trap_engine import TrapEngine
from engines.value_engine import ValueEngine
from engines.lazarus_engine import LazarusEngine
from engines.evidence_engine import EvidenceEngine
from engines.confidence_engine import ConfidenceEngine
from engines.nbs_engine import NBSEngine
from engines.recommendation_engine import RecommendationEngine
from engines.final_decision_engine import FinalDecisionEngine


class MasterEngine:

    def __init__(self):
        self.form = FormEngine()
        self.goal = GoalProbabilityEngine()
        self.under = UnderEngine()
        self.btts = BTTSEngine()

        self.attack = AttackStrengthEngine()
        self.defence = DefenceStrengthEngine()
        self.league = LeagueProfileEngine()
        self.momentum = MomentumEngine()

        self.explosion = ExplosionEngine()
        self.trap = TrapEngine()
        self.value = ValueEngine()
        self.lazarus = LazarusEngine()

        self.evidence = EvidenceEngine()
        self.confidence = ConfidenceEngine()
        self.nbs = NBSEngine()
        self.recommendation = RecommendationEngine()
        self.final = FinalDecisionEngine()

    def analyze(self, context):
        # Run foundational profiles first.
        self._run(context, "Form Engine", self.form)
        self._run(context, "League Profile Engine", self.league)
        self._run(context, "Attack Strength Engine", self.attack)
        self._run(context, "Defence Strength Engine", self.defence)
        self._run(context, "Momentum Engine", self.momentum)

        # These engines use the foundational feature values above.
        goal = self._run(context, "Goal Probability Engine", self.goal)
        context.features.goal_probability = goal.get("score", 0)
        self._run(context, "Under Engine", self.under)
        self._run(context, "BTTS Engine", self.btts)
        self._run(context, "Explosion Engine", self.explosion)
        self._run(context, "Lazarus Engine", self.lazarus)

        # Resolve data risk before engines that depend on it.
        self._run(context, "NBS Engine", self.nbs)
        self._run(context, "Trap Engine", self.trap)
        self._run(context, "Value Engine", self.value)
        self._run(context, "Evidence Engine", self.evidence)

        confidence = self._run(context, "Confidence Engine", self.confidence)
        context.features.confidence = confidence.get("score", 0)

        self._run(context, "Recommendation Engine", self.recommendation)
        final = self._run(context, "Final Decision Engine", self.final)
        context.features.recommendation = final.get("recommendation", "WAIT")

        return context.results

    @staticmethod
    def _run(context, name, engine):
        result = engine.calculate(context)
        context.results[name] = result
        return result
