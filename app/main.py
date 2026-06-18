from __future__ import annotations

from fastapi import FastAPI

from app.routers import accounts
from app.routers import users

app = FastAPI(title="Eagle Bank API")


# include routers
app.include_router(users.router)
app.include_router(accounts.router)
