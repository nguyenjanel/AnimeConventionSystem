from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal

class TicketBase(BaseModel):
    attendee_id: int = Field(..., gt=0, description="ID of the attendee")
    event_id: int = Field(..., gt=0, description="ID of the event")
    seat_number: Optional[str] = Field(None, max_length=10, description="Seat assignment")
    price: Decimal = Field(..., gt=0, description="Ticket price")  # positive decimal
    status: str = Field("reserved", description="Ticket status: reserved, paid, canceled")

class TicketCreate(TicketBase):
    pass  # same as TicketBase

class Ticket(TicketBase):
    ticket_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

from pydantic import BaseModel, Field

class TicketTransactionCreate(BaseModel):
    attendee_id: int = Field(..., example=1)
    event_id: int = Field(..., example=1)
    seat_number: str = Field(..., example="A2")
    price: float = Field(..., example=50.0)

class TicketUpdate(BaseModel):
    attendee_id: Optional[int] = Field(None, gt=0, description="ID of the attendee")
    event_id: Optional[int] = Field(None, gt=0, description="ID of the event")
    seat_number: Optional[str] = Field(None, max_length=10, description="Seat assignment")
    price: Optional[Decimal] = Field(None, gt=0, description="Ticket price")  # positive decimal
    status: Optional[str] = Field(None, description="Ticket status: reserved, paid, canceled")