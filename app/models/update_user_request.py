from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr

from .address import Address
from .types import PhoneStr


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    address: Optional[Address] = None
    phoneNumber: Optional[PhoneStr] = None
    email: Optional[EmailStr] = None
