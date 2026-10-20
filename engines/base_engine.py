class BaseEngine:

    def __init__(self, name):
        self.name = name

    def calculate(self, context):
        raise NotImplementedError(
            f"{self.name} must implement calculate(context)."
        )