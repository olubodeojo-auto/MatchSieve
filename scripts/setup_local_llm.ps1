# MatchSieve local LLM setup for Windows PowerShell
# Installs Ollama from its official installer, selects a model based on physical RAM,
# starts the local service if needed, downloads the model, and verifies the local API.
$ErrorActionPreference = "Stop"

$Computer = Get-CimInstance Win32_ComputerSystem
$RamGb = [math]::Round($Computer.TotalPhysicalMemory / 1GB, 1)

if ($RamGb -ge 16) {
    $Model = "qwen2.5:7b"
} elseif ($RamGb -ge 8) {
    $Model = "qwen2.5:3b"
} else {
    $Model = "qwen2.5:1.5b"
    Write-Warning "This PC has less than 8 GB RAM. The selected 1.5B model is a basic smoke-test model and may be too weak for dependable football analysis."
}

Write-Host ""
Write-Host "MatchSieve local LLM setup" -ForegroundColor Cyan
Write-Host ("Detected physical RAM: {0} GB" -f $RamGb)
Write-Host ("Selected local model:  {0}" -f $Model)
Write-Host "No hosted AI API key or VPS is required."
Write-Host ""

$Ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $Ollama) {
    Write-Host "Installing Ollama using its official Windows install script..."
    Invoke-RestMethod "https://ollama.com/install.ps1" | Invoke-Expression

    # Refresh this process PATH because installers may update the user's PATH only
    # for new terminal sessions.
    $PossiblePaths = @(
        (Join-Path $env:LOCALAPPDATA "Programs\Ollama"),
        (Join-Path $env:LOCALAPPDATA "Ollama")
    )
    foreach ($PathCandidate in $PossiblePaths) {
        if ((Test-Path $PathCandidate) -and ($env:Path -notlike "*$PathCandidate*")) {
            $env:Path = "$PathCandidate;$env:Path"
        }
    }
    $Ollama = Get-Command ollama -ErrorAction SilentlyContinue
}

if (-not $Ollama) {
    throw "Ollama was not found in this PowerShell session. Close and reopen PowerShell, then run this script again."
}

$OllamaPath = $Ollama.Source
$ApiUrl = "http://127.0.0.1:11434"
$ApiReady = $false

try {
    Invoke-RestMethod "$ApiUrl/api/tags" -TimeoutSec 3 | Out-Null
    $ApiReady = $true
} catch {
    Write-Host "Starting Ollama's local service..."
    Start-Process -FilePath $OllamaPath -ArgumentList "serve" -WindowStyle Hidden
}

for ($Attempt = 0; $Attempt -lt 20 -and -not $ApiReady; $Attempt++) {
    Start-Sleep -Seconds 2
    try {
        Invoke-RestMethod "$ApiUrl/api/tags" -TimeoutSec 3 | Out-Null
        $ApiReady = $true
    } catch {
        # Continue polling the local service.
    }
}
if (-not $ApiReady) {
    throw "Ollama did not respond at $ApiUrl. Open Ollama from the Start menu and run this script again."
}

Write-Host ("Downloading {0}; this may use several GB of internet data..." -f $Model) -ForegroundColor Yellow
& $OllamaPath pull $Model
if ($LASTEXITCODE -ne 0) {
    throw "Model download failed. Check your internet connection and available disk space, then rerun this script."
}

# Store the choice for MatchSieve's CLI in future terminals, and this process now.
$env:MATCHSIEVE_OLLAMA_MODEL = $Model
[Environment]::SetEnvironmentVariable("MATCHSIEVE_OLLAMA_MODEL", $Model, "User")

$Body = @{
    model = $Model
    stream = $false
    messages = @(
        @{ role = "user"; content = "Reply with exactly: MatchSieve local model ready" }
    )
} | ConvertTo-Json -Depth 6

$Reply = Invoke-RestMethod -Method Post -Uri "$ApiUrl/api/chat" -ContentType "application/json" -Body $Body -TimeoutSec 180
if (-not $Reply.message.content) {
    throw "The local model API responded but returned no message content."
}

Write-Host ""
Write-Host "Local LLM is installed and responding." -ForegroundColor Green
Write-Host ("Model: {0}" -f $Model)
Write-Host ("Ollama API: {0}" -f $ApiUrl)
Write-Host ("Model response: {0}" -f $Reply.message.content.Trim())
Write-Host ""
Write-Host "Next: from the MatchSieve repository root, run:"
Write-Host "  python -m unittest tests.test_local_llm -v"
Write-Host "  python -m unittest discover -s tests -v"
Write-Host "The Python tests are still to be run against your local checkout."
