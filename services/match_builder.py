from services.provider_router import ProviderRouter
from services.adapters.footballdata_io_adapter import FootballDataIOAdapter


class MatchBuilder:

    def __init__(self):
        self.router = ProviderRouter()

    def build_today(self):
        data = self.router.get_today_matches()
        if not data:
            return []

        payload = data.get("data") if isinstance(data, dict) else None
        rows = payload.get("matches") if isinstance(payload, dict) else None
        if not isinstance(rows, list):
            print("FootballData.io response did not contain a data.matches list")
            return []

        matches = []
        for index, row in enumerate(rows):
            try:
                normalized = FootballDataIOAdapter.convert(row)
            except (TypeError, ValueError, KeyError) as exc:
                print(f"Skipping malformed FootballData.io fixture at index {index}: {exc}")
                continue
            matches.append(normalized)

        return matches

    def build_one(self, match):
        return FootballDataIOAdapter.convert(match)
