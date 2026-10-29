import requests
from pathlib import Path


class FootballDataIO:
    """Optional FootballData.io adapter with a clear no-key behavior."""

    BASE_URL = "https://footballdata.io/api/v1"
    KEY_PATH = Path("config/footballdata_key.txt")
    REQUEST_TIMEOUT_SECONDS = 20

    def __init__(self):
        # The application and offline tests must start without a paid provider key.
        # A missing key disables requests; it must never crash unrelated analysis.
        try:
            self.api_key = self.KEY_PATH.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            self.api_key = ""

    def _get_json(self, endpoint: str):
        if not self.api_key:
            raise RuntimeError(
                "FootballData.io is not configured: add the API key to "
                "config/footballdata_key.txt before requesting this provider."
            )

        response = requests.get(
            f"{self.BASE_URL}{endpoint}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json()

    def fixtures(self):
        return self._get_json("/fixtures/today")

    def live(self):
        return self._get_json("/fixtures/live")

    def upcoming(self):
        return self._get_json("/fixtures/upcoming")

    def match(self, match_id):
        return self._get_json(f"/matches/{match_id}")
