from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from bson import ObjectId

from app.schemas.chat_schema import (
    CreateSessionRequest,
    SessionResponse,
    MessageRequest,
)
from app.services.chat_service import ChatService
from app.utils.deps import get_db_dep, get_current_user

router = APIRouter()


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(user_id: ObjectId = Depends(get_current_user), db=Depends(get_db_dep)):
    svc = ChatService(db)
    sessions = await svc.list_sessions(user_id)
    return sessions


@router.post("/session", response_model=SessionResponse, status_code=201)
async def create_session(body: CreateSessionRequest, user_id: ObjectId = Depends(get_current_user), db=Depends(get_db_dep)):
    svc = ChatService(db)
    session = await svc.create_session(user_id, body.title)
    return session


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, user_id: ObjectId = Depends(get_current_user), db=Depends(get_db_dep)):
    svc = ChatService(db)
    session = await svc.get_session(ObjectId(session_id), user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/message")
async def post_message(body: MessageRequest, user_id: ObjectId = Depends(get_current_user), db=Depends(get_db_dep)):
    svc = ChatService(db)

    async def event_stream():
        async for chunk in svc.send_message_and_stream(body.session_id, user_id, body.content):
            yield chunk

    return StreamingResponse(event_stream(), media_type="text/event-stream")
