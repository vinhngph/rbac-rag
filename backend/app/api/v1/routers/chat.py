from fastapi import APIRouter
from fastapi.sse import EventSourceResponse
from typing import List
from uuid import UUID

from app.models.chat_session import ChatSessionCreate, ChatSessionRead
from app.models.chat_message import ChatMessageCreate, ChatMessageRead

from app.api.dependencies.current_user import CurrentUser
from app.api.dependencies.db_session import DB_Session

from app.services.chat import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/sessions", response_model=ChatSessionRead)
async def create_chat_session(
    chat_session_create: ChatSessionCreate, current_user: CurrentUser, db: DB_Session
):
    chat_service = ChatService(db)
    return await chat_service.create_chat_session(chat_session_create, current_user)


@router.get("/sessions", response_model=List[ChatSessionRead])
async def read_chat_sessions(current_user: CurrentUser, db: DB_Session):
    chat_service = ChatService(db)
    return await chat_service.read_chat_sessions(current_user)


@router.post(
    "/sessions/{session_id}/messages",
    response_class=EventSourceResponse,
    response_model=ChatMessageRead,
)
async def create_chat_message_and_stream(
    session_id: UUID,
    chat_message_create: ChatMessageCreate,
    current_user: CurrentUser,
    db: DB_Session,
):
    chat_service = ChatService(db)

    async for chunk in chat_service.stream_chat_response(
        session_id, chat_message_create, current_user
    ):
        yield chunk


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageRead])
async def read_chat_messages(
    session_id: UUID, current_user: CurrentUser, db: DB_Session
):
    chat_service = ChatService(db)
    return await chat_service.read_chat_messages(session_id, current_user)
