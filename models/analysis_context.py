class AnalysisContext:

    def __init__(self, match=None, features=None):

        self.match = match

        self.features = features

        self.results = {}

        self.logs = []

        self.flags = []

        self.evidence = []

        self.contradictions = []

        self.metadata = {}

    def add_result(self, name, result):

        self.results[name] = result

    def get_result(self, name):

        return self.results.get(name)

    def add_flag(self, flag):

        self.flags.append(flag)

    def add_log(self, text):

        self.logs.append(text)