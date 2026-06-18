from __future__ import annotations

from typing import List

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str


class BadRequestDetail(BaseModel):
    field: str
    message: str
    type: str


class BadRequestErrorResponse(BaseModel):
    message: str
    details: List[BadRequestDetail]
