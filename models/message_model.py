from typing import Any
from pydantic import BaseModel, field_serializer, field_validator
from datetime import datetime


class Message(BaseModel):
    sender: str
    text: str
    timestamp: datetime

    @field_serializer('timestamp')
    def serialize_timestamp(self, ts: datetime):
        return ts.strftime("%Y-%m-%d %H:%M:%S")

    @field_validator('timestamp')
    def validate_timestamp(cls, ts: datetime, info: Any):
        timestmp = info.data.get('timestamp', ts.strftime("%Y-%m-%d %H:%M:%S"))
        if ts.strftime("%Y-%m-%d %H:%M:%S") != timestmp:
            raise ValueError("Date does not match")
        return ts
