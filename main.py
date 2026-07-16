from providers.provider_manager import ProviderManager

print("=" * 60)
print("          BOJO SENTINEL AI")
print("    Football Intelligence Platform")
print("=" * 60)

api = ProviderManager()

print("\nMAIN MENU")
print("1. Analyze Match")
print("2. Live Scanner")
print("3. Exit")
print()

choice = input("Select option: ")

if choice == "1":

    fixtures = api.get_fixtures()

    if fixtures is None:
        exit()

    print("\nToday's Fixtures")
    print("-" * 60)

    matches = fixtures[:10]

    for i, match in enumerate(matches, start=1):
        print(f"{i}. {match.get('name', 'Unknown Match')}")

    print()

    selection = int(input("Select fixture number: "))

    fixture = matches[selection - 1]

    print("\nLoading match information...\n")

    details = api.fixture(fixture["id"])

    if details is None:
        exit()

    data = details["data"]

    print("=" * 60)
    print("MATCH INFORMATION")
    print("=" * 60)

    print("Fixture :", data.get("name"))
    print("League  :", data.get("league", {}).get("name", "Unknown"))
    print("Venue   :", data.get("venue", {}).get("name", "Unknown"))
    print("Status  :", data.get("state", {}).get("state", "Unknown"))
    print("Kickoff :", data.get("starting_at", "Unknown"))
    print("Round   :", data.get("round", {}).get("name", "Unknown"))
    print("Season  :", data.get("season", {}).get("name", "Unknown"))

    print()

    participants = data.get("participants", [])

    home_team = "Unknown"
    away_team = "Unknown"

    for team in participants:
        if team.get("meta", {}).get("location") == "home":
            home_team = team.get("name")
        elif team.get("meta", {}).get("location") == "away":
            away_team = team.get("name")

        print("Home Team :", home_team)
    print("Away Team :", away_team)

    print("\nMATCH STATISTICS")
    print("-" * 60)

    stats = api.statistics(fixture["id"])

    print(stats)


elif choice == "2":

    print("\nChecking Live Matches...\n")

    live = api.live()

    if live is None:
        exit()

    matches = live["data"]

    if len(matches) == 0:
        print("No live matches found.")
    else:
        print(f"{len(matches)} live matches found.\n")

        for match in matches[:10]:
            print(match.get("name"))

else:

    print("Goodbye.")
    print("\nTESTING TEAM MATCHES...\n")

test = api.team_matches(85)

print(test)