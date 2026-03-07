$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$python = 'C:\Program Files\MySQL\MySQL Shell 8.0\lib\Python3.13\Lib\venv\scripts\nt\python.exe'
if (-not (Test-Path $python)) {
  throw "Python runtime not found at $python"
}

$env:PYTHONPATH = '.deps;src'
$env:DATABASE_URL = 'sqlite:///./public_jobs_tracker.db'

# Quick first-test guardrail: fetch only one page from CIDO.
if (-not $env:CIDO_MAX_PAGES) { $env:CIDO_MAX_PAGES = '1' }
if (-not $env:CIDO_PAGE_LIMIT) { $env:CIDO_PAGE_LIMIT = '20' }

& $python -c "from alembic.config import Config; from alembic import command; cfg=Config('alembic.ini'); command.upgrade(cfg,'head'); print('alembic_ok')"
& $python scripts/run_ingestion.py

Write-Host 'First test completed. You can open the UI with:'
Write-Host '.\scripts\run_ui.ps1'
