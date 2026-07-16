from services.normalized_match import NormalizedMatch


class DataFusion:

    def __init__(self):

        self.match = NormalizedMatch()

    # --------------------------------------------------
    # Main Merge
    # --------------------------------------------------

    def merge(self, incoming):

        self.match.add_provider(incoming.provider)

        self.match.add_raw_data(
            incoming.provider,
            incoming.to_dict()
        )

        self._merge_identity(incoming)
        self._merge_competition(incoming)
        self._merge_teams(incoming)
        self._merge_status(incoming)
        self._merge_score(incoming)
        self._merge_xg(incoming)
        self._merge_probabilities(incoming)
        self._merge_odds(incoming)
        self._merge_rankings(incoming)
        self._merge_form(incoming)
        self._merge_weather(incoming)
        self._merge_statistics(incoming)
        self._merge_events(incoming)
        self._merge_h2h(incoming)
        self._merge_injuries(incoming)
        self._merge_predictions(incoming)
        self._merge_news(incoming)
        self._merge_bookmakers(incoming)
        self._merge_confidence(incoming)

        return self.match

    # --------------------------------------------------
    # Identity
    # --------------------------------------------------

    def _merge_identity(self, source):

        if self.match.fixture_id is None:
            self.match.fixture_id = source.fixture_id

        if self.match.provider is None:
            self.match.provider = source.provider

    # --------------------------------------------------
    # Competition
    # --------------------------------------------------

    def _merge_competition(self, source):

        if not self.match.league:
            self.match.league = source.league

        if not self.match.country:
            self.match.country = source.country

        if not self.match.season:
            self.match.season = source.season

        if not self.match.round:
            self.match.round = source.round

        if not self.match.kickoff:
            self.match.kickoff = source.kickoff

        if not self.match.venue:
            self.match.venue = source.venue

    # --------------------------------------------------
    # Teams
    # --------------------------------------------------

    def _merge_teams(self, source):

        if not self.match.home_team:
            self.match.home_team = source.home_team

        if not self.match.away_team:
            self.match.away_team = source.away_team

        if not self.match.home_logo:
            self.match.home_logo = source.home_logo

        if not self.match.away_logo:
            self.match.away_logo = source.away_logo

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    def _merge_status(self, source):

        if source.status is not None:
            self.match.status = source.status

        if source.minute is not None:
            self.match.minute = source.minute

    # --------------------------------------------------
    # Score
    # --------------------------------------------------

    def _merge_score(self, source):

        self.match.home_score = max(
            self.match.home_score,
            source.home_score
        )

        self.match.away_score = max(
            self.match.away_score,
            source.away_score
        )

    # --------------------------------------------------
    # xG
    # --------------------------------------------------

    def _merge_xg(self, source):

        if source.home_xg is not None:
            self.match.home_xg = source.home_xg

        if source.away_xg is not None:
            self.match.away_xg = source.away_xg

    # --------------------------------------------------
    # Probabilities
    # --------------------------------------------------

    def _merge_probabilities(self, source):

        if source.home_probability is not None:
            self.match.home_probability = source.home_probability

        if source.draw_probability is not None:
            self.match.draw_probability = source.draw_probability

        if source.away_probability is not None:
            self.match.away_probability = source.away_probability

    # --------------------------------------------------
    # Odds
    # --------------------------------------------------

    def _merge_odds(self, source):

        if source.home_odds is not None:
            self.match.home_odds = source.home_odds

        if source.draw_odds is not None:
            self.match.draw_odds = source.draw_odds

        if source.away_odds is not None:
            self.match.away_odds = source.away_odds

    # --------------------------------------------------
    # Rankings
    # --------------------------------------------------

    def _merge_rankings(self, source):

        if source.home_rank is not None:
            self.match.home_rank = source.home_rank

        if source.away_rank is not None:
            self.match.away_rank = source.away_rank

        if source.home_points is not None:
            self.match.home_points = source.home_points

        if source.away_points is not None:
            self.match.away_points = source.away_points

    # --------------------------------------------------
    # Form
    # --------------------------------------------------

    def _merge_form(self, source):

        if source.home_form:
            self.match.home_form = source.home_form

        if source.away_form:
            self.match.away_form = source.away_form

    # --------------------------------------------------
    # Weather
    # --------------------------------------------------

    def _merge_weather(self, source):

        if source.weather:
            self.match.weather = source.weather

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    def _merge_statistics(self, source):

        self.match.statistics.update(source.statistics)

    # --------------------------------------------------
    # Events
    # --------------------------------------------------

    def _merge_events(self, source):

        self.match.events.extend(source.events)

    # --------------------------------------------------
    # H2H
    # --------------------------------------------------

    def _merge_h2h(self, source):

        if source.h2h:
            self.match.h2h = source.h2h

    # --------------------------------------------------
    # Injuries
    # --------------------------------------------------

    def _merge_injuries(self, source):

        if source.injuries:
            self.match.injuries = source.injuries

    # --------------------------------------------------
    # Predictions
    # --------------------------------------------------

    def _merge_predictions(self, source):

        self.match.predictions.update(source.predictions)

    # --------------------------------------------------
    # News
    # --------------------------------------------------

    def _merge_news(self, source):

        self.match.news.extend(source.news)

    # --------------------------------------------------
    # Bookmakers
    # --------------------------------------------------

    def _merge_bookmakers(self, source):

        self.match.bookmakers.extend(source.bookmakers)

    # --------------------------------------------------
    # Confidence
    # --------------------------------------------------

    def _merge_confidence(self, source):

        self.match.confidence.update(source.confidence)