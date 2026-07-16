import requests


class SportScoreProvider:

    BASE_URL = "https://sportscore.com/api"

    def fixtures(self):

        response = requests.get(

            f"{self.BASE_URL}/widget/matches/",

            params={

                "sport": "football",
                "limit": 20

            }

        )

        response.raise_for_status()

        return response.json()

    def fixture(self, slug):

        response = requests.get(

            f"{self.BASE_URL}/widget/match/",

            params={

                "sport": "football",
                "slug": slug

            }

        )

        response.raise_for_status()

        return response.json()

    def standings(self, slug):

        response = requests.get(

            f"{self.BASE_URL}/widget/standings/",

            params={

                "sport": "football",
                "slug": slug

            }

        )

        response.raise_for_status()

        return response.json()