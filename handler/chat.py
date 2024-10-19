import asyncio
import json
from typing import List

from aiokafka import AIOKafkaProducer
from aioredis import Redis
from fastapi import Depends, APIRouter
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.websockets import WebSocket, WebSocketDisconnect

from auth import get_current_user
from common.redis_conf import get_redis
from database import get_db
from handler.chat_kafka import get_kafka_producer, get_kafka_consumer
from model.chat import Chat, ChatUser
from model.user import User
from schema.chat import ChatResponse
from schema.user import UserResponse

router = APIRouter(tags=["Chat"])


async def get_chat_history(redis: Redis, room_id: str, offset: int = 0, limit: int = 20):
    history = await redis.lrange(room_id, offset, offset + limit - 1)
    return history


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

    async def listen_to_redis():
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                await websocket.send_text(message['data'])

    listen_task = asyncio.create_task(listen_to_redis())
    try:
        while True:
            msg = await websocket.receive_text()
            data = json.dumps({
                "user": current_user.name,
                "message": msg,
            }, ensure_ascii=False)

            await redis.rpush(room_id, data)
            await redis.publish(room_id, data)
    except WebSocketDisconnect:
        try:
            await redis.publish(f"room:{room_id}", json.dumps({
                "user": current_user.name,
                "message": "has disconnected."
            }))
        except WebSocketDisconnect:
            pass
    finally:
        listen_task.cancel()
        try:
            await listen_task
        except asyncio.CancelledError:
            print("Redis listener task cancelled successfully.")


# @router.websocket("/chat/ws/kafka")
async def websocket_endpoint(
        room_id: str,
        jwt_token: str,
        websocket: WebSocket,
        kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer),
):
    current_user = await get_current_user(jwt_token)
    await websocket.accept()

    # Kafka 컨슈머 생성 및 시작
    kafka_consumer = await get_kafka_consumer(room_id)

    async def listen_to_kafka():
        async for message in kafka_consumer:
            # Kafka에서 수신한 메시지를 WebSocket 클라이언트로 전송
            msg_data = message.value.decode('utf-8')
            await websocket.send_text(msg_data)

    # Kafka 메시지 구독을 위한 비동기 Task 생성
    listen_task = asyncio.create_task(listen_to_kafka())

    try:
        # WebSocket 메시지 처리 루프
        while True:
            msg = await websocket.receive_text()
            data = json.dumps({
                "user": current_user.name,
                "message": msg,
            }, ensure_ascii=False)

            # Kafka에 메시지를 발행 (Produce)
            await kafka_producer.send_and_wait(room_id, data.encode('utf-8'))

    except WebSocketDisconnect:
        try:
            # 연결 해제 메시지를 Kafka에 발행
            disconnect_msg = json.dumps({
                "user": current_user.name,
                "message": "has disconnected."
            }, ensure_ascii=False)
            await kafka_producer.send_and_wait(room_id, disconnect_msg.encode('utf-8'))
        except WebSocketDisconnect:
            pass
    finally:
        # Kafka 컨슈머와 프로듀서 정리
        listen_task.cancel()
        try:
            await listen_task
        except asyncio.CancelledError:
            print("Kafka listener task cancelled successfully.")
        await kafka_consumer.stop()
        await kafka_producer.stop()


@router.get("/chat/history")
async def get_history(
        room_id: str,
        offset: int = 0,
        limit: int = 20,
        redis=Depends(get_redis)
):
    history = await get_chat_history(redis, room_id, offset, limit)
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
        select(Chat)
        .join(Chat.users)
        .where(User.id == current_user.id)
    )
    chats = result.scalars().all()
    response = [
        ChatResponse(
            id=chat.id,
            users=[UserResponse.model_validate(u) for u in chat.users],
        ) for chat in chats
    ]
    return response


@router.delete("/chat/{chat_id}")
async def delete_chat(
        chat_id: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        delete(Chat).where(Chat.id == chat_id)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Chat not found")
