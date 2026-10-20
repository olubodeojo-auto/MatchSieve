$ErrorActionPreference = 'Stop'
# Places approved CSV/JSON drops in data\inbox. This job makes NO internet/API calls.
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
python run.py sync-inbox
if ($LASTEXITCODE -ne 0) { throw "MatchSieve inbox sync failed with exit code $LASTEXITCODE" }
