from providers.football_data_org import FootballDataAPI

api = FootballDataAPI()

print("Testing Football-Data.org...\n")

data = api.competitions()

print("Available Competitions:\n")

for comp in data["competitions"]:
    print(comp["code"], "-", comp["name"])