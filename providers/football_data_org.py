import requests
from pathlib import Path


class FootballDataAPI:
    BASE_URL = "https://api.football-data.org/v4"
    KEY_PATH = Path("config/football_dataorg_key.txt")

    def __init__(self):
        try:
            self.api_key = self.KEY_PATH.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            self.api_key = ""

    def _require_key(self):
        if not self.api_key:
            raise RuntimeError(
                "Football-Data.org is not configured: add the API key to "
                "config/football_dataorg_key.txt before requesting this provider."
            )

    def competitions(self):
        self._require_key()
        response = requests.get(
            f"{self.BASE_URL}/competitions",
            headers={"X-Auth-Token": self.api_key},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()
