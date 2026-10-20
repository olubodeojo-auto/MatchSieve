import csv
import tempfile
import unittest
from pathlib import Path

from matchsieve.repository import Repository
from matchsieve.importers import import_csv, normalize_row
from matchsieve.analytics import build_evidence
from matchsieve.reporting import generate_report
from matchsieve.db import table_counts


class MatchSieveArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / 'test.sqlite3'
        self.repo = Repository(self.db_path)

    def tearDown(self):
        self.temp.cleanup()

    def add_result(self, date, home, away, hs, aws, competition='Test League'):
        return self.repo.add_fixture({
            'competition': competition, 'kickoff_utc': date, 'home_team': home, 'away_team': away,
            'home_score': hs, 'away_score': aws, 'status': 'finished',
            'source_key': 'unit_test', 'source_ref': 'synthetic-test-row',
        }, source_key='unit_test', source_ref='synthetic-test-row', raw_payload={'date':date,'home':home,'away':away,'score':[hs,aws]})

    def populate(self):
        self.add_result('2026-11-01T12:00:00Z','North City','Other A',2,1)
        self.add_result('2026-11-04T12:00:00Z','Other B','North City',4,2)
        self.add_result('2026-11-07T12:00:00Z','North City','Other C',0,0)
        self.add_result('2026-11-10T12:00:00Z','Other D','North City',1,1)
        self.add_result('2026-11-13T12:00:00Z','North City','Other E',3,1)
        self.add_result('2026-11-02T12:00:00Z','Other F','South United',0,1)
        self.add_result('2026-11-05T12:00:00Z','South United','Other G',2,2)
        self.add_result('2026-11-08T12:00:00Z','Other H','South United',3,0)
        self.add_result('2026-11-11T12:00:00Z','South United','Other I',1,0)
        self.add_result('2026-11-14T12:00:00Z','Other J','South United',2,3)
        return self.repo.add_fixture({'competition':'Test League','kickoff_utc':'2026-11-21T15:00:00Z',
            'home_team':'North City','away_team':'South United','status':'scheduled','source_key':'manual_csv','source_ref':'schedule.csv'},
            source_key='manual_csv',source_ref='schedule.csv',raw_payload={'fixture':'future'})

    def test_deduplicates_same_day_fixture_from_two_sources(self):
        a = self.repo.add_fixture({'competition':'League','kickoff_utc':'2026-11-21T12:00:00Z','home_team':'A FC','away_team':'B FC','source_key':'csv'},source_key='csv',raw_payload={'v':1})
        b = self.repo.add_fixture({'competition':'League','kickoff_utc':'2026-11-21T14:00:00Z','home_team':'A FC','away_team':'B FC','source_key':'api'},source_key='api',raw_payload={'v':2})
        self.assertEqual(a,b)
        self.assertEqual(len(self.repo.list_fixtures()),1)

    def test_under45_evidence_explicitly_counts_five_plus_games(self):
        fixture_id=self.populate()
        e=build_evidence(self.repo,fixture_id,'UNDER_4_5')
        self.assertEqual(e['home_form']['sample_size'],5)
        self.assertEqual(e['home_form']['five_plus_goals_count'],1)
        self.assertEqual(e['away_form']['five_plus_goals_count'],1)
        self.assertEqual(e['status'],'READY_FOR_REVIEW')
        self.assertTrue(any('5+ total goals' in line for line in e['counter_signals']))
        self.assertIn('injury', '\n'.join(e['missing_information']).lower())

    def test_sparse_history_is_limited_evidence_not_a_prediction(self):
        fixture_id=self.repo.add_fixture({'competition':'League','kickoff_utc':'2026-11-21','home_team':'A','away_team':'B','source_key':'manual','source_ref':'typed'},source_key='manual',raw_payload={'fixture':True})
        e=build_evidence(self.repo,fixture_id,'BTTS')
        self.assertEqual(e['status'],'LIMITED_EVIDENCE')
        self.assertEqual(e['home_form']['sample_size'],0)
        self.assertIn('probabilities',e['method_note'])

    def test_csv_import_football_data_aliases_and_preserves_snapshot(self):
        p=Path(self.temp.name)/'matches.csv'
        p.write_text('Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HS,AS\nE0,13/09/2025,Alpha,Beta,2,1,H,9,4\n',encoding='utf-8')
        result=import_csv(p,self.repo,source_key='football_data_co_uk')
        self.assertEqual(result['imported'],1)
        self.assertEqual(len(result['errors']),0)
        f=self.repo.list_fixtures()[0]
        self.assertEqual(f['home_team'],'Alpha')
        self.assertEqual(f['home_score'],2)
        self.assertEqual(f['away_score'],1)
        from matchsieve.db import connect
        c=connect(self.db_path)
        try:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM source_snapshots').fetchone()[0],1)
            self.assertGreaterEqual(c.execute('SELECT COUNT(*) FROM field_observations').fetchone()[0],1)
        finally:c.close()

    def test_report_version_saved_to_db_and_markdown(self):
        fixture_id=self.populate()
        one=generate_report(fixture_id,'UNDER_4_5',self.repo)
        two=generate_report(fixture_id,'UNDER_4_5',self.repo)
        self.assertEqual(two['report_id'],one['report_id']+1)
        self.assertTrue(Path(one['path']).exists())
        self.assertIn('Signals against',one['markdown'])
        self.assertIn('Publication status',one['markdown'])
        self.assertEqual(table_counts(self.db_path)['research_reports'],2)
        # Reports refresh human-readable indexes beside this test database, not in the live project.
        self.assertTrue((Path(self.temp.name) / 'knowledge-base' / 'INDEX.md').exists())
        self.assertTrue((Path(self.temp.name) / 'knowledge-base' / 'weeks').exists())


    def test_reimporting_same_payload_does_not_duplicate_observations(self):
        p=Path(self.temp.name)/'one.csv'
        p.write_text('Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,HS,AS\nE0,2025-09-13,Alpha,Beta,2,1,9,4\n',encoding='utf-8')
        import_csv(p,self.repo,source_key='football_data_co_uk')
        from matchsieve.db import connect
        conn=connect(self.db_path)
        try: before=conn.execute('SELECT COUNT(*) FROM field_observations').fetchone()[0]
        finally: conn.close()
        import_csv(p,self.repo,source_key='football_data_co_uk')
        conn=connect(self.db_path)
        try:
            after=conn.execute('SELECT COUNT(*) FROM field_observations').fetchone()[0]
            self.assertEqual(before,after)
        finally: conn.close()

    def test_fixture_csv_export_is_excel_readable(self):
        self.add_result('2026-11-01T12:00:00Z','North City','Other A',2,1)
        from matchsieve.exports import export_fixtures_csv
        path=Path(self.temp.name)/'exports'/'archive.csv'
        result=export_fixtures_csv(self.repo,path)
        self.assertEqual(result['exported_rows'],1)
        with path.open(encoding='utf-8-sig',newline='') as fh:
            rows=list(csv.DictReader(fh))
        self.assertEqual(rows[0]['home_team'],'North City')
        self.assertEqual(rows[0]['home_score'],'2')


    def test_full_archive_jsonl_export_is_streamed_and_typed(self):
        self.add_result('2026-11-01T12:00:00Z','North City','Other A',2,1)
        from matchsieve.exports import export_archive_jsonl
        path=Path(self.temp.name)/'exports'/'full.jsonl'
        out=export_archive_jsonl(self.repo,path)
        lines=path.read_text(encoding='utf-8').splitlines()
        self.assertTrue(out['streaming'])
        self.assertGreaterEqual(out['records_exported'],2)
        self.assertEqual(__import__('json').loads(lines[0])['record_type'],'archive_export_metadata')
        self.assertTrue(any(__import__('json').loads(x)['record_type']=='fixtures' for x in lines[1:]))

    def test_normalizer_rejects_missing_teams(self):
        with self.assertRaises(ValueError): normalize_row({'Date':'13/09/2025','HomeTeam':'A'})

if __name__=='__main__': unittest.main()
