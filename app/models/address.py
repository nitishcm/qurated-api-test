from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Address(BaseModel):
    line1: str
    line2: Optional[str] = None
    line3: Optional[str] = None
    town: str
    county: str
    postcode: str
