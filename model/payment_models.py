from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional

class PaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)     # must be > 0
    method: str = Field(..., min_length=1) # like credit or cash
    attendee_id: Optional[int] = None
    vendor_id: Optional[int] = None

class PaymentResponse(BaseModel):
    payment_id: int
    amount: Decimal
    method: str
    attendee_id: Optional[int] = None
    vendor_id: Optional[int] = None
