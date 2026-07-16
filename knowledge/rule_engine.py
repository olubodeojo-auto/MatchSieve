import json
from pathlib import Path


class RuleEngine:

    def __init__(self):

        self.rules = json.loads(
            Path("knowledge/sentinel_rules.json").read_text()
        )

    def recommendation(self, name):

        return self.rules["recommendations"].get(name, {})

    def exists(self, section):

        return section in self.rules

    def get(self, section):

        return self.rules.get(section, {})

    def reload(self):

        self.rules = json.loads(
            Path("knowledge/sentinel_rules.json").read_text()
        )