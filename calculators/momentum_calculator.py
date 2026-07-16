class MomentumCalculator:

    @staticmethod
    def calculate(features):

        return round(features.home_probability, 2)

    @staticmethod
    def calculate_away(features):

        return round(features.away_probability, 2)