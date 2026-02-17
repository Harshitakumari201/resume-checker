Backend FastAPI for ATS Resume Checker

Run locally:

1. Create a virtualenv and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. Start the dev server

```bash
uvicorn backend.main:app --reload --port 8000
```

3. The endpoint is `POST /api/process-resume` and accepts `multipart/form-data` with field `file`.

Notes:
- The backend performs a lightweight text extraction and basic heuristics. Replace or augment with an AI service for richer analysis.
- CORS allows `http://localhost:3000` by default to integrate with the Next.js frontend.
