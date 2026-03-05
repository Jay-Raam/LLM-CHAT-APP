# Nexus AI Chat

Lightweight AI chat application with a FastAPI backend and a React + Vite frontend.

## Summary

- **Project:** Nexus AI Chat
- **Backend:** FastAPI (Python)
- **Frontend:** React + Vite + TypeScript

## Features

- Chat and auth endpoints (API under `/api/v1`)
- MongoDB integration
- Minimal Dockerfile for backend

## Repo layout

- `Backend/` — Python API, DB, services, models
- `frontend/` — React + Vite UI

## Requirements

- Python 3.10+ (or compatible)
- Node.js 18+ and npm/yarn
- MongoDB (URI available via env)

## Backend — Setup & Run

1. Create a virtual environment and activate it:

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r Backend/requirements.txt
```

3. Create a `.env` file in `Backend/` (or set env vars) with values such as:

- `MONGO_URI` — MongoDB connection string
- `SECRET_KEY` — app secret for tokens
- `CORS_ORIGINS` — JSON array or comma-separated list of allowed origins
- any provider keys used by `llm_service.py` (e.g. OpenAI or other LLM keys)

4. Start the API (from project root or `Backend/`):

```bash
# from Backend/
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Health check: GET `http://localhost:8000/health`

API prefix: `/api/v1` (see `Backend/app/api/router.py`)

## Frontend — Setup & Run

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Run in development:

```bash
npm run dev
```

3. Build for production:

```bash
npm run build
npm run preview
```

The frontend config and main entry are in `frontend/src`.

## Docker

- There is a `Backend/Dockerfile` to containerize the API. Build and run by providing environment variables and a MongoDB connection.

## Important files

- `Backend/app/main.py` — application entry; sets up CORS, DB startup/shutdown, routes
- `Backend/app/api/` — API route definitions
- `Backend/app/services/` — auth, chat, and LLM integration logic
- `frontend/` — React client (Vite)

## Development notes

- The backend exposes the API under `/api/v1` and includes a health endpoint at `/health`.
- Configure `CORS_ORIGINS` in env for local development (e.g. `http://localhost:5173`).

## Contributing

- Open an issue or PR describing the change.
- Keep changes small and focused; include tests where relevant.

## License

- Add an appropriate license file to the repository (e.g., MIT) if you intend to open-source.
