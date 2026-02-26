from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request

from app.core.security import decode_access_token
from app.db.mongo import get_db
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db_dep():
    return get_db()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
