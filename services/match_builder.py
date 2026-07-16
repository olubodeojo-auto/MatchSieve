from services.provider_router import ProviderRouter
from services.adapters.footballdata_io_adapter import FootballDataIOAdapter


class MatchBuilder:

    def __init__(self):

        self.router = ProviderRouter()

    def build_today(self):

        data = self.router.get_today_matches()

        if not data:
            return []

        matches = []

        for match in data["data"]["matches"]:

            normalized = FootballDataIOAdapter.convert(match)

            matches.append(normalized)

        return matches

    def build_one(self, match):

        return FootballDataIOAdapter.convert(match)