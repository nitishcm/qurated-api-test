from __future__ import annotations

from typing import Any
from typing import Dict

from fastapi import APIRouter
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
from app.utils.utils import gen_user_id
from app.utils.utils import now_iso

router = APIRouter(prefix="/v1/users", tags=["users"])

# Simple in-memory "database"
_db: Dict[str, Dict[str, Any]] = {}


# Endpoints
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "model": BadRequestErrorResponse,
            "description": "Invalid details supplied",
        },
        500: {"model": ErrorResponse, "description": "An unexpected error occurred"},
    },
)
def create_user(req: CreateUserRequest):
    # basic uniqueness on email
    for user in _db.values():
        if user["email"] == req.email:
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
    responses={
        400: {
            "model": BadRequestErrorResponse,
            "description": "The request didn't supply all the necessary data",
        },
        401: {
            "model": ErrorResponse,
            "description": "Access token is missing or invalid",
        },
        403: {
            "model": ErrorResponse,
            "description": "The user is not allowed to access the transaction",
        },
        404: {"model": ErrorResponse, "description": "User was not found"},
        500: {"model": ErrorResponse, "description": "An unexpected error occurred"},
    },
)
def fetch_user_by_id(
    userId: str = Path(..., pattern=r"^usr-[A-Za-z0-9]+$"),
):
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
        400: {
            "model": BadRequestErrorResponse,
            "description": "The request didn't supply all the necessary data",
        },
        401: {
            "model": ErrorResponse,
            "description": "Access token is missing or invalid",
        },
        403: {
            "model": ErrorResponse,
            "description": "The user is not allowed to access the transaction",
        },
        404: {"model": ErrorResponse, "description": "User was not found"},
        500: {"model": ErrorResponse, "description": "An unexpected error occurred"},
    },
)
def update_user_by_id(
    req: UpdateUserRequest,
    userId: str = Path(..., pattern=r"^usr-[A-Za-z0-9]+$"),
):

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
        400: {
            "model": BadRequestErrorResponse,
            "description": "The request didn't supply all the necessary data",
        },
        401: {
            "model": ErrorResponse,
            "description": "Access token is missing or invalid",
        },
        403: {
            "model": ErrorResponse,
            "description": "The user is not allowed to access the transaction",
        },
        404: {"model": ErrorResponse, "description": "User was not found"},
        409: {
            "model": ErrorResponse,
            "description": "A user cannot be deleted when they are associated with a bank account",
        },
        500: {"model": ErrorResponse, "description": "An unexpected error occurred"},
    },
)
def delete_user_by_id(
    userId: str = Path(..., pattern=r"^usr-[A-Za-z0-9]+$"),
):

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
