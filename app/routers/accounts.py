from __future__ import annotations

import secrets
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from fastapi import APIRouter
from fastapi import Header
from fastapi import HTTPException
from fastapi import Path
from fastapi import status
from fastapi.responses import Response

from app.models import BadRequestErrorResponse
from app.models import BankAccountResponse
from app.models import CreateBankAccountRequest
from app.models import CreateTransactionRequest
from app.models import ErrorResponse
from app.models import ListBankAccountsResponse
from app.models import ListTransactionsResponse
from app.models import TransactionResponse

router = APIRouter(prefix="/v1/accounts")

# Simple in-memory "database"
_accounts: Dict[str, Dict[str, Any]] = {}
_transactions: Dict[str, List[Dict[str, Any]]] = {}

# Auth helper (same pattern as users router)


def require_bearer(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Access token is missing or invalid"},
        )
    return authorization.split(" ", 1)[1]


def now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def gen_account_number() -> str:
    # 01xxxxxx
    return "01" + secrets.token_hex(3)[:6]


def gen_transaction_id() -> str:
    return f"tan-{secrets.token_hex(4)}"


@router.post(
    "",
    response_model=BankAccountResponse,
    tags=["account"],
    status_code=status.HTTP_201_CREATED,
)
def create_account(
    req: CreateBankAccountRequest,
    token: str = Header(None, alias="Authorization"),
):
    require_bearer(token)
    # create account with unique accountNumber
    account_number = gen_account_number()
    ts = now_iso()
    account = {
        "accountNumber": account_number,
        "sortCode": "10-10-10",
        "name": req.name,
        "accountType": req.accountType,
        "balance": 0.00,
        "currency": "GBP",
        "createdTimestamp": ts,
        "updatedTimestamp": ts,
    }
    _accounts[account_number] = account
    _transactions[account_number] = []
    return account


@router.get("", response_model=ListBankAccountsResponse, tags=["account"])
def list_accounts(token: str = Header(None, alias="Authorization")):
    require_bearer(token)
    return {"accounts": list(_accounts.values())}


@router.get(
    "/{accountNumber}",
    response_model=BankAccountResponse,
    tags=["account"],
    responses={
        400: {"model": BadRequestErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def fetch_account(
    accountNumber: str = Path(..., pattern=r"^01\d{6}$"),
    token: str = Header(None, alias="Authorization"),
):
    require_bearer(token)
    acc = _accounts.get(accountNumber)
    if not acc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Bank account was not found"},
        )
    return acc


@router.patch(
    "/{accountNumber}",
    response_model=BankAccountResponse,
    tags=["account"],
    responses={
        400: {"model": BadRequestErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def update_account(
    req: Dict[str, Any],
    accountNumber: str = Path(..., pattern=r"^01\d{6}$"),
    token: str = Header(None, alias="Authorization"),
):
    require_bearer(token)
    acc = _accounts.get(accountNumber)
    if not acc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Bank account was not found"},
        )
    # allow updating name and accountType
    if "name" in req:
        acc["name"] = req["name"]
    if "accountType" in req:
        acc["accountType"] = req["accountType"]
    acc["updatedTimestamp"] = now_iso()
    return acc


@router.delete(
    "/{accountNumber}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["transactions"],
    responses={
        400: {"model": BadRequestErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def delete_account(
    accountNumber: str = Path(..., pattern=r"^01\d{6}$"),
    token: str = Header(None, alias="Authorization"),
):
    require_bearer(token)
    acc = _accounts.get(accountNumber)
    if not acc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Bank account was not found"},
        )
    # can't delete if transactions exist
    if _transactions.get(accountNumber):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "The request didn't supply all the necessary data"},
        )
    del _accounts[accountNumber]
    del _transactions[accountNumber]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Transactions
@router.post(
    "/{accountNumber}/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["transactions"],
    responses={
        400: {"model": BadRequestErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def create_transaction(
    req: CreateTransactionRequest,
    accountNumber: str = Path(..., pattern=r"^01\d{6}$"),
    token: str = Header(None, alias="Authorization"),
):
    require_bearer(token)
    acc = _accounts.get(accountNumber)
    if not acc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Bank account was not found"},
        )
    # simple balance checks
    if req.type == "withdrawal" and acc["balance"] - req.amount < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Insufficient funds to process transaction"},
        )
    # apply transaction
    tx_id = gen_transaction_id()
    ts = now_iso()
    tx = {
        "id": tx_id,
        "amount": req.amount,
        "currency": req.currency,
        "type": req.type,
        "reference": req.reference,
        "userId": None,
        "createdTimestamp": ts,
    }
    # update balance
    if req.type == "deposit":
        acc["balance"] = round(acc["balance"] + req.amount, 2)
    else:
        acc["balance"] = round(acc["balance"] - req.amount, 2)
    acc["updatedTimestamp"] = ts
    _transactions[accountNumber].append(tx)
    return tx


@router.get(
    "/{accountNumber}/transactions",
    response_model=ListTransactionsResponse,
    tags=["transactions"],
    responses={
        400: {"model": BadRequestErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def list_transactions(
    accountNumber: str = Path(..., pattern=r"^01\d{6}$"),
    token: str = Header(None, alias="Authorization"),
):
    require_bearer(token)
    acc = _accounts.get(accountNumber)
    if not acc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Bank account was not found"},
        )
    return {"transactions": _transactions.get(accountNumber, [])}
