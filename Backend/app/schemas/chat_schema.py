from pydantic import BaseModel
from typing import List, Literal, Optional
from datetime import datetime


class CreateSessionRequest(BaseModel):
    title: str


class MessageRequest(BaseModel):
    session_id: str
    content: str


class MessageResponse(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


class SessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    messages: List[MessageResponse]
    created_at: datetime
    updated_at: datetime
