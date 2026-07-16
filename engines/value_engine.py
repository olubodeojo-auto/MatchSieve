from engines.base_engine import BaseEngine


class ValueEngine(BaseEngine):

    def __init__(self):
        super().__init__("Value Engine")

    def calculate(self, context):

        features = context.features

        score = 50
        reasons = []

        home = features.home_odds
        draw = features.draw_odds
        away = features.away_odds

        goal = context.results.get(
            "Goal Probability Engine",
            {}
        ).get("score", 50)

        # ----------------------------------
        # Goal Probability
        # ----------------------------------

        if goal >= 80:
            score += 15
            reasons.append("High internal probability")

        elif goal <= 30:
            score -= 10
            reasons.append("Low internal probability")

        # ----------------------------------
        # Market Availability
        # ----------------------------------

        if home and draw and away:

            score += 10

            reasons.append("Market data available")

            favourite = min(home, away)

            if favourite <= 1.60:

                score -= 10

                reasons.append("Heavy favourite")

            elif favourite >= 2.20:

                score += 10

                reasons.append("Balanced market")

        else:

            reasons.append("No odds available")

        # ----------------------------------
        # Trap Engine
        # ----------------------------------

        trap = context.results.get("Trap Engine", {})

        if trap.get("score", 0) >= 70:

            score -= 20

            reasons.append("Trap risk detected")

        # ----------------------------------
        # Clamp
        # ----------------------------------

        score = max(0, min(score, 100))

        if score >= 80:
            value = "EXCELLENT"

        elif score >= 65:
            value = "GOOD"

        elif score >= 50:
            value = "FAIR"

        else:
            value = "POOR"

        features.value_score = score

        return {

            "score": score,

            "value": value,

            "reasons": reasons

        }
    