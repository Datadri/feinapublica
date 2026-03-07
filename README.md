# public-jobs-tracker

MVP per fer seguiment de convocatories publiques d'ocupacio a Catalunya amb pipeline d'ingesta incremental i UI en Streamlit.

## Stack
- Python 3.12
- SQLAlchemy + Alembic
- PostgreSQL (produccio) / SQLite (local)
- Streamlit
- Pydantic
- httpx
- pytest

## Setup local
1. Crear entorn virtual i instal.lar dependencies:
```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e .[dev]
```
2. Configurar variables:
```bash
copy .env.example .env
```
3. Executar migracions:
```bash
alembic upgrade head
```
4. Llançar ingesta completa:
```bash
python scripts/run_ingestion.py
```
5. Obrir UI:
```bash
streamlit run streamlit_app/Home.py
```

## Pipeline
- `scripts/fetch_postings.py`: llegeix API CIDO paginada i desa `job_posting_raw` + `source_job_run`.
- `scripts/normalize_postings.py`: transforma raw a model normalitzat, calcula `hash_content` i crea snapshots.
- `scripts/detect_changes.py`: detecta `NEW`, `UPDATED`, `DEADLINE_CHANGED`, `CLOSED`.
- `scripts/run_ingestion.py`: orquestra tot el flux.

## Disseny de fonts
La capa `public_jobs_tracker.sources` desacobla el connector concret de CIDO de la resta del sistema.
Per afegir una nova font, cal implementar `SourceClient` i registrar-la al `source_registry`.

## Camps i mapatge CIDO
No es codifiquen supostos de negoci fora de `sources/cido/mapping.py`.
Si la documentacio oficial canvia noms de camps, cal ajustar nomes aquesta capa.

## Tests
```bash
pytest
```
Cobertura minima requerida:
- hash_content
- deteccio de canvis
- upsert
- paginacio

## Desplegament minim suggerit
- DB PostgreSQL gestionada (Render/Neon/Supabase)
- Procés programat (GitHub Actions cron o Render Cron Job) que executi `python scripts/run_ingestion.py`
- Streamlit Cloud o contenidor Docker per la UI

## Primera prova rapida (aquesta maquina)
Executa:
```powershell
.\scripts\bootstrap_first_test.ps1
```
Aixo aplicara migracions i executara una ingesta de prova limitada (`CIDO_MAX_PAGES=1`).

Per obrir la UI:
```powershell
.\scripts\run_ui.ps1
```

## UI TypeScript (nova)
S'ha afegit una nova visualitzacio en `web-ts/` amb React + Vite, i una API en FastAPI.

### API backend
```powershell
cd C:\Users\DatAd\codex_projects\ocupacio_publica\public-jobs-tracker
$env:PYTHONPATH=".deps;src"
$env:DATABASE_URL="sqlite:///./public_jobs_tracker.db"
& "C:\Program Files\MySQL\MySQL Shell 8.0\lib\Python3.13\Lib\venv\scripts\nt\python.exe" scripts/run_api.py
```

### Frontend TypeScript
```powershell
cd C:\Users\DatAd\codex_projects\ocupacio_publica\public-jobs-tracker\web-ts
npm install
npm run dev
```

Per defecte la UI consumeix `http://localhost:8000`.

## Deploy Vercel (API + Web)

### 1) Projecte API (Vercel)
- Importa el repo a Vercel i crea projecte `feinapublica-api`.
- Root directory: `/`.
- Variable d'entorn obligatoria:
  - `DATABASE_URL` (PostgreSQL en produccio).
- L'entrypoint es `api/index.py`.

Endpoints util:
- `/`
- `/health`
- `/docs`
- `/api/postings`

### 2) Projecte Web (Vercel)
- Crea segon projecte `feinapublica-web` amb el mateix repo.
- Root directory: `web-ts`.
- Variable d'entorn:
  - `VITE_API_BASE_URL=https://feinapublica.vercel.app`

### 3) Primera carrega de dades (una sola vegada)
Executa localment contra la mateixa `DATABASE_URL` de produccio:
```powershell
cd C:\Users\DatAd\codex_projects\ocupacio_publica\public-jobs-tracker
$env:PYTHONPATH="src"
$env:DATABASE_URL="postgresql+psycopg://USER:PASS@HOST:5432/DB"
& "C:\Program Files\MySQL\MySQL Shell 8.0\lib\Python3.13\Lib\venv\scripts\nt\python.exe" -m alembic upgrade head
$env:CIDO_FILTER_PUBLICATION_FROM="2026-01-01"
$env:CIDO_MAX_PAGES="0"
$env:CIDO_PAGE_LIMIT="100"
& "C:\Program Files\MySQL\MySQL Shell 8.0\lib\Python3.13\Lib\venv\scripts\nt\python.exe" scripts/run_ingestion.py
```

### 4) Ingesta periodica automatica (GitHub Actions)
S'ha afegit workflow `.github/workflows/ingestion-cron.yml`:
- Programat cada 48h.
- Te `workflow_dispatch` manual.

Configura a GitHub:
- Secret: `DATABASE_URL`
- Variables opcionals:
  - `CIDO_FILTER_PUBLICATION_FROM` (default `2026-01-01`)
  - `CIDO_PAGE_LIMIT` (default `100`)
  - `CIDO_MAX_PAGES` (default `0` = sense limit)
