from __future__ import annotations

from typing import Annotated

from pydantic import Field

# Reusable constrained types using Annotated to satisfy static checkers
PhoneStr = Annotated[str, Field(pattern=r"^\+[1-9]\d{1,14}$")]
UserIdStr = Annotated[str, Field(pattern=r"^usr-[A-Za-z0-9]+$")]
