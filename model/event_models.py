from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None

class EventCreate(EventBase):
    room_id: int
    start_time: datetime
    end_time: datetime

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    room_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class EventRead(EventBase):
    event_id: int
    room_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
