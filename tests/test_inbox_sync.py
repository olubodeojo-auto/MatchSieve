import tempfile
import unittest
from pathlib import Path
from matchsieve.repository import Repository
from matchsieve.inbox_sync import sync_inbox
from matchsieve.db import connect, table_counts


class InboxSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = Repository(self.root / 'db' / 'matchsieve.sqlite3')
        self.inbox = self.root / 'inbox'
        self.inbox.mkdir()
        self.csv = self.inbox / 'week_fixtures.csv'
        self.csv.write_text(
            'Competition,Date,HomeTeam,AwayTeam\n'
            'Test League,2026-10-25,Home FC,Away FC\n', encoding='utf-8'
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_sync_imports_then_skips_same_file_hash(self):
        first = sync_inbox(self.repo, self.inbox)
        self.assertEqual(first['scanned'], 1)
        self.assertEqual(first['results'][0]['imported'], 1)
        self.assertTrue((self.root / 'db' / 'knowledge-base' / 'INDEX.md').exists())
        counts_before = table_counts(self.repo.db_path)
        second = sync_inbox(self.repo, self.inbox)
        self.assertEqual(second['skipped_unchanged'], 1)
        self.assertEqual(second['results'], [])
        self.assertEqual(table_counts(self.repo.db_path)['fixtures'], counts_before['fixtures'])
        conn = connect(self.repo.db_path)
        try:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM ingested_files').fetchone()[0], 1)
        finally:
            conn.close()

    def test_changed_file_is_imported_again_but_fixture_is_upserted(self):
        sync_inbox(self.repo, self.inbox)
        self.csv.write_text(
            'Competition,Date,HomeTeam,AwayTeam,Venue\n'
            'Test League,2026-10-25,Home FC,Away FC,Ground A\n', encoding='utf-8'
        )
        result = sync_inbox(self.repo, self.inbox)
        self.assertEqual(result['results'][0]['status'], 'imported')
        self.assertEqual(table_counts(self.repo.db_path)['fixtures'], 1)
        self.assertTrue((self.root / 'db' / 'knowledge-base' / 'fixtures-index.md').exists())


if __name__ == '__main__':
    unittest.main()
