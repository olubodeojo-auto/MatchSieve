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

        goal = results.get(
            "Goal Probability Engine",
            {}
        )

        goal_score = goal.get("score", 0)

        if goal_score >= 75:

            score += 20

            reasons.append("High goal probability")

        # ----------------------------------
        # Under Engine
        # ----------------------------------

        under = results.get(
            "Under Engine",
            {}
        )

        under_score = under.get("score", 0)

        if under_score >= 75:

            score += 15

            reasons.append("Strong Under profile")

        # ----------------------------------
        # BTTS Engine
        # ----------------------------------

        btts = results.get(
            "BTTS Engine",
            {}
        )

        btts_score = btts.get("score", 0)

        if btts_score >= 70:

            score += 10

            reasons.append("Strong BTTS profile")

        # ----------------------------------
        # Explosion Engine
        # ----------------------------------

        explosion = results.get(
            "Explosion Engine",
            {}
        )

        explosion_score = explosion.get("score", 0)

        if explosion_score >= 75:

            score += 15

            reasons.append("Explosion potential")

        # ----------------------------------
        # Lazarus Engine
        # ----------------------------------

        lazarus = results.get(
            "Lazarus Engine",
            {}
        )

        lazarus_score = lazarus.get("score", 0)

        if lazarus_score >= 75:

            score += 10

            reasons.append("Late goal opportunity")

        # ----------------------------------
        # Trap Engine
        # ----------------------------------

        trap = results.get(
            "Trap Engine",
            {}
        )

        trap_score = trap.get("score", 0)

        if trap_score >= 70:

            score -= 25

            reasons.append("Trap detected")

        # ----------------------------------
        # NBS Engine
        # ----------------------------------

        nbs = results.get(
            "NBS Engine",
            {}
        )

        nbs_risk = nbs.get("risk", "MEDIUM")

        if nbs_risk == "LOW":

            score += 15

            reasons.append("Low NBS risk")

        elif nbs_risk == "HIGH":

            score -= 20

            reasons.append("High NBS risk")

        # ----------------------------------
        # Confidence Engine
        # ----------------------------------

        confidence = results.get(
            "Confidence Engine",
            {}
        ).get("score", 50)

        score += confidence // 10

        # ----------------------------------
        # Clamp
        # ----------------------------------

        score = max(0, min(score, 100))

        availability = getattr(context.features, "data_availability", {}) or {}
        usable_evidence = any(availability.get(key) for key in (
            "xg", "form", "h2h", "goal_averages", "btts_rate"
        ))

        if not usable_evidence:
            recommendation = "WAIT"
            reasons.append("Insufficient verified match evidence; final selection withheld")

        elif trap_score >= 80:

            recommendation = "AVOID"

        elif score >= 85:

            recommendation = "STRONG BET"

        elif score >= 70:

            recommendation = "BET"

        elif under_score >= 85:

            recommendation = "UNDER LEAN STRONG"

        elif under_score >= 70:

            recommendation = "UNDER LEAN"

        else:

            recommendation = "WAIT"

        return {

            "score": score,

            "recommendation": recommendation,

            "confidence": confidence,

            "goal_probability": goal_score,

            "under_score": under_score,

            "trap_score": trap_score,

            "reasons": reasons

        }