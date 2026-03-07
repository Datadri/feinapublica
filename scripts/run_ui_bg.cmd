@echo off
cd /d C:\Users\DatAd\codex_projects\ocupacio_publica\public-jobs-tracker
set PYTHONPATH=.deps;src
set DATABASE_URL=sqlite:///./public_jobs_tracker.db
start "streamlit-public-jobs" cmd /c ""C:\Program Files\MySQL\MySQL Shell 8.0\lib\Python3.13\Lib\venv\scripts\nt\python.exe" -m streamlit run streamlit_app/Home.py --global.developmentMode=false --server.headless=true --server.port=8501 >> streamlit.log 2>&1"
