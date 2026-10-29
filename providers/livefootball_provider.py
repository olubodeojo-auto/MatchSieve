import requests
from pathlib import Path


class LiveFootballProvider:
    BASE_URL = "https://live-football-api.com/api/v1"
    KEY_PATH = Path("config/livefootball_key.txt")

    def __init__(self):
        try:
            self.api_key = self.KEY_PATH.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            self.api_key = ""

    def _require_key(self):
        if not self.api_key:
            raise RuntimeError(
                "LiveFootball is not configured: add the API key to "
                "config/livefootball_key.txt before requesting this provider."
            )

    def fixtures(self, date=None):
        self._require_key()
        params = {"api_key": self.api_key}
        if date:
            params["date"] = date
        response = requests.get(
            f"{self.BASE_URL}/matches", params=params, timeout=20
        )
        response.raise_for_status()
        return response.json()

    def live_match_details(self, match_id):
        self._require_key()
        response = requests.get(
            f"{self.BASE_URL}/live_match_details",
            params={"api_key": self.api_key, "match_id": match_id},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def lineups(self, match_id):
        self._require_key()
        response = requests.get(
            f"{self.BASE_URL}/lineups",
            params={"api_key": self.api_key, "match_id": match_id},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def h2h(self, match_id):
        self._require_key()
        response = requests.get(
            f"{self.BASE_URL}/h2h",
            params={"api_key": self.api_key, "match_id": match_id},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def injuries(self, match_id):
        self._require_key()
        response = requests.get(
            f"{self.BASE_URL}/injuries",
            params={"api_key": self.api_key, "match_id": match_id},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def leagues(self):
        self._require_key()
        response = requests.get(
            f"{self.BASE_URL}/leagues",
            params={"api_key": self.api_key},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()
