from typing import Optional, Any
from datetime import datetime, timezone
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
# Use `Any` for DB/result types to avoid editor/type-stub issues when stubs aren't installed


class UserRepository:
    def __init__(self, db: Any):
        self._col = db.users

    async def create(self, email: str, hashed_password: str) -> Optional[Any]:
        doc: dict[str, str | datetime] = {"email": email, "hashed_password": hashed_password, "created_at": datetime.now(timezone.utc)}
        try:
            result = await self._col.insert_one(doc)
            return result
        except DuplicateKeyError:
            # Email already exists
            return None

    async def find_by_email(self, email: str) -> Optional[dict[str, Any]]:
        return await self._col.find_one({"email": email})

    async def find_by_id(self, id: ObjectId) -> Optional[dict[str, Any]]:
        return await self._col.find_one({"_id": id})
