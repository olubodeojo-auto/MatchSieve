import unittest
from unittest.mock import patch
from matchsieve.providers.sportscore import SportScoreProvider
from matchsieve.providers.openligadb import OpenLigaDBProvider
from matchsieve.providers.football_data_org import FootballDataOrgProvider
from matchsieve.providers.catalog import list_providers

class ProviderAdapterTests(unittest.TestCase):
    @patch('matchsieve.providers.sportscore.get_json')
    def test_sportscore_maps_documented_shape(self,mock):
        mock.return_value={'data':[{'id':17,'date':'2026-10-25T16:30:00Z','home_team':{'name':'Home FC'},'away_team':{'name':'Away FC'},'competition':{'name':'Test Cup'},'status':'upcoming'}]}
        rows=SportScoreProvider().fetch_fixtures('2026-10-25')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['home_team'],'Home FC')
        self.assertEqual(rows[0]['source_key'],'sportscore')

    @patch('matchsieve.providers.openligadb.get_json')
    def test_openligadb_maps_final_score(self,mock):
        mock.return_value=[{'matchID':1,'leagueName':'Test','matchDateTimeUTC':'2026-10-01T18:00:00Z','team1':{'teamName':'A'},'team2':{'teamName':'B'},'matchResults':[{'resultName':'Endergebnis','pointsTeam1':3,'pointsTeam2':0}]}]
        rows=OpenLigaDBProvider().fetch_fixtures('bl1','2026')
        self.assertEqual(rows[0]['home_score'],3); self.assertEqual(rows[0]['away_score'],0)

    @patch('matchsieve.providers.football_data_org.get_json')
    @patch.dict('os.environ', {'FOOTBALL_DATA_ORG_TOKEN': 'unit-test-token'})
    def test_football_data_org_maps_fixture_and_final_score(self, mock):
        mock.return_value={'matches':[{'id':41,'utcDate':'2026-10-25T15:00:00Z','status':'FINISHED',
            'competition':{'name':'Synthetic League','code':'SL'},'season':{'startDate':'2026-08-01'},
            'homeTeam':{'name':'Example Home'},'awayTeam':{'name':'Example Away'},
            'score':{'fullTime':{'home':2,'away':1},'halfTime':{'home':1,'away':0}}}]}
        rows=FootballDataOrgProvider().fetch_fixtures('2026-10-25','2026-10-25','SL')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['home_team'],'Example Home')
        self.assertEqual(rows[0]['away_team'],'Example Away')
        self.assertEqual(rows[0]['home_score'],2)
        self.assertEqual(rows[0]['away_score'],1)
        self.assertEqual(rows[0]['source_key'],'football_data_org')
        self.assertIn('X-Auth-Token', mock.call_args.kwargs['headers'])

    def test_catalog_contains_legacy_and_free_candidates_without_enabling(self):
        keys={p['key']:p for p in list_providers()}
        for k in ('sportmonks','football_data_org','footballdata_io','livefootball','sportscore','clearsports','the_odds_api','openweather','football_data_co_uk','openligadb'):
            self.assertIn(k,keys)
        self.assertEqual(keys['football_data_co_uk']['kind'],'local_csv')

if __name__=='__main__': unittest.main()
