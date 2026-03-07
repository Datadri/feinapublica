$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$python = 'C:\Program Files\MySQL\MySQL Shell 8.0\lib\Python3.13\Lib\venv\scripts\nt\python.exe'
if (-not (Test-Path $python)) {
  throw "Python runtime not found at $python"
}

$env:PYTHONPATH = '.deps;src'
$env:DATABASE_URL = 'sqlite:///./public_jobs_tracker.db'

& $python -m streamlit run streamlit_app/Home.py
