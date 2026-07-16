from engines.base_engine import BaseEngine


class DefenceStrengthEngine(BaseEngine):

    def __init__(self):
        super().__init__("Defence Strength Engine")

    def calculate(self, context):

        features = context.features

        score = 50
        reasons = []

        # ----------------------------------
        # Goals Conceded
        # ----------------------------------

        avg = (
            features.home_conceded_average +
            features.away_conceded_average
        ) / 2

        if avg <= 0.8:
            score += 20
            reasons.append("Excellent defensive record")

        elif avg <= 1.2:
            score += 10
            reasons.append("Good defensive record")

        elif avg >= 2.0:
            score -= 15
            reasons.append("Weak defensive record")

        # ----------------------------------
        # Clean Sheets
        # ----------------------------------

        clean = (
            features.home_clean_sheet_rate +
            features.away_clean_sheet_rate
        ) / 2

        if clean >= 50:
            score += 15
            reasons.append("High clean sheet rate")

        elif clean <= 20:
            score -= 10
            reasons.append("Few clean sheets")

        # ----------------------------------
        # BTTS
        # ----------------------------------

        if features.btts_rate <= 40:
            score += 10
            reasons.append("Low BTTS rate")

        elif features.btts_rate >= 70:
            score -= 10
            reasons.append("High BTTS rate")

        # ----------------------------------
        # xG Against
        # ----------------------------------

        if features.total_xg <= 2.0:
            score += 10
            reasons.append("Low expected goals against")

        elif features.total_xg >= 3.2:
            score -= 10
            reasons.append("High expected goals against")

        # ----------------------------------
        # Momentum
        # ----------------------------------

        if features.momentum == "RISING":
            score += 5
            reasons.append("Defensive momentum improving")

        elif features.momentum == "DECLINING":
            score -= 5
            reasons.append("Defensive momentum declining")

        score = max(0, min(100, score))

        features.defence_strength = score

        return {

            "score": score,

            "rating": (
                "ELITE" if score >= 90 else
                "HIGH" if score >= 75 else
                "MEDIUM" if score >= 55 else
                "LOW"
            ),

            "reasons": reasons

        }