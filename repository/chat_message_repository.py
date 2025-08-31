import json
from uuid import uuid4
from typing import Optional
from config.redis_client import redis_client  # type: ignore
from models.message_model import Message


def create_chat_room() -> str:
    room_id = str(uuid4())
    redis_client.sadd("chat:rooms", room_id)
    return room_id


def add_message(room_id: str, message: Message):
    redis_client.rpush(f"chat:{room_id}:messages", message.model_dump_json())


def get_chat_history(room_id: str) -> Optional[list[Message]]:
    messages: list[str] = redis_client.lrange(
        f"chat:{room_id}:messages", 0, -1)
    return [Message.model_validate(json.loads(m)) for m in messages] if len(messages) > 0 else None
