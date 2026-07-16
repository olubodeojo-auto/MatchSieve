from core.api import SportMonksAPI


class HistoryProvider:

    def __init__(self):
        self.api = SportMonksAPI()

    def last_matches(self, team_id):

        return self.api.team_matches(team_id)

    def head_to_head(self, team1, team2):

        return self.api.head_to_head(team1, team2)