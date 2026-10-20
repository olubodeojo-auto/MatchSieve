from engines.base_engine import BaseEngine


class FormEngine(BaseEngine):

    def __init__(self):
        super().__init__("Form Engine")

    def calculate(self, context):

        features = context.features

        home_points = sum(features.home_last5)

        away_points = sum(features.away_last5)

        difference = home_points - away_points

        if difference >= 8:

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

            "rating": rating

        }