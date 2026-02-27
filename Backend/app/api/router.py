from fastapi import APIRouter

from app.api.v1 import auth as auth_router
from app.api.v1 import chat as chat_router

api_router = APIRouter()
api_router.include_router(auth_router.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat_router.router, prefix="/chat", tags=["chat"])
