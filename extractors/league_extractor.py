from extractors.base_extractor import BaseExtractor


class LeagueExtractor(BaseExtractor):

    def extract(self, match, features):

        features.league = match.league

        features.country = match.country

        features.league_strength = 0

        features.league_goal_average = 0

        features.league_btts_rate = 0

        features.league_over25_rate = 0

        return features