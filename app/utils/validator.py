from __future__ import annotations


def validate_missing_exists(token: str) -> bool:
    # check if token exists and is not empty
    if token and isinstance(token, str) and token.strip():
        return True
    else:
        return False


def validate_user_edit_token(token: str) -> bool:
    user_edit_token = "4212Hnasin"
    if token.credentials == user_edit_token:
        return True
    else:
        return False


def validate_account_edit_token(token: str) -> bool:
    user_edit_token = "42saf2asin"
    if token.credentials == user_edit_token:
        return True
    else:
        return False
