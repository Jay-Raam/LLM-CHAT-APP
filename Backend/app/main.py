from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.mongo import connect_db, close_db
from app.api.router import api_router

app = FastAPI(title="AI Chatbot API", version="1.0.0")

setup_logging()

import json

# Normalize CORS origins from settings. Allow the env var to be a JSON list or a
# comma-separated string for convenience in development.
origins = settings.CORS_ORIGINS
if isinstance(origins, str):
    try:
        origins = json.loads(origins)
    except Exception:
        origins = [o.strip() for o in origins.split(",") if o.strip()]

if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await connect_db()


@app.on_event("shutdown")
async def shutdown_event():
    await close_db()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
