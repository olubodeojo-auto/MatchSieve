from extractors.base_extractor import BaseExtractor


class RiskExtractor(BaseExtractor):

    def extract(self, match, features):

        features.data_quality = 100

        features.provider_agreement = 100

        return features