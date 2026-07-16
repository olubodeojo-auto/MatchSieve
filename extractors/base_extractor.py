class BaseExtractor:

    def extract(self, match, features):
        raise NotImplementedError(
            "Extractor must implement extract()"
        )