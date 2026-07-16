from extractors.base_extractor import BaseExtractor


class DefenceExtractor(BaseExtractor):

    def extract(self, match, features):

        features.home_defence_strength = round(

            max(0, 100 - features.away_xg * 40),

            2

        )

        features.away_defence_strength = round(

            max(0, 100 - features.home_xg * 40),

            2

        )

        return features