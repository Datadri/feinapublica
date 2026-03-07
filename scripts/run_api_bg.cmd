@echo off
cd /d C:\Users\DatAd\codex_projects\ocupacio_publica\public-jobs-tracker
set PYTHONPATH=.deps;src
set DATABASE_URL=sqlite:///./public_jobs_tracker.db
start "api-public-jobs" cmd /c ""C:\Program Files\MySQL\MySQL Shell 8.0\lib\Python3.13\Lib\venv\scripts\nt\python.exe" scripts\run_api.py >> api.log 2>&1"
