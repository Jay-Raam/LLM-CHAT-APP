from typing import AsyncGenerator
from bson import ObjectId
from datetime import datetime, timezone

from app.repositories.chat_repository import ChatRepository
from app.services.llm_service import LLMService


class ChatService:
    def __init__(self, db):
        self.repo = ChatRepository(db)
        self.llm = LLMService()

    async def list_sessions(self, user_id: ObjectId):
        docs = await self.repo.list_sessions(user_id)
        out = []
        for d in docs:
            out.append({
                "id": str(d.get("_id")),
                "user_id": str(d.get("user_id")),
                "title": d.get("title"),
                "messages": d.get("messages", []),
                "created_at": d.get("created_at"),
                "updated_at": d.get("updated_at"),
            })
        return out

    async def create_session(self, user_id: ObjectId, title: str):
        doc = await self.repo.create_session(user_id, title)
        return {
            "id": str(doc.get("_id")),
            "user_id": str(doc.get("user_id")),
            "title": doc.get("title"),
            "messages": doc.get("messages"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }

    async def get_session(self, session_id: ObjectId, user_id: ObjectId):
        d = await self.repo.get_session(session_id, user_id)
        if not d:
            return None
        return {
            "id": str(d.get("_id")),
            "user_id": str(d.get("user_id")),
            "title": d.get("title"),
            "messages": d.get("messages", []),
            "created_at": d.get("created_at"),
            "updated_at": d.get("updated_at"),
        }

    async def send_message_and_stream(self, session_id: str, user_id: ObjectId, content: str) -> AsyncGenerator[str, None]:
        sess_obj = ObjectId(session_id)
        # Save user message
        user_message = {"role": "user", "content": content, "created_at": datetime.now(timezone.utc)}
        await self.repo.append_message(sess_obj, user_message)

        # Fetch full conversation
        session = await self.repo.get_session(sess_obj, user_id)
        messages = []
        # prepend system prompt
        messages.append({"role": "system", "content": "You are a helpful AI assistant."})
        for m in session.get("messages", []):
            messages.append({"role": m.get("role"), "content": m.get("content")})

        # Stream from LLM and yield SSE-framed text
        buffer = []
        async for chunk in self.llm.stream_chat(messages):
            # format as SSE
            yield f"data: {chunk}\n\n"
            buffer.append(chunk)

        # After streaming completes, append assistant message consolidated
        assistant_text = "".join(buffer).strip()
        if assistant_text:
            assistant_message = {"role": "assistant", "content": assistant_text, "created_at": datetime.now(timezone.utc)}
            await self.repo.append_message(sess_obj, assistant_message)
