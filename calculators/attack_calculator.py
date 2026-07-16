class AttackCalculator:

    @staticmethod
    def calculate(features):

        xg = features.home_xg

        if xg <= 0:
            return 0

        return round(min(xg * 40, 100), 2)

    @staticmethod
    def calculate_away(features):

        xg = features.away_xg

        if xg <= 0:
            return 0

        return round(min(xg * 40, 100), 2)