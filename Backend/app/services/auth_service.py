from datetime import timedelta
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token


class AuthService:
    def __init__(self, db):
        self.repo = UserRepository(db)

    async def register(self, email: str, password: str):
        hashed = hash_password(password)
        return await self.repo.create(email, hashed)

    async def create_token(self, user_id: str) -> str:
        return create_access_token(subject=user_id, expires_delta=timedelta(minutes=60))

    async def authenticate_and_get_token(self, email: str, password: str):
        user = await self.repo.find_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.get("hashed_password")):
            return None
        return create_access_token(subject=str(user.get("_id")))
