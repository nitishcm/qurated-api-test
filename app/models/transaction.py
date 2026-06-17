from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import BaseModel


class CreateTransactionRequest(BaseModel):
    amount: float
    currency: str
    type: str
    reference: Optional[str] = None


class TransactionResponse(BaseModel):
    id: str
    amount: float
    currency: str
    type: str
    reference: Optional[str] = None
    userId: Optional[str] = None
    createdTimestamp: str


class ListTransactionsResponse(BaseModel):
    transactions: List[TransactionResponse]
