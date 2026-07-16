class EngineResult:

    def __init__(self):

        self.engine = ""

        self.score = 0

        self.rating = ""

        self.recommendation = ""

        self.reasons = []

        self.warnings = []

        self.confidence = 0

    def to_dict(self):

        return self.__dict__