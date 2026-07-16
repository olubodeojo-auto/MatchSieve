import requests
from pathlib import Path


class FootballDataAPI:

    BASE_URL = "https://api.football-data.org/v4"

    def __init__(self):
        self.api_key = Path("config/football_dataorg_key.txt").read_text().strip()

    def competitions(self):

        response = requests.get(
            f"{self.BASE_URL}/competitions",
            headers={
                "X-Auth-Token": self.api_key
            }
        )

        response.raise_for_status()

        return response.json()