from __future__ import annotations

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field

from .address import Address


class CreateUserRequest(BaseModel):
    name: str
    address: Address
    phoneNumber: str = Field(..., pattern=r"^\+[1-9]\d{1,14}$")
    email: EmailStr
