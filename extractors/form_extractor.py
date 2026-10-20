from extractors.base_extractor import BaseExtractor


class FormExtractor(BaseExtractor):

    def extract(self, match, features):

        features.home_form_score = len(match.home_form)

        features.away_form_score = len(match.away_form)

        features.home_last5 = match.home_form

        features.away_last5 = match.away_form

        features.home_weighted_form = (
            features.home_form_score * 20
        )

        features.away_weighted_form = (
            features.away_form_score * 20
        )

        return features