from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import BaseModel


class CreateBankAccountRequest(BaseModel):
    name: str
    accountType: str


class UpdateBankAccountRequest(BaseModel):
    name: Optional[str] = None
    accountType: Optional[str] = None


class BankAccountResponse(BaseModel):
    accountNumber: str
    sortCode: str
    name: str
    accountType: str
    balance: float
    currency: str
    createdTimestamp: str
    updatedTimestamp: str


class ListBankAccountsResponse(BaseModel):
    accounts: List[BankAccountResponse]
