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
