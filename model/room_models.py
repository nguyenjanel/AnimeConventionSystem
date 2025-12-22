from pydantic import BaseModel, Field
from typing import Optional

# base model for shared validation
class RoomBase(BaseModel):
    name: str = Field(..., min_length=1)
    capacity: int = Field(..., gt=0)  # must be positive
    location: str = Field(..., min_length=1)

# model used when creating a new Room
class RoomCreate(RoomBase):
    pass

#model used when returning Room data (includes room_id)
class Room(RoomBase):
    room_id: int

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None