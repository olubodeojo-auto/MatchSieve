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

        # -----------------------------
        # Core Analysis
        # -----------------------------

        self.form = FormEngine()
        self.goal = GoalProbabilityEngine()
        self.under = UnderEngine()
        self.btts = BTTSEngine()

        # -----------------------------
        # Football Intelligence
        # -----------------------------

        self.attack = AttackStrengthEngine()
        self.defence = DefenceStrengthEngine()
        self.league = LeagueProfileEngine()
        self.momentum = MomentumEngine()

        # -----------------------------
        # Advanced Intelligence
        # -----------------------------

        self.explosion = ExplosionEngine()
        self.trap = TrapEngine()
        self.value = ValueEngine()
        self.lazarus = LazarusEngine()

        # -----------------------------
        # Decision Layer
        # -----------------------------

        self.evidence = EvidenceEngine()
        self.confidence = ConfidenceEngine()
        self.nbs = NBSEngine()
        self.recommendation = RecommendationEngine()
        self.final = FinalDecisionEngine()

    def analyze(self, context):

        # ----------------------------------
        # Form Engine
        # ----------------------------------

        form = self.form.calculate(context)

        context.results["Form Engine"] = form

        # ----------------------------------
        # Goal Probability Engine
        # ----------------------------------

        goal = self.goal.calculate(context)

        context.results["Goal Probability Engine"] = goal

        context.features.goal_probability = goal.get("score", 0)

        # ----------------------------------
        # Under Engine
        # ----------------------------------

        under = self.under.calculate(context)

        context.results["Under Engine"] = under

        # ----------------------------------
        # BTTS Engine
        # ----------------------------------

        btts = self.btts.calculate(context)

        context.results["BTTS Engine"] = btts

        # ----------------------------------
        # Attack Strength Engine
        # ----------------------------------

        attack = self.attack.calculate(context)

        context.results["Attack Strength Engine"] = attack

        # ----------------------------------
        # Defence Strength Engine
        # ----------------------------------

        defence = self.defence.calculate(context)

        context.results["Defence Strength Engine"] = defence

        # ----------------------------------
        # League Profile Engine
        # ----------------------------------

        league = self.league.calculate(context)

        context.results["League Profile Engine"] = league

        # ----------------------------------
        # Momentum Engine
        # ----------------------------------

        momentum = self.momentum.calculate(context)

        context.results["Momentum Engine"] = momentum

        # ----------------------------------
        # Explosion Engine
        # ----------------------------------

        explosion = self.explosion.calculate(context)

        context.results["Explosion Engine"] = explosion

        # ----------------------------------
        # Trap Engine
        # ----------------------------------

        trap = self.trap.calculate(context)

        context.results["Trap Engine"] = trap

        # ----------------------------------
        # Value Engine
        # ----------------------------------

        value = self.value.calculate(context)

        context.results["Value Engine"] = value

        # ----------------------------------
        # Lazarus Engine
        # ----------------------------------

        lazarus = self.lazarus.calculate(context)

        context.results["Lazarus Engine"] = lazarus

        # ----------------------------------
        # Evidence Engine
        # ----------------------------------

        evidence = self.evidence.calculate(context)

        context.results["Evidence Engine"] = evidence

        # ----------------------------------
        # Confidence Engine
        # ----------------------------------

        confidence = self.confidence.calculate(context)

        context.results["Confidence Engine"] = confidence

        context.features.confidence = confidence.get("score", 0)

        # ----------------------------------
        # NBS Engine
        # ----------------------------------

        nbs = self.nbs.calculate(context)

        context.results["NBS Engine"] = nbs

        # ----------------------------------
        # Recommendation Engine
        # ----------------------------------

        recommendation = self.recommendation.calculate(context)

        context.results["Recommendation Engine"] = recommendation

        # ----------------------------------
        # Final Decision Engine
        # ----------------------------------

        final = self.final.calculate(context)

        context.results["Final Decision Engine"] = final

        context.features.recommendation = final.get(
            "recommendation",
            "WAIT"
        )

        return context.results