import asyncio
import json
from contextlib import asynccontextmanager
from typing import List

from aioredis import Redis
from fastapi import APIRouter, Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.websockets import WebSocket, WebSocketDisconnect

from auth import get_current_user
from common.redis_conf import get_redis
from database import get_db
from model.chat import Chat, ChatUser
from model.user import User
from schema.chat import ChatResponse
from schema.user import UserResponse

router = APIRouter(tags=["Chat"])


@asynccontextmanager
async def redis_listener(pubsub, websocket: WebSocket):
    listen_task = asyncio.create_task(listen_to_redis(pubsub, websocket))
    try:
        yield listen_task
    finally:
        listen_task.cancel()
        try:
            await listen_task
        except asyncio.CancelledError:
            print("Redis listener task cancelled successfully.")


async def listen_to_redis(pubsub, websocket: WebSocket):
    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True)
        if message:
            await websocket.send_text(
                message["data"].decode("utf-8")
            )  # 메시지 전송


@router.websocket("/chat/ws")
async def websocket_endpoint(
    room_id: str,
    jwt_token: str,
    websocket: WebSocket,
    redis: Redis = Depends(get_redis),
):
    current_user = await get_current_user(jwt_token)
    await websocket.accept()

    pubsub = redis.pubsub()
    await pubsub.subscribe(room_id)

    async with redis_listener(pubsub, websocket):
        try:
            while True:
                text = await websocket.receive_text()
                msg = {"user": current_user.name, "message": text}
                data = json.dumps(msg, ensure_ascii=False)
                await redis.rpush(room_id, data)  # Redis에 메시지 저장
                await redis.publish(room_id, data)  # Redis에 메시지 발행
        except WebSocketDisconnect:
            pass
        finally:
            await pubsub.unsubscribe(room_id)


@router.get("/chat/history")
async def get_history(
    room_id: str, offset: int = 0, limit: int = 20, redis=Depends(get_redis)
):
    history = await redis.lrange(room_id, offset, offset + limit - 1)
    return {"history": [message for message in history]}


@router.post("/chat", response_model=ChatResponse)
async def create_chat(
    to_user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    async with db.begin():
        chat = Chat()
        db.add(chat)
        await db.flush()

        chat_user1 = ChatUser(chat_id=chat.id, user_id=current_user.id)
        chat_user2 = ChatUser(chat_id=chat.id, user_id=to_user_id)
        db.add_all([chat_user1, chat_user2])

        await db.flush()
        await db.refresh(chat)

        response = ChatResponse(
            id=chat.id,
            users=[UserResponse.model_validate(u) for u in chat.users],
        )
        return response


@router.get("/chat", response_model=List[ChatResponse])
async def get_chat(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Chat).join(Chat.users).where(User.id == current_user.id)
    )
    chats = result.scalars().all()
    response = [
        ChatResponse(
            id=chat.id,
            users=[UserResponse.model_validate(u) for u in chat.users],
        )
        for chat in chats
    ]
    return response


@router.delete("/chat/{chat_id}")
async def delete_chat(
    chat_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(delete(Chat).where(Chat.id == chat_id))
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Chat not found")
