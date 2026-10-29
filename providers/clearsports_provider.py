import requests
from pathlib import Path


class ClearSportsProvider:
    BASE_URL = "https://api.clearsportsapi.com/api/v1"
    KEY_PATH = Path("config/clearsports_key.txt")

    def __init__(self):
        try:
            self.api_key = self.KEY_PATH.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            self.api_key = ""

    def _require_key(self):
        if not self.api_key:
            raise RuntimeError(
                "ClearSports is not configured: add the API key to "
                "config/clearsports_key.txt before requesting this provider."
            )

    def news(self):
        self._require_key()
        response = requests.get(
            f"{self.BASE_URL}/news",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def predictions(self, league="epl"):
        self._require_key()
        response = requests.get(
            f"{self.BASE_URL}/soccer/predictions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            params={"league": league},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def team_stats(self, league="epl", team_id=None):
        self._require_key()
        response = requests.get(
            f"{self.BASE_URL}/{league}/team-stats",
            headers={"Authorization": f"Bearer {self.api_key}"},
            params={"team_id": team_id},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def player_stats(self, league="epl", team_id=None):
        self._require_key()
        response = requests.get(
            f"{self.BASE_URL}/{league}/player-stats",
            headers={"Authorization": f"Bearer {self.api_key}"},
            params={"team_id": team_id},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def game_odds(self, league="epl"):
        self._require_key()
        response = requests.get(
            f"{self.BASE_URL}/{league}/game-odds",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()
