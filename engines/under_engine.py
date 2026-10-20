from engines.base_engine import BaseEngine


class UnderEngine(BaseEngine):

    def __init__(self):
        super().__init__("Under Engine")

    def calculate(self, context):
        features = context.features
        available = getattr(features, "data_availability", {}) or {}
        score = 50
        reasons = []

        if available.get("goal_averages"):
            avg_goals = features.home_goal_average + features.away_goal_average
            if avg_goals <= 1.8:
                score += 20
                reasons.append("Very low goal average")
            elif avg_goals <= 2.3:
                score += 10
                reasons.append("Low goal average")
            elif avg_goals >= 3.2:
                score -= 20
                reasons.append("Very high goal average")

        if available.get("conceded_averages"):
            avg_conceded = features.home_conceded_average + features.away_conceded_average
            if avg_conceded <= 1.5:
                score += 15
                reasons.append("Strong defensive profile")
            elif avg_conceded >= 3:
                score -= 15
                reasons.append("Weak defensive profile")

        if available.get("clean_sheet_rates"):
            clean = (features.home_clean_sheet_rate + features.away_clean_sheet_rate) / 2
            if clean >= 50:
                score += 10
                reasons.append("High clean sheet rate")

        if available.get("btts_rate"):
            if features.btts_rate <= 40:
                score += 10
                reasons.append("Low BTTS rate")
            elif features.btts_rate >= 70:
                score -= 10
                reasons.append("High BTTS rate")

        if available.get("xg"):
            if features.total_xg <= 1.8:
                score += 10
                reasons.append("Low combined xG")
            elif features.total_xg >= 3.2:
                score -= 10
                reasons.append("High combined xG")

        # H2H rate fields are not currently calculated from raw H2H records,
        # so do not score under25/over25 from their default zero values.
        if features.market_stability == "VOLATILE":
            score -= 5
            reasons.append("Volatile market")

        score = max(0, min(score, 100))
        stars = round(score / 20)
        evidence_available = any(available.get(key) for key in (
            "goal_averages", "conceded_averages", "clean_sheet_rates",
            "btts_rate", "xg"
        ))

        return {
            "score": score,
            "stars": stars,
            "under05": evidence_available and score >= 92,
            "under15": evidence_available and score >= 82,
            "under25": evidence_available and score >= 72,
            "under35": evidence_available and score >= 60,
            "under45": evidence_available and score >= 60,
            "evidence_available": evidence_available,
            "reasons": reasons,
        }
