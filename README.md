# Nexus AI ✦ FastAPI Python & React Streaming Platform

[![CI](https://github.com/Jay-Raam/LLM-CHAT-APP/actions/workflows/ci.yml/badge.svg)](https://github.com/Jay-Raam/LLM-CHAT-APP/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

High-performance, asynchronous AI conversational platform featuring an asynchronous **FastAPI (Python)** backend, **Motor (async MongoDB)** persistence, Dockerized container runtime, and a reactive **Vite + React** interface.

---

## 🌟 Key Architecture Highlights

- **Asynchronous FastAPI Engine**: Async route handlers and SSE / streaming response generation powered by `uvicorn` and `httpx`.
- **Async MongoDB Persistence**: Non-blocking database operations with `motor` and strict data validation using `pydantic v2`.
- **JWT & Password Security**: Token-based authentication using `python-jose` with bcrypt cryptographic password hashing via `passlib`.
- **Containerized Deployment**: Minimal, production-hardened `Dockerfile` for single-command container orchestration.
- **Automated CI Validation**: Multi-stage GitHub Actions workflow validating Python code syntax and React Vite production bundles.

---

## 🏗️ Repository Structure

```
LLM-CHAT-APP/
├── Backend/                 # Python FastAPI Asynchronous Service
│   ├── app/
│   │   ├── api/             # API routers (auth, chat, completions)
│   │   ├── core/            # Configuration, CORS, JWT secrets
│   │   ├── models/          # Pydantic v2 validation schemas
│   │   ├── services/        # Asynchronous LLM client & MongoDB handlers
│   │   └── main.py          # Application entrypoint & lifespan hooks
│   ├── Dockerfile           # Optimized Python container image
│   └── requirements.txt     # Pinned Python package dependencies
│
├── frontend/                # React 18 + Vite User Interface
│   ├── src/                 # Chat components, state hooks, styling
│   └── package.json
│
└── .github/workflows/ci.yml # GitHub Actions automated CI verification
```

---

## 🚀 Quickstart & Setup

### 1. Backend (Python FastAPI)

```bash
cd Backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- API Base URL: `http://localhost:8000/api/v1`
- Swagger UI Documentation: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`

### 2. Frontend (React + Vite)

```bash
cd ../frontend
npm install
npm run dev
```

The frontend client launches at `http://localhost:5173`.

### 3. Docker Deployment

```bash
cd Backend
docker build -t nexus-ai-fastapi .
docker run -p 8000:8000 --env-file .env nexus-ai-fastapi
```

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).
