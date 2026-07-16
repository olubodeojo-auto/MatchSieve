class ConfidenceCalculator:

    @staticmethod
    def calculate(features):

        score = 0

        if features.home_probability:
            score += 20

        if features.home_odds:
            score += 20

        if features.home_xg:
            score += 20

        if features.league:
            score += 20

        if features.home_team:
            score += 20

        return score