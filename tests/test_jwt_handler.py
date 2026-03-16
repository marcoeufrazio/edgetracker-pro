from __future__ import annotations

import time

from auth.jwt_handler import create_access_token, decode_access_token


def test_create_and_decode_access_token_round_trip() -> None:
    token = create_access_token("42", "test-secret", additional_claims={"role": "user"})
    payload = decode_access_token(token, "test-secret")

    assert payload["sub"] == "42"
    assert payload["role"] == "user"
    assert payload["exp"] >= payload["iat"]


def test_decode_access_token_rejects_expired_token() -> None:
    token = create_access_token("42", "test-secret", expires_in_seconds=-1)

    try:
        decode_access_token(token, "test-secret")
    except ValueError as exc:
        assert str(exc) == "Token has expired."
    else:
        raise AssertionError("Expected expired token to raise ValueError.")
