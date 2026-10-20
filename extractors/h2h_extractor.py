from extractors.base_extractor import BaseExtractor


class H2HExtractor(BaseExtractor):

    def extract(self, match, features):

        features.h2h = match.h2h

        features.h2h_played = len(match.h2h)

        return features