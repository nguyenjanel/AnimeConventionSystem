from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class AttendeeBase(BaseModel):
    name: str
    email: EmailStr


class AttendeeCreate(AttendeeBase):
    # No extra fields for now the table only has name, email, registration_date
    pass


class AttendeeUpdate(BaseModel):
    # Allow updating name or email
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class AttendeeResponse(AttendeeBase):
    attendee_id: int
    registration_date: datetime


class MoveRegistrationRequest(BaseModel):
    old_ticket_id: int = Field(..., example=1)
    new_event_id: int = Field(..., example=4)
    new_seat_number: str = Field(..., example="B5")
    new_price: float = Field(..., example=60.0)

