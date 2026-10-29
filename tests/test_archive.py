import csv
import json
import tempfile
import unittest
from pathlib import Path

from matchsieve.repository import Repository
from matchsieve.repository import canonical_key
from matchsieve.importers import import_csv, normalize_row
from matchsieve.analytics import build_evidence
from matchsieve.reporting import generate_report
from matchsieve.db import connect, table_counts


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

    def test_curated_cross_provider_aliases_deduplicate_and_preserve_provenance(self):
        pairs = [
            ("Liga MX", "Guadalajara Chivas", "Necaxa", "Guadalajara", "Necaxa", "2026"),
            ("Liga MX", "Atletico San Luis", "Club Queretaro", "A San Luis", "Querétaro", "2026"),
            ("Liga MX", "FC Juarez", "Atlante FC", "Juárez", "Atlante", "2026"),
            ("CONCACAF Central American Cup", "CD Marathon", "Alianza", "Marathón", "Alianza", "2026"),
            ("WE League", "INAC Kobe Leonessa W", "JEF United W", "Leonessa", "JEF Utd", "2026"),
            ("Liga MX Femenil", "Guadalajara W", "Necaxa W", "Guadalajara", "Necaxa", "2026"),
        ]
        fixture_ids = []
        for index, (competition, home_a, away_a, home_b, away_b, season) in enumerate(pairs):
            with self.subTest(competition=competition, home=home_a):
                first = {
                    "competition": competition,
                    "kickoff_utc": "2026-10-21T03:00:00Z",
                    "home_team": home_a,
                    "away_team": away_a,
                    "season": season,
                    "source_key": "api_football",
                }
                second_competition = "WE League Women" if competition == "WE League" else competition
                second = {
                    "competition": second_competition,
                    "kickoff_utc": "2026-10-21T03:00:00Z",
                    "home_team": home_b,
                    "away_team": away_b,
                    "source_key": "livefootball",
                }
                self.assertEqual(canonical_key(first), canonical_key({**second, "season": season}))

                first_id = self.repo.add_fixture(
                    {**first, "external_id": f"api-{index}"},
                    source_key="api_football",
                    source_ref=f"api-{index}",
                    source_url="https://api.example.test",
                    raw_payload={"id": f"api-{index}"},
                )
                second_id = self.repo.add_fixture(
                    {**second, "external_id": f"live-{index}"},
                    source_key="livefootball",
                    source_ref=f"live-{index}",
                    source_url="https://live.example.test",
                    raw_payload={"id": f"live-{index}"},
                )
                repeated_id = self.repo.add_fixture(
                    {**second, "external_id": f"live-{index}"},
                    source_key="livefootball",
                    source_ref=f"live-{index}",
                    source_url="https://live.example.test",
                    raw_payload={"id": f"live-{index}"},
                )
                self.assertEqual(first_id, second_id)
                self.assertEqual(first_id, repeated_id)
                self.assertEqual(self.repo.get_fixture(first_id)["home_team"], home_a)
                fixture_ids.append(first_id)

                conn = connect(self.db_path)
                try:
                    snapshots = conn.execute(
                        """SELECT source_key,source_ref,source_url,payload_json FROM source_snapshots
                        WHERE fixture_id=? ORDER BY source_key""",
                        (first_id,),
                    ).fetchall()
                    self.assertEqual(len(snapshots), 2)
                    self.assertEqual(
                        {(row["source_key"], row["source_ref"], row["source_url"]) for row in snapshots},
                        {
                            ("api_football", f"api-{index}", "https://api.example.test"),
                            ("livefootball", f"live-{index}", "https://live.example.test"),
                        },
                    )
                    self.assertEqual(
                        {json.loads(row["payload_json"])["id"] for row in snapshots},
                        {f"api-{index}", f"live-{index}"},
                    )
                finally:
                    conn.close()
        self.assertEqual(len(self.repo.list_fixtures(limit=500)), len(pairs))
        self.assertNotEqual(fixture_ids[0], fixture_ids[-1])

    def test_aliases_do_not_merge_across_sources_competitions_or_seasons(self):
        def add(source, competition, home, season="2026"):
            return self.repo.add_fixture(
                {
                    "competition": competition,
                    "kickoff_utc": "2026-10-21T03:00:00Z",
                    "home_team": home,
                    "away_team": "Necaxa",
                    "season": season,
                    "source_key": source,
                },
                source_key=source,
                source_ref=f"{source}:{competition}:{home}:{season}",
                raw_payload={"source": source, "home": home},
            )

        curated = add("api_football", "Liga MX", "Guadalajara Chivas")
        unscoped_source = add("manual", "Liga MX", "Guadalajara")
        unscoped_competition = add("api_football", "Friendly Cup", "Guadalajara")
        other_season = add("livefootball", "Liga MX", "Guadalajara", "2027")
        self.assertEqual(len({curated, unscoped_source, unscoped_competition, other_season}), 4)

    def test_youth_and_reserve_team_names_are_not_collapsed(self):
        senior = self.repo.add_fixture(
            {
                "competition": "Liga MX",
                "kickoff_utc": "2026-10-21T03:00:00Z",
                "home_team": "Guadalajara Chivas",
                "away_team": "Necaxa",
                "season": "2026",
                "source_key": "api_football",
            }
        )
        youth = self.repo.add_fixture(
            {
                "competition": "Liga MX",
                "kickoff_utc": "2026-10-21T03:00:00Z",
                "home_team": "Guadalajara Chivas U20",
                "away_team": "Necaxa U20",
                "season": "2026",
                "source_key": "api_football",
            }
        )
        reserve = self.repo.add_fixture(
            {
                "competition": "Liga MX",
                "kickoff_utc": "2026-10-21T03:00:00Z",
                "home_team": "Guadalajara Chivas Reserves",
                "away_team": "Necaxa Reserves",
                "season": "2026",
                "source_key": "api_football",
            }
        )
        self.assertEqual(len({senior, youth, reserve}), 3)

    def test_missing_season_matches_only_a_unique_candidate(self):
        known_season = self.repo.add_fixture(
            {
                "competition": "Liga MX",
                "kickoff_utc": "2026-10-21T03:00:00Z",
                "home_team": "Guadalajara Chivas",
                "away_team": "Necaxa",
                "season": "2026",
                "source_key": "api_football",
            }
        )
        missing_season = self.repo.add_fixture(
            {
                "competition": "Liga MX",
                "kickoff_utc": "2026-10-21T03:00:00Z",
                "home_team": "Guadalajara",
                "away_team": "Necaxa",
                "source_key": "livefootball",
            }
        )
        self.assertEqual(known_season, missing_season)

    def test_missing_season_does_not_choose_between_multiple_seasons(self):
        def add(source, season):
            return self.repo.add_fixture(
                {
                    "competition": "Liga MX",
                    "kickoff_utc": "2026-10-21T03:00:00Z",
                    "home_team": "Guadalajara Chivas",
                    "away_team": "Necaxa",
                    "season": season,
                    "source_key": source,
                },
                source_key=source,
            )

        first_season = add("api_football", "2026")
        second_season = add("api_football", "2027")
        season_unknown = add("livefootball", None)
        self.assertNotEqual(first_season, second_season)
        self.assertNotIn(season_unknown, {first_season, second_season})

    def test_ambiguous_alias_candidates_are_not_merged(self):
        first = self.repo.add_fixture(
            {
                "competition": "Liga MX",
                "kickoff_utc": "2026-10-21T03:00:00Z",
                "home_team": "Guadalajara Chivas",
                "away_team": "Necaxa",
                "season": "2026",
                "source_key": "manual",
            }
        )
        second = self.repo.add_fixture(
            {
                "competition": "Liga MX",
                "kickoff_utc": "2026-10-21T03:00:00Z",
                "home_team": "Guadalajara",
                "away_team": "Necaxa",
                "season": "2026",
                "source_key": "manual",
            }
        )
        incoming = self.repo.add_fixture(
            {
                "competition": "Liga MX",
                "kickoff_utc": "2026-10-21T03:00:00Z",
                "home_team": "Guadalajara",
                "away_team": "Necaxa",
                "season": "2026",
                "source_key": "api_football",
            }
        )
        repeated_incoming = self.repo.add_fixture(
            {
                "competition": "Liga MX",
                "kickoff_utc": "2026-10-21T03:00:00Z",
                "home_team": "Guadalajara",
                "away_team": "Necaxa",
                "season": "2026",
                "source_key": "api_football",
            }
        )
        self.assertNotEqual(first, second)
        self.assertNotIn(incoming, {first, second})
        self.assertEqual(incoming, repeated_incoming)
        self.assertEqual(len(self.repo.list_fixtures(limit=500)), 3)

    def test_conflicting_result_is_preserved_and_flagged(self):
        fixture = {
            "competition": "Test League",
            "kickoff_utc": "2026-11-21T15:00:00Z",
            "home_team": "Home FC",
            "away_team": "Away FC",
            "status": "finished",
        }
        fixture_id = self.repo.add_fixture(
            {**fixture, "home_score": 2, "away_score": 1},
            source_key="api_football",
            source_ref="api-42",
            source_url="https://api.example.test/match/42",
            raw_payload={"id": 42, "score": [2, 1]},
        )
        self.repo.add_fixture(
            {**fixture, "home_score": 1, "away_score": 3},
            source_key="livefootball",
            source_ref="live-abc",
            source_url="https://live.example.test/match/abc",
            raw_payload={"id": "abc", "score": [1, 3]},
        )
        self.repo.add_fixture(
            {**fixture, "home_score": 1, "away_score": 3},
            source_key="livefootball",
            source_ref="live-abc",
            source_url="https://live.example.test/match/abc",
            raw_payload={"id": "abc", "score": [1, 3]},
        )

        self.assertEqual(self.repo.get_fixture(fixture_id)["home_score"], 2)
        self.assertEqual(self.repo.get_fixture(fixture_id)["away_score"], 1)
        conn = connect(self.db_path)
        try:
            result = conn.execute(
                "SELECT source_key FROM match_results WHERE fixture_id=?", (fixture_id,)
            ).fetchone()
            conflicts = conn.execute(
                """SELECT value_json,source_key,source_ref,source_url,verification_status
                FROM field_observations WHERE fixture_id=? AND field_name='score_conflict'""",
                (fixture_id,),
            ).fetchall()
            self.assertEqual(result["source_key"], "api_football")
            self.assertEqual(len(conflicts), 1)
            self.assertEqual(
                (conflicts[0]["source_key"], conflicts[0]["source_ref"], conflicts[0]["source_url"],
                 conflicts[0]["verification_status"]),
                ("livefootball", "live-abc", "https://live.example.test/match/abc", "conflict"),
            )
            self.assertEqual(
                json.loads(conflicts[0]["value_json"]),
                {
                    "incoming": {"away_score": 3, "home_score": 1},
                    "stored": {"away_score": 1, "home_score": 2},
                },
            )
        finally:
            conn.close()

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
