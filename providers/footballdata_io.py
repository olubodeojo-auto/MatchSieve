import requests
from pathlib import Path


class FootballDataIO:

    BASE_URL = "https://footballdata.io/api/v1"

    def __init__(self):

        self.api_key = Path(
            "config/footballdata_key.txt"
        ).read_text().strip()

    def fixtures(self):

        response = requests.get(

            f"{self.BASE_URL}/fixtures/today",

            headers={
                "Authorization": f"Bearer {self.api_key}"
            }

        )

        response.raise_for_status()

        return response.json()

    def live(self):

        response = requests.get(

            f"{self.BASE_URL}/fixtures/live",

            headers={
                "Authorization": f"Bearer {self.api_key}"
            }

        )

        response.raise_for_status()

        return response.json()

    def upcoming(self):

        response = requests.get(

            f"{self.BASE_URL}/fixtures/upcoming",

            headers={
                "Authorization": f"Bearer {self.api_key}"
            }

        )

        response.raise_for_status()

        return response.json()

    def match(self, match_id):

        response = requests.get(

            f"{self.BASE_URL}/matches/{match_id}",

            headers={
                "Authorization": f"Bearer {self.api_key}"
            }

        )

        response.raise_for_status()

        return response.json()