class DefenceCalculator:

    @staticmethod
    def calculate(features):

        xg = features.away_xg

        return round(max(0, 100 - xg * 40), 2)

    @staticmethod
    def calculate_away(features):

        xg = features.home_xg

        return round(max(0, 100 - xg * 40), 2)