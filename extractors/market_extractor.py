from extractors.base_extractor import BaseExtractor


class MarketExtractor(BaseExtractor):

    def extract(self, match, features):

        features.home_probability = match.home_probability or 0

        features.draw_probability = match.draw_probability or 0

        features.away_probability = match.away_probability or 0

        features.home_odds = match.home_odds or 0

        features.draw_odds = match.draw_odds or 0

        features.away_odds = match.away_odds or 0

        return features