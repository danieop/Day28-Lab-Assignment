param(
    [Parameter(Mandatory = $true)]
    [string]$KaggleUsername,

    [Parameter(Mandatory = $true)]
    [string]$KaggleApiToken
)

$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
$kernelDir = Join-Path $repo "kaggle-lab28"
$metadata = Join-Path $kernelDir "kernel-metadata.json"
$kaggleExe = (Get-Command kaggle.exe -ErrorAction SilentlyContinue).Source

if (-not $kaggleExe) {
    $kaggleExe = Join-Path $env:LOCALAPPDATA "Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Scripts\kaggle.exe"
}

if (-not (Test-Path $kaggleExe)) {
    throw "kaggle.exe not found. Install with: python -m pip install --user kaggle"
}

$json = Get-Content $metadata -Raw | ConvertFrom-Json
$json.id = "$KaggleUsername/lab28-vllm-ngrok-serving"
$json | ConvertTo-Json -Depth 20 | Set-Content $metadata -Encoding UTF8

$env:KAGGLE_API_TOKEN = $KaggleApiToken

& $kaggleExe kernels push -p $kernelDir

Remove-Item Env:\KAGGLE_API_TOKEN -ErrorAction SilentlyContinue
