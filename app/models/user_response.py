from __future__ import annotations

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field

from .address import Address


class UserResponse(BaseModel):
    id: str = Field(..., pattern=r"^usr-[A-Za-z0-9]+$")
    name: str
    address: Address
    phoneNumber: str = Field(..., pattern=r"^\+[1-9]\d{1,14}$")
    email: EmailStr
    createdTimestamp: str
    updatedTimestamp: str
