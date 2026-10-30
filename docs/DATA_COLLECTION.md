# Data collection

MatchSieve's collection commands use the existing provider adapters and SQLite
archive. Each provider remains controlled by `MATCHSIEVE_ENABLED_PROVIDERS`;
credentials do not enable a source. No collection command should be treated as
evidence of worldwide or complete historical coverage.

## Commands

```powershell
python -m matchsieve.cli collectors
python -m matchsieve.cli collect --sources football_data_org,sportscore --date-from 2026-10-25 --date-to 2026-10-26 --competition PL
python -m matchsieve.cli collect --sources openligadb --date-from 2026-08-01 --date-to 2026-08-31 --league bl1 --season 2026
python -m matchsieve.cli fetch --provider sportscore --date 2026-10-25 --force-refresh
python -m matchsieve.cli collection-runs
python -m matchsieve.cli provenance --fixture-id 1
python -m matchsieve.cli coverage --date-from 2026-10-25 --date-to 2026-10-31
```

`collect` requires explicit comma-separated sources to prevent accidental
fan-out. Date ranges are limited to 31 days per job. Daily API adapters make a
request per day; Football-Data.org and FootballData.io accept ranges, and
OpenLigaDB fetches the selected league/season then applies date filtering.
Providers are isolated: one failure is reported without stopping later
selected sources. `--cache-ttl` sets the local response-cache lifetime in
seconds (default 900); `--force-refresh` bypasses it. Cache files are not part
of the archive and are stored under the configured database directory's
`cache/provider-fetch` folder.

The saved-HTML path is offline only:

```powershell
python -m matchsieve.cli collect-html permitted-match-page.html --source-url https://example.test/match/123 --competition "Example League"
```

It accepts structured Schema.org `SportsEvent` JSON-LD only. It does not infer
fixtures from visible page text or claim that a particular website supplies
this markup. Original structured event evidence, source IDs, URLs, and hashes
are archived through the existing provenance tables.

## Source status and constraints

The implemented API adapters are API-Football, Football-Data.org,
FootballData.io, LiveFootball, OpenLigaDB, SportMonks, SportScore, and
TheSportsDB. Their presence does not establish current credentials, schema
compatibility, quotas, rights, or live availability. Provider enablement is
opt-in, and live requests were not made as part of this implementation.

Soccerway's terms restrict automated scraping without express permission. The
old Playwright page-capture entry point now refuses live requests; the
structured saved-HTML parser can be used only for data the operator is
permitted to process. Soccerway-specific markup compatibility remains
unverified.

Flashscore's terms restrict personal use and reserve database extraction;
its robots.txt disallows several fixture/live page paths. FotMob's robots.txt
disallows general automated access to `/api/`. Neither service has an adapter
here, and no undocumented endpoints are used. Sofascore and official
competition websites also have no verified adapter; access and reuse rules
must be checked per source. Football-Data.co.uk's published restrictions
exclude commercial use and AI/data-training use, so it is not wired as an
automated source. Local CSV/JSON import remains available subject to the
operator's rights to use the files.

No live source smoke test was performed. Keep source records attributed,
review data-use terms before commercial use, and treat incomplete or
timezone-uncertain records as unverified evidence.

## Manual match-history paste importer

The local research desk includes an operator-only paste intake at **Data setup → Paste
match history**. It accepts copied text supplied manually by the operator; it
does not open, crawl, scrape, or call Flashscore or Soccerway.

Before copying a match page, expand each history panel separately:
- Home team's last matches
- Away team's last matches
- Head-to-head matches

The parser keeps these three sections separate, deduplicates repeated rows
within each section, and records the count found against the 35-record target.
A count below 35 is explicitly marked incomplete or not supplied; it is never
treated as a complete sample. Each recognised result retains its date,
competition (or an explicit Unknown competition value when absent), actual
home/away teams, score, source hash and section/venue context. Parsed history
results are archived as completed fixtures so the existing research queries
can use them. The full section bundle and paste provenance are also attached
to the selected fixture as a source observation.

The importer accepts one-line rows and multiline clipboard blocks. It recognises a date followed by competition, home team, away team and score lines (including repeated team labels in accessibility text). It also accepts one-line rows. For example:

```text
Last matches: Home Team - Home
25.10.2026 | League Name | Club A - Club B | 2-1
Last matches: Away Team - Away
24.10.2026 | Cup Name | Club C - Club D | 0-0
Head-to-head matches
10.05.2026 | League Name | Home Team - Away Team | 1-0
```

Rows without an unambiguous date, team pairing and score are not guessed.
Unrecognised layouts, missing sections, unknown competitions and import
conflicts must be reviewed rather than silently filled. Odds, bookmaker names,
betting links and advertisements are excluded from this QQR dataset.

The 35-record figure is a collection target, not a promise that a source has
35 available matches. The importer only reports what was actually present in
the pasted text. Validate source terms and your right to process copied data
before commercial use.
