from providers.footballdata_io import FootballDataIO
from services.adapters.footballdata_io_adapter import FootballDataIOAdapter

provider = FootballDataIO()

data = provider.fixtures()

match = data["data"]["matches"][0]

normalized = FootballDataIOAdapter.convert(match)

print(normalized.to_dict())