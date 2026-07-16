class BaseEngine:

    def __init__(self, name):
        self.name = name

    def calculate(self, match):
        raise NotImplementedError(
            f"{self.name} must implement calculate()."
        )