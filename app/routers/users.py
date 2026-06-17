from __future__ import annotations

import secrets
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

from fastapi import APIRouter
from fastapi import Header
from fastapi import HTTPException
from fastapi import Path
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.responses import Response

from app.models import BadRequestErrorResponse
from app.models import CreateUserRequest
from app.models import ErrorResponse
from app.models import UpdateUserRequest
from app.models import UserResponse

router = APIRouter(prefix="/v1/users", tags=["users"])

# Simple in-memory "database"
_db: Dict[str, Dict[str, Any]] = {}


# Simple auth dependency: endpoints that require bearer token call this
def require_bearer(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Access token is missing or invalid"},
        )
    # token accepted; in a real router validate token here
    return authorization.split(" ", 1)[1]


def now_iso() -> str:
    from datetime import timezone

    return datetime.now(tz=timezone.utc).isoformat()


def gen_user_id() -> str:
    return f"usr-{secrets.token_hex(4)}"


# Endpoints


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(req: CreateUserRequest):
    # basic uniqueness on email
    for u in _db.values():
        if u["email"] == req.email:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Invalid details supplied",
                    "details": [
                        {
                            "field": "email",
                            "message": "email already exists",
                            "type": "unique",
                        },
                    ],
                },
            )
    user_id = gen_user_id()
    ts = now_iso()
    stored = {
        "id": user_id,
        "name": req.name,
        "address": req.address.model_dump(),
        "phoneNumber": req.phoneNumber,
        "email": req.email,
        "createdTimestamp": ts,
        "updatedTimestamp": ts,
        # internal: associated accounts list (empty)
        "accounts": [],
    }
    _db[user_id] = stored
    return stored


@router.get(
    "/{userId}",
    response_model=UserResponse,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def fetch_user_by_id(
    userId: str = Path(..., pattern=r"^usr-[A-Za-z0-9]+$"),
    token: str = Header(None, alias="Authorization"),
):
    require_bearer(token)
    user = _db.get(userId)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "User was not found"},
        )
    return user


@router.patch(
    "/{userId}",
    response_model=UserResponse,
    responses={
        400: {"model": BadRequestErrorResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def update_user_by_id(
    req: UpdateUserRequest,
    userId: str = Path(..., pattern=r"^usr-[A-Za-z0-9]+$"),
    token: str = Header(None, alias="Authorization"),
):
    require_bearer(token)
    user = _db.get(userId)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "User was not found"},
        )
    # routerly updates
    if req.name is not None:
        user["name"] = req.name
    if req.address is not None:
        user["address"] = req.address.model_dump()
    if req.phoneNumber is not None:
        user["phoneNumber"] = req.phoneNumber
    if req.email is not None:
        # ensure email uniqueness
        for uid, u in _db.items():
            if uid != userId and u["email"] == req.email:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "message": "Invalid details supplied",
                        "details": [
                            {
                                "field": "email",
                                "message": "email already exists",
                                "type": "unique",
                            },
                        ],
                    },
                )
        user["email"] = req.email
    user["updatedTimestamp"] = now_iso()
    return user


@router.delete(
    "/{userId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def delete_user_by_id(
    userId: str = Path(..., pattern=r"^usr-[A-Za-z0-9]+$"),
    token: str = Header(None, alias="Authorization"),
):
    require_bearer(token)
    user = _db.get(userId)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "User was not found"},
        )
    # simulate constraint: cannot delete if associated accounts exist
    if user.get("accounts"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "A user cannot be deleted when they are associated with a bank account",
            },
        )
    del _db[userId]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
