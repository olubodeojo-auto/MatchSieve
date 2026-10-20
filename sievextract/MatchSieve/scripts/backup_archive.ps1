$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
python run.py export-archive
if ($LASTEXITCODE -ne 0) { throw "Archive export failed with exit code $LASTEXITCODE" }
Write-Host 'Archive exported to data/exports as JSONL. Store the export in a separate backup location.'
