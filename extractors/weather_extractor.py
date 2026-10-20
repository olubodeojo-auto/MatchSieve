from extractors.base_extractor import BaseExtractor


class WeatherExtractor(BaseExtractor):

    def extract(self, match, features):

        features.weather_factor = 0

        return features