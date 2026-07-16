import requests
from pathlib import Path


class ClearSportsProvider:

    BASE_URL = "https://api.clearsportsapi.com/api/v1"

    def __init__(self):

        self.api_key = Path(
            "config/clearsports_key.txt"
        ).read_text().strip()

    def news(self):

        response = requests.get(

            f"{self.BASE_URL}/news",

            headers={
                "Authorization": f"Bearer {self.api_key}"
            }

        )

        response.raise_for_status()

        return response.json()

    def predictions(self, league="epl"):

        response = requests.get(

            f"{self.BASE_URL}/soccer/predictions",

            headers={
                "Authorization": f"Bearer {self.api_key}"
            },

            params={
                "league": league
            }

        )

        response.raise_for_status()

        return response.json()

    def team_stats(self, league="epl", team_id=None):

        response = requests.get(

            f"{self.BASE_URL}/{league}/team-stats",

            headers={
                "Authorization": f"Bearer {self.api_key}"
            },

            params={
                "team_id": team_id
            }

        )

        response.raise_for_status()

        return response.json()

    def player_stats(self, league="epl", team_id=None):

        response = requests.get(

            f"{self.BASE_URL}/{league}/player-stats",

            headers={
                "Authorization": f"Bearer {self.api_key}"
            },

            params={
                "team_id": team_id
            }

        )

        response.raise_for_status()

        return response.json()

    def game_odds(self, league="epl"):

        response = requests.get(

            f"{self.BASE_URL}/{league}/game-odds",

            headers={
                "Authorization": f"Bearer {self.api_key}"
            }

        )

        response.raise_for_status()

        return response.json()