from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId


class ChatRepository:
    def __init__(self, db):
        self._col = db.chat_sessions

    async def create_session(self, user_id: ObjectId, title: str) -> dict:
        now = datetime.now(timezone.utc)
        doc = {
            "user_id": user_id,
            "title": title,
            "messages": [],
            "created_at": now,
            "updated_at": now,
        }
        result = await self._col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def list_sessions(self, user_id: ObjectId) -> List[dict]:
        cursor = self._col.find({"user_id": user_id}).sort("updated_at", -1)
        return [s async for s in cursor]

    async def get_session(self, session_id: ObjectId, user_id: ObjectId) -> Optional[dict]:
        return await self._col.find_one({"_id": session_id, "user_id": user_id})

    async def append_message(self, session_id: ObjectId, message: dict):
        await self._col.update_one({"_id": session_id}, {"$push": {"messages": message}, "$set": {"updated_at": datetime.now(timezone.utc)}})
