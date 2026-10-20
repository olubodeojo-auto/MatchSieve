# MatchSieve JSON API Contract — local development v0.2

Base URL for the local web backend: `http://127.0.0.1:8765/`. Android emulator debug base URL: `http://10.0.2.2:8765/`. This is a local development contract, not a public API promise. Responses may evolve; bump and test the contract version if changing fields.

## GET `/api/status` and `/api/health`

Returns `ok`, `product`, `version`, `counts`, `ollama_enabled`, optional `ollama_model`, `markets`, `api_contract`, `production_ready:false`, and a readiness note. It is a diagnostic endpoint and presently does not require authentication because the server is local-only. Before public hosting, make sure it reveals no sensitive internal state and decide if it should be public at all.

## GET `/api/mobile/fixtures?q={query}&limit={1..250}`

Returns a JSON array. Fixture fields: `id`, `competition`, `season`, `kickoff_utc`, `home_team`, `away_team`, `status`, nullable `home_score`, nullable `away_score`, `source_primary`, `source_ref`, `venue`. Fixture `id` belongs to the fixture archive.

## GET `/api/mobile/markets`

Returns `[{"code":"UNDER_4_5","label":"...","question":"...","metric":"..."}, ...]`. The server owns allowed market codes. The mobile client must not invent server-unsupported codes.

## POST `/api/mobile/research`

Request:

```json
{"fixture_id": 123, "market": "UNDER_4_5", "ollama": false}
```

Response fields: `id` and `report_id` (both currently refer to the saved research report ID), `fixture`, `market_code`, `market_label`, `status`, `summary`, `supporting_evidence[]`, `counter_evidence[]`, `missing_data[]`, `source_records[]`, `h2h[]`, nullable `home_form` / `away_form`, `generated_at_utc`, `markdown`, optional `path`, `llm_used`, `method_note`.

Evidence item fields: `label`, `detail`, `direction`, optional `source_name`, optional `captured_at_utc`. Source record fields include `source_key`, `source_ref`, `source_url`, `captured_at` and `quality_label`, depending on supplied data. Unavailable source fields may be null or absent. Never represent missing data as an observed zero.

`status` is an evidence-quality status, currently `READY_FOR_REVIEW` or `LIMITED_EVIDENCE`. It is not a probability, pick verdict or betting instruction.

## GET `/api/mobile/research/history?limit={1..100}`

Returns array of saved report objects, with the same main shape as a report, to build history cards. Opening an item should fetch its detail rather than regenerate it.

## GET `/api/mobile/research/{reportId}`

Returns one report or 404 JSON `{"error":"Research report not found."}`.

## Other local/operator routes

- `GET /api/fixtures`, `GET /api/markets`, `GET /api/research/history`, `GET /api/research/{id}`: browser-compatible versions.
- `GET /api/providers`: provider catalogue and explicitly enabled status.
- `GET /api/kb-search?q=...`: local knowledge-base search.
- `POST /api/fixture`: creates a manual local fixture.
- `POST /api/research`: browser report response shape.
- `POST /api/import-csv`: imports a named CSV already present inside `data/inbox/`.
- `POST /api/provider-fetch`: makes one deliberately requested provider fetch only if provider is enabled.

**Security warning:** those operator routes have no login/authorization in this foundation. Do not expose the server to untrusted networks or the public internet. Production must introduce authentication, authorisation, customer-to-report access rules, rate limiting, audit logs and entitlement enforcement before these routes can be enabled.

## Contract test expectations

Offline tests verify market codes, mobile report identity, report history/detail mapping and fixture identity. Add tests when a field or route changes. Keep a stable synthetic test fixture and test unknown IDs, malformed JSON, provider disabled/failure and report errors.
