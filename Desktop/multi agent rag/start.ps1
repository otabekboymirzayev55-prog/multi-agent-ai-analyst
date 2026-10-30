$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (!(Test-Path -LiteralPath $python)) { throw 'Create .venv and install requirements.txt first.' }
$node = (Get-Command node -ErrorAction Stop).Source
if (!(Test-Path -LiteralPath 'frontend/node_modules/vite/bin/vite.js')) { throw 'Install frontend dependencies first.' }
$logs = Join-Path $PSScriptRoot '.run'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
if (!(Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $python -ArgumentList '-m uvicorn api.main:app --host 127.0.0.1 --port 8001' -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logs 'api.log') -RedirectStandardError (Join-Path $logs 'api-error.log') | Out-Null
}
if (!(Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue)) {
    $previousApi = $env:VITE_API_URL
    try {
        $env:VITE_API_URL = 'http://127.0.0.1:8001'
        Start-Process -FilePath $node -ArgumentList 'node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5173 --strictPort' -WorkingDirectory (Join-Path $PSScriptRoot 'frontend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logs 'ui.log') -RedirectStandardError (Join-Path $logs 'ui-error.log') | Out-Null
    } finally { $env:VITE_API_URL = $previousApi }
}
Write-Output 'Multi-Agent: http://localhost:5173/ ; API: http://127.0.0.1:8001/health (logs: .run)'
