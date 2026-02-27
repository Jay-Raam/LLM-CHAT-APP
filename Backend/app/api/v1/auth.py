from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta

from app.schemas.auth_schema import RegisterRequest, TokenResponse, LoginRequest
from app.services.auth_service import AuthService
from app.utils.deps import get_db_dep

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest, db=Depends(get_db_dep)):
    service = AuthService(db)
    user = await service.register(body.email, body.password)
    if not user:
        raise HTTPException(status_code=400, detail="Email already exists or registration failed")
    token = await service.create_token(str(user.inserted_id))
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db=Depends(get_db_dep)):
    service = AuthService(db)
    token = await service.authenticate_and_get_token(body.email, body.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}
