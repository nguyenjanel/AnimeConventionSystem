from pydantic import BaseModel, Field
from typing import Optional

class GuestBase(BaseModel):
    name: str = Field(..., min_length=1)
    contact_info: Optional[str] = None

class GuestCreate(GuestBase):
    pass   

class Guest(GuestBase):
    guest_id: int  # primary key