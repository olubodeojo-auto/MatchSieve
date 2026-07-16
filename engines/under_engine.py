from engines.base_engine import BaseEngine


class UnderEngine(BaseEngine):

    def __init__(self):
        super().__init__("Under Engine")

    def calculate(self, features):

        score = 50
        reasons = []

        # -----------------------
        # Goal Average
        # -----------------------

        avg_goals = (
            features.home_goal_average +
            features.away_goal_average
        )

        if avg_goals <= 1.8:
            score += 20
            reasons.append("Very low goal average")

        elif avg_goals <= 2.3:
            score += 10
            reasons.append("Low goal average")

        elif avg_goals >= 3.2:
            score -= 20
            reasons.append("Very high goal average")

        # -----------------------
        # Defence
        # -----------------------

        avg_conceded = (
            features.home_conceded_average +
            features.away_conceded_average
        )

        if avg_conceded <= 1.5:
            score += 15
            reasons.append("Strong defensive profile")

        elif avg_conceded >= 3:
            score -= 15
            reasons.append("Weak defensive profile")

        # -----------------------
        # Clean Sheets
        # -----------------------

        clean = (
            features.home_clean_sheet_rate +
            features.away_clean_sheet_rate
        ) / 2

        if clean >= 50:
            score += 10
            reasons.append("High clean sheet rate")

        # -----------------------
        # BTTS
        # -----------------------

        if features.btts_rate <= 40:
            score += 10
            reasons.append("Low BTTS rate")

        elif features.btts_rate >= 70:
            score -= 10
            reasons.append("High BTTS rate")

        # -----------------------
        # H2H
        # -----------------------

        if features.under25 >= 60:
            score += 15
            reasons.append("Strong H2H Under trend")

        elif features.over25 >= 70:
            score -= 15
            reasons.append("H2H goals trend")

        # -----------------------
        # Market Stability
        # -----------------------

        if features.market_stability == "VOLATILE":
            score -= 5
            reasons.append("Volatile market")

        # -----------------------
        # Clamp
        # -----------------------

        score = max(0, min(score, 100))

        stars = round(score / 20)

        return {

            "score": score,

            "stars": stars,

            "under05": score >= 92,

            "under15": score >= 82,

            "under25": score >= 72,

            "under35": score >= 60,

            "under45": score >= 45,

            "reasons": reasons

        }