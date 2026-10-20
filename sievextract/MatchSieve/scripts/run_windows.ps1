$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path '.env')) { Copy-Item '.env.example' '.env' }
python run.py init
python run.py serve
