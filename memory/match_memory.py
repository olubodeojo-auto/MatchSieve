import json
from pathlib import Path


class MatchMemory:

    FILE = Path("memory/history.json")

    def __init__(self):

        if not self.FILE.exists():
            self.FILE.write_text("[]")

    def load(self):

        return json.loads(self.FILE.read_text())

    def save(self, prediction):

        history = self.load()

        history.append(prediction)

        self.FILE.write_text(
            json.dumps(history, indent=4)
        )