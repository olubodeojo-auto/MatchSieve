from extractors.base_extractor import BaseExtractor


class LiveExtractor(BaseExtractor):

    def extract(self, match, features):

        features.home_score = match.home_score

        features.away_score = match.away_score

        return features