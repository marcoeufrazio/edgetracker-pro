from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time


DEFAULT_EXPIRATION_SECONDS = 3600


def create_access_token(
    subject: str,
    secret_key: str,
    expires_in_seconds: int = DEFAULT_EXPIRATION_SECONDS,
    additional_claims: dict[str, object] | None = None,
) -> str:
    now = int(time.time())
    payload: dict[str, object] = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_in_seconds,
    }
    if additional_claims:
        payload.update(additional_claims)

    header = {"alg": "HS256", "typ": "JWT"}
    encoded_header = _encode_segment(header)
    encoded_payload = _encode_segment(payload)
    signature = _sign(f"{encoded_header}.{encoded_payload}", secret_key)
    return f"{encoded_header}.{encoded_payload}.{signature}"


def decode_access_token(token: str, secret_key: str) -> dict[str, object]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token format.")

    encoded_header, encoded_payload, encoded_signature = parts
    signing_input = f"{encoded_header}.{encoded_payload}"
    expected_signature = _sign(signing_input, secret_key)
    if not hmac.compare_digest(encoded_signature, expected_signature):
        raise ValueError("Invalid token signature.")

    header = _decode_segment(encoded_header)
    if header.get("alg") != "HS256":
        raise ValueError("Unsupported token algorithm.")

    payload = _decode_segment(encoded_payload)
    exp = payload.get("exp")
    if not isinstance(exp, int):
        raise ValueError("Token is missing an expiration timestamp.")
    if exp < int(time.time()):
        raise ValueError("Token has expired.")
    return payload


def _encode_segment(value: dict[str, object]) -> str:
    raw = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return _urlsafe_b64encode(raw)


def _decode_segment(value: str) -> dict[str, object]:
    raw = _urlsafe_b64decode(value)
    return json.loads(raw.decode("utf-8"))


def _sign(value: str, secret_key: str) -> str:
    digest = hmac.new(secret_key.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).digest()
    return _urlsafe_b64encode(digest)


def _urlsafe_b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _urlsafe_b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")
