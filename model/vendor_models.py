from pydantic import BaseModel, Field
from typing import Optional

class VendorBase(BaseModel):
    name: str = Field(..., min_length=1)
    contact_info: str = Field(..., min_length=1)
    room_id: int

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[str] = None
    room_id: Optional[int] = None

class Vendor(VendorBase):
    vendor_id: int