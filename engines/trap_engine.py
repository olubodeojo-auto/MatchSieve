from engines.base_engine import BaseEngine


class TrapEngine(BaseEngine):

    def __init__(self):
        super().__init__("Trap Engine")

    def calculate(self, context):

        features = context.features

        score = 0
        reasons = []

        # ----------------------------------
        # Market Volatility
        # ----------------------------------

        if features.market_stability == "VOLATILE":
            score += 30
            reasons.append("Volatile betting market")

        # ----------------------------------
        # Goal Probability vs Under
        # ----------------------------------

        goal = context.results.get("Goal Probability Engine", {})
        under = context.results.get("Under Engine", {})

        if goal.get("score", 0) >= 75 and under.get("score", 0) >= 75:
            score += 25
            reasons.append("Conflicting goal signals")

        # ----------------------------------
        # Explosion Risk
        # ----------------------------------

        explosion = context.results.get("Explosion Engine", {})

        if explosion.get("score", 0) >= 80:
            score += 15
            reasons.append("Explosion risk detected")

        # ----------------------------------
        # NBS
        # ----------------------------------

        nbs = context.results.get("NBS Engine", {})

        if nbs.get("risk") == "HIGH":
            score += 20
            reasons.append("High NBS risk")

        # ----------------------------------
        # Clamp
        # ----------------------------------

        score = max(0, min(score, 100))

        if score >= 75:
            level = "EXTREME"

        elif score >= 60:
            level = "HIGH"

        elif score >= 40:
            level = "MEDIUM"

        else:
            level = "LOW"

        features.trap_risk = score

        return {

            "score": score,

            "level": level,

            "reasons": reasons

        }