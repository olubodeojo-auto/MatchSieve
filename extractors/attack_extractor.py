from extractors.base_extractor import BaseExtractor


class AttackExtractor(BaseExtractor):

    def extract(self, match, features):

        features.home_attack_strength = round(

            min(features.home_xg * 40, 100),

            2

        )

        features.away_attack_strength = round(

            min(features.away_xg * 40, 100),

            2

        )

        return features