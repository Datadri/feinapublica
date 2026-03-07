import os

import uvicorn


if __name__ == "__main__":
    os.environ.setdefault("PYTHONPATH", ".deps;src")
    uvicorn.run("public_jobs_tracker.api.app:app", host="0.0.0.0", port=8000, reload=False)