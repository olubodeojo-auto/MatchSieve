from engines.base_engine import BaseEngine


class LeagueProfileEngine(BaseEngine):

    def __init__(self):
        super().__init__("League Profile Engine")

    def calculate(self, context):

        features = context.features

        score = 50
        reasons = []

        league = (features.league or "").lower()

        # -----------------------------
        # High Scoring Leagues
        # -----------------------------

        high_scoring = [
            "eredivisie",
            "bundesliga",
            "norway",
            "eliteserien",
            "sweden",
            "allsvenskan",
            "austria",
            "denmark"
        ]

        # -----------------------------
        # Lower Scoring Leagues
        # -----------------------------

        low_scoring = [
            "algeria",
            "greece",
            "romania",
            "serbia",
            "paraguay",
            "uruguay"
        ]

        for item in high_scoring:

            if item in league:

                score += 20

                reasons.append("Historically high-scoring league")

                break

        for item in low_scoring:

            if item in league:

                score -= 20

                reasons.append("Historically low-scoring league")

                break

        score = max(0, min(score, 100))

        return {

            "score": score,

            "rating": (
                "HIGH" if score >= 70 else
                "MEDIUM" if score >= 45 else
                "LOW"
            ),

            "reasons": reasons

        }