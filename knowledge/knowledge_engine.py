import json
from pathlib import Path


class KnowledgeEngine:

    def __init__(self):

        path = Path("knowledge/weights.json")

        self.weights = json.loads(path.read_text())

    def get(self, engine):

        return self.weights.get(engine, {})