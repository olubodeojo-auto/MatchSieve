# Local LLM analysis for MatchSieve

MatchSieve can optionally use a local language model through [Ollama](https://ollama.com/).
The model runs on your own Windows PC. This requires no hosted AI API key and no VPS.
The deterministic MatchSieve pipeline still runs without Ollama.

## 1. One-command Windows setup

From the MatchSieve repository root, open PowerShell and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_local_llm.ps1
```

The script uses the official [Ollama Windows installer](https://ollama.com/download/windows),
checks physical RAM, chooses a Qwen2.5 model size, downloads the model, starts the local
service if needed, tests the local API, and stores the model name in the user environment
variable `MATCHSIEVE_OLLAMA_MODEL`.

- 16 GB RAM or more: `qwen2.5:7b` (about 4.7 GB download).
- 8–15 GB RAM: `qwen2.5:3b` (about 1.9 GB download).
- Under 8 GB RAM: `qwen2.5:1.5b` (basic smoke-test only; too small to trust for serious analysis).

These are approximate model download sizes. You also need extra disk space and memory for
Windows, the context window, and other running applications. Speed depends on CPU/GPU and
available RAM. If you have a low-memory machine, close heavy applications before testing.

**Security note:** the setup script executes Ollama's official installation script from
`https://ollama.com/install.ps1`. It then uses only the local loopback API at
`http://127.0.0.1:11434`. MatchSieve's local adapter rejects non-loopback/cloud URLs.
The first installation and model download require internet; subsequent local inference
does not need a hosted AI service.

## 2. Run the MatchSieve test suite

```powershell
python -m unittest tests.test_local_llm -v
python -m unittest tests.test_local_llm_pipeline -v
python -m unittest discover -s tests -v
```

The local adapter tests mock the HTTP response, so they do not require a downloaded model.
The complete project suite should be green before merging the pull request. GitHub Actions
also runs compile checks and unit tests for pushes and pull requests.

## 3. Run the supplied Atletico-MG vs Cruzeiro example

The example under `examples/atletico_mg_cruzeiro.local.json` was transcribed from a user-pasted
page excerpt. It is not a fresh Soccerway collection, is not independently verified, and
its capture timestamp is synthetic for demonstration. Do not treat the example as current
match advice.

After installing the model, run:

```powershell
python scripts/run_agent_pipeline.py examples/atletico_mg_cruzeiro.local.json --market RESULT_1X2 --local-llm --output data/atletico-cruzeiro-report.json
```

MatchSieve will write:
- `data/atletico-cruzeiro-report.json` — full pipeline output and model analysis.
- `data/atletico-cruzeiro-report.md` — deterministic evidence report.
- `data/atletico-cruzeiro-report.llm.json` — structured local LLM response and validation result.
- `data/atletico-cruzeiro-report.llm.md` — readable local LLM interpretation.

When using an archived sample, the deterministic quality gate may correctly reject the
record as stale. For live research, use freshly collected records with the true capture
timestamp and source URL.

## 4. What the local LLM does and does not do

The local model interprets structured evidence assembled by MatchSieve. It does not
independently collect fixtures, open Soccerway pages, fetch missing H2H results, verify
source licensing, or calculate authoritative statistics. Those jobs belong to the
collector, structured database, and deterministic analytics.

Supporting and counter-evidence points must cite record IDs from the quality-approved
evidence set. Missing or unknown IDs are flagged for review. This checks traceability,
not whether the cited data truly supports the claim. The LLM can still misunderstand or
misstate football evidence; its report is not automatically published and human review
remains mandatory.

This is a research tool, not a guarantee of betting success.
