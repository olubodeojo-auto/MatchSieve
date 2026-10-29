# Local LLM analysis for MatchSieve

MatchSieve can optionally use a local language model through [Ollama](https://ollama.com/).
This mode uses the model running on your own computer. It does not require a hosted LLM
API key or a VPS. The existing deterministic pipeline continues to work without Ollama.

## 1. Install and prepare Ollama on Windows

1. Install Ollama from https://ollama.com/download/windows.
2. Open PowerShell and download a model:
   ```powershell
   ollama pull qwen2.5:7b
   ```
3. Confirm the model is available:
   ```powershell
   ollama list
   ```
4. Confirm Ollama responds locally:
   ```powershell
   Invoke-RestMethod http://127.0.0.1:11434/api/tags
   ```

The model download needs internet once. Analysis can then run locally, provided Ollama
is running and the model is installed. Local inference still uses your computer's RAM,
CPU and, if available, GPU. A 7B model is a better starting point on a machine with
adequate memory; on a lower-memory machine, try `qwen2.5:3b` instead. Actual speed
depends on the hardware and context size.

## 2. Run MatchSieve with local LLM analysis

Prepare the usual MatchSieve JSON input containing a `fixture` and `collection.records`,
then run:

```powershell
python scripts/run_agent_pipeline.py data/your-match.json --market RESULT_1X2 --local-llm
```

Choose another supported market as needed:
- `DOUBLE_CHANCE`
- `DRAW_NO_BET`
- `OVER_UNDER_MATCH_GOALS`
- `OVER_UNDER_TEAM_GOALS`

Use a different model or local Ollama URL if required:

```powershell
python scripts/run_agent_pipeline.py data/your-match.json --market RESULT_1X2 --local-llm --ollama-model qwen2.5:3b
```

The script writes the standard deterministic report and a separate `.llm.json` analysis
file. The LLM is not permitted to publish a report or override the deterministic quality
gate. Its evidence claims must cite record IDs from the quality-approved evidence set.
Claims with missing or unknown record IDs are flagged for review.

## 3. What the local LLM does and does not do

The LLM interprets the evidence assembled by MatchSieve. It does not collect fixtures,
open Soccerway pages, fetch missing H2H results, verify source licensing, or calculate
authoritative match statistics by itself. Those jobs belong to the collector, structured
database, and deterministic analytics. A future integration can feed it richer, normalized
form/H2H/standings/odds data once the source adapter reliably extracts those fields.

The model may still misunderstand evidence or produce plausible but wrong analysis.
Citation checks are a safety filter, not proof that a claim is true. Keep human review,
source traceability, and regression tests. Do not use the output as a guarantee of betting
success.

## 4. Tests

Run the local adapter tests and the existing project suite:

```powershell
python -m unittest tests.test_local_llm -v
python -m unittest discover -s tests -v
```

The local LLM tests mock the HTTP response, so they do not require Ollama or a downloaded
model. A separate manual smoke test with Ollama verifies that the installed model responds.
