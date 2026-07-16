from extractors.base_extractor import BaseExtractor


class GoalExtractor(BaseExtractor):

    def extract(self, match, features):

        features.home_xg = match.home_xg or 0

        features.away_xg = match.away_xg or 0

        features.total_xg = round(

            features.home_xg +

            features.away_xg,

            2

        )

        return features