# MatchSieve Legacy Pipeline Audit

Audit date: 2026-10-20

This is a source review of the legacy engine path in the root repository. Changes are committed to `main`; the suite still needs to be run in the local VS Code environment.

## Defects corrected

1. **Fixture state leakage:** `PipelineRunner` now creates a fresh `DataFusion` instance per fixture, preventing one fixture's provider payload, identity, or score from carrying into the next.
2. **Engine dependency order:** the master engine now calculates NBS before Trap, Trap before Value, and NBS before Evidence. Recommendation and final decision run after their inputs.
3. **Form parsing:** W/D/L markers are converted to 3/1/0 points. Unknown markers are ignored instead of causing `sum()` to fail. Form strength now reflects points earned, not merely the number of entries.
4. **Fabricated quality metrics:** feature defaults for data quality, provider agreement and feature quality are zero until measured. Provider agreement remains unknown (zero) because cross-provider field comparisons are not implemented.
5. **False signals from missing data:** Goal Probability, Under and BTTS engines now gate key signals on explicitly available metrics. A missing metric is not automatically treated as a measured zero. With no usable match evidence, both recommendation layers return `WAIT`; goal score is marked as a heuristic signal score, not a calibrated probability.
6. **Incomplete provider payloads:** the FootballData.io adapter tolerates absent optional xG, odds, probabilities and venue data. A malformed fixture no longer aborts the entire fixture batch.
7. **Feature mapping:** fixture metadata is copied into the feature object, and the risk extractor maps recognized numeric fields from the normalized statistics dictionary before measuring coverage.

## Tests added

- `tests/test_pipeline_runner_isolation.py`
- `tests/test_legacy_feature_audit.py`
- `tests/test_master_engine_order.py`
- `tests/test_legacy_provider_adapter.py`

These tests have been added to the repository but **have not yet been executed in the user's VS Code environment**. Treat them as pending verification until the local test command passes.

## Known limitations still open

- The legacy path does not yet reliably ingest recent team form, historical goal averages, H2H rates, injuries, line-ups, or all live match statistics from its provider adapter. Missing inputs will correctly lead to limited evidence or `WAIT`, but useful coverage is still incomplete.
- Provider agreement is not calculated by comparing overlapping fields from multiple sources. It must not be interpreted as a score of 100%.
- Data quality is a simple completeness indicator, not a validation of accuracy, freshness, source permissions, or provider reliability.
- The goal, BTTS, Under, Trap, Explosion, Value and final decision scores are heuristics, not statistically calibrated probabilities or proven betting edges.
- The league profile contains hand-written league-name heuristics; it is not driven by a measured, season-specific league database.
- The legacy adapter's expected FootballData.io payload shape still needs validation against an approved current sample.
- The newer local-first `matchsieve/` archive/reporting foundation is separate from this legacy engine path. These changes do not merge the two architectures or imply production readiness.

## Local verification after pulling

From the repository root in PowerShell:

```powershell
python -m compileall -q engines extractors models services core tests
python -m unittest discover -s tests -v
```

Run the tests before using legacy recommendations. A passing test suite verifies code behaviour covered by tests; it does not establish prediction accuracy.
