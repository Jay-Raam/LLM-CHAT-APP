from pydantic import BaseModel
from typing import List, Literal, Optional
from datetime import datetime


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


class ChatSession(BaseModel):
    id: Optional[str]
    user_id: str
    title: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
