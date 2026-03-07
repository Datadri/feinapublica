@echo off
cd /d C:\Users\DatAd\codex_projects\ocupacio_publica\public-jobs-tracker\web-ts
set VITE_API_BASE_URL=http://localhost:8000
start "web-ts-public-jobs" cmd /c "npm.cmd run dev -- --host 0.0.0.0 --port 5173 >> web-ts.log 2>&1"
