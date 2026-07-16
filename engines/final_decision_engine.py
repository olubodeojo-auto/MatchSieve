from engines.base_engine import BaseEngine


class FinalDecisionEngine(BaseEngine):

    def __init__(self):
        super().__init__("Final Decision Engine")

    def calculate(self, context):

        results = context.results

        score = 0
        reasons = []

        # ----------------------------------
        # Goal Probability
        # ----------------------------------

        goal = results.get("Goal Probability Engine", {})

        if goal.get("score", 0) >= 75:

            score += 20

            reasons.append("High goal probability")

        # ----------------------------------
        # Under Engine
        # ----------------------------------

        under = results.get("Under Engine", {})

        if under.get("score", 0) >= 75:

            score += 15

            reasons.append("Strong under profile")

        # ----------------------------------
        # BTTS
        # ----------------------------------

        btts = results.get("BTTS Engine", {})

        if btts.get("score", 0) >= 70:

            score += 10

            reasons.append("Strong BTTS profile")

        # ----------------------------------
        # Explosion
        # ----------------------------------

        explosion = results.get("Explosion Engine", {})

        if explosion.get("score", 0) >= 75:

            score += 15

            reasons.append("Explosion risk")

        # ----------------------------------
        # Lazarus
        # ----------------------------------

        lazarus = results.get("Lazarus Engine", {})

        if lazarus.get("score", 0) >= 75:

            score += 10

            reasons.append("Late goal opportunity")

        # ----------------------------------
        # Trap
        # ----------------------------------

        trap = results.get("Trap Engine", {})

        if trap.get("score", 0) >= 70:

            score -= 25

            reasons.append("Trap detected")

        # ----------------------------------
        # NBS
        # ----------------------------------

        nbs = results.get("NBS Engine", {})

        if nbs.get("risk") == "LOW":

            score += 15

            reasons.append("Low NBS risk")

        elif nbs.get("risk") == "HIGH":

            score -= 20

            reasons.append("High NBS risk")

        # ----------------------------------
        # Confidence
        # ----------------------------------

        confidence = results.get("Confidence Engine", 50)

        score += confidence // 10

        # ----------------------------------
        # Clamp
        # ----------------------------------

        score = max(0, min(score, 100))

        if score >= 85:

            recommendation = "STRONG BET"

        elif score >= 70:

            recommendation = "BET"

        elif score >= 55:

            recommendation = "UNDER LEAN STRONG"

        elif score >= 40:

            recommendation = "UNDER LEAN"

        else:

            recommendation = "WAIT"

        return {

            "score": score,

            "recommendation": recommendation,

            "reasons": reasons

        }