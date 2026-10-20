# MatchSieve Knowledge Base

The knowledge base is a **searchable archive**, not one huge prompt. The structured source of truth is the SQLite database at `data/matchsieve.sqlite3`; this directory holds human-readable report exports, compact indexes, week digests and reusable templates.

## Folder map

- `INDEX.md` — counts and navigation; refreshed with `python run.py index-kb`.
- `fixtures-index.md` — recent fixture navigation list.
- `weeks/YYYY-Www.md` — generated weekly digest.
- `reports/` — saved Markdown report versions.
- `snapshots/` — optional manual notes/exports. Raw imported payload snapshots live in SQLite with source metadata.
- `templates/` — report dossier and source-capture templates.

## Reusable workflow

1. Place allowed CSV/JSON files in `data/inbox/`.
2. Run `python run.py sync-inbox`. The hash ledger skips unchanged files after successful import.
3. Search fixtures locally and choose a fixture plus explicit market.
4. Generate a report and inspect evidence, sample sizes, missing fields, opposing signals and source timestamps.
5. Export fixture data to CSV when needed: `python run.py export-fixtures`.

A Markdown index is for navigation, not the authoritative raw record. Imported data rights must be checked before inclusion in paid, customer-facing outputs.
