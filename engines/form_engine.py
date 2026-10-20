from engines.base_engine import BaseEngine


class FormEngine(BaseEngine):

    def __init__(self):
        super().__init__("Form Engine")

    def calculate(self, context):
        features = context.features

        # FormExtractor converts W/D/L markers to 3/1/0 points.
        home_points = sum(features.home_last5)
        away_points = sum(features.away_last5)
        difference = home_points - away_points
        evidence_available = bool(features.home_last5 and features.away_last5)

        if not evidence_available:
            rating = "UNKNOWN"
        elif difference >= 8:
            rating = "HOME VERY STRONG"
        elif difference >= 4:
            rating = "HOME STRONG"
        elif difference <= -8:
            rating = "AWAY VERY STRONG"
        elif difference <= -4:
            rating = "AWAY STRONG"
        else:
            rating = "EVEN"

        return {
            "home_points": home_points,
            "away_points": away_points,
            "difference": difference,
            "rating": rating,
            "evidence_available": evidence_available,
        }
