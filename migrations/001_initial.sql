PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS fixtures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_key TEXT NOT NULL UNIQUE,
    external_id TEXT,
    competition TEXT NOT NULL,
    season TEXT,
    kickoff_utc TEXT NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'scheduled',
    venue TEXT,
    source_primary TEXT NOT NULL DEFAULT 'manual',
    source_ref TEXT,
    is_synthetic INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fixture_kickoff ON fixtures(kickoff_utc);
CREATE INDEX IF NOT EXISTS idx_fixture_competition ON fixtures(competition, kickoff_utc);
CREATE INDEX IF NOT EXISTS idx_fixture_teams ON fixtures(home_team, away_team);

CREATE TABLE IF NOT EXISTS match_results (
    fixture_id INTEGER PRIMARY KEY REFERENCES fixtures(id) ON DELETE CASCADE,
    home_score INTEGER NOT NULL,
    away_score INTEGER NOT NULL,
    halftime_home_score INTEGER,
    halftime_away_score INTEGER,
    result_type TEXT NOT NULL DEFAULT 'full_time',
    captured_at TEXT NOT NULL,
    source_key TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_result_captured ON match_results(captured_at);

CREATE TABLE IF NOT EXISTS source_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER REFERENCES fixtures(id) ON DELETE SET NULL,
    source_key TEXT NOT NULL,
    source_ref TEXT,
    source_url TEXT,
    captured_at TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    quality_label TEXT NOT NULL DEFAULT 'unreviewed',
    UNIQUE(fixture_id, source_key, payload_sha256)
);
CREATE INDEX IF NOT EXISTS idx_snapshot_source ON source_snapshots(source_key, captured_at);

CREATE TABLE IF NOT EXISTS field_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER NOT NULL REFERENCES fixtures(id) ON DELETE CASCADE,
    field_name TEXT NOT NULL,
    value_json TEXT NOT NULL,
    source_key TEXT NOT NULL,
    source_ref TEXT,
    source_url TEXT,
    captured_at TEXT NOT NULL,
    verification_status TEXT NOT NULL DEFAULT 'unverified'
);
CREATE INDEX IF NOT EXISTS idx_observation_fixture_field ON field_observations(fixture_id, field_name, captured_at DESC);

CREATE TABLE IF NOT EXISTS provider_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_key TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    records_received INTEGER NOT NULL DEFAULT 0,
    message TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS research_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER NOT NULL REFERENCES fixtures(id),
    market_code TEXT NOT NULL,
    report_version INTEGER NOT NULL,
    evidence_status TEXT NOT NULL,
    request_json TEXT NOT NULL,
    report_json TEXT NOT NULL,
    markdown TEXT NOT NULL,
    llm_used INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    published_at TEXT,
    UNIQUE(fixture_id, market_code, report_version)
);
CREATE INDEX IF NOT EXISTS idx_report_fixture_market ON research_reports(fixture_id, market_code, created_at DESC);

CREATE TABLE IF NOT EXISTS knowledge_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    doc_type TEXT NOT NULL,
    markdown TEXT NOT NULL,
    tags_json TEXT NOT NULL DEFAULT '[]',
    source_json TEXT NOT NULL DEFAULT '[]',
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(doc_key UNINDEXED, title, markdown, tags);


CREATE TABLE IF NOT EXISTS ingested_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    relative_path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    source_key TEXT NOT NULL,
    file_type TEXT NOT NULL,
    imported_at TEXT NOT NULL,
    imported_records INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    errors_json TEXT NOT NULL DEFAULT '[]',
    UNIQUE(relative_path, sha256)
);
CREATE INDEX IF NOT EXISTS idx_ingested_files_imported ON ingested_files(imported_at DESC);
