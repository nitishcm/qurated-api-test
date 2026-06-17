from __future__ import annotations

import secrets
from datetime import datetime


def now_iso() -> str:
    from datetime import timezone

    return datetime.now(tz=timezone.utc).isoformat()


def gen_user_id() -> str:
    return f"usr-{secrets.token_hex(4)}"


def gen_account_number() -> str:
    # 01xxxxxx
    return "01" + secrets.token_hex(3)[:6]


def gen_transaction_id() -> str:
    return f"tan-{secrets.token_hex(4)}"
