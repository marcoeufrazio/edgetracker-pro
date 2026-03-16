from __future__ import annotations

import base64
import hashlib
import hmac
import os
import sqlite3
from dataclasses import dataclass

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from auth.jwt_handler import create_access_token, decode_access_token


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    email: str
    name: str
    created_at: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthUserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthService:
    def __init__(self, connection: sqlite3.Connection, secret_key: str) -> None:
        self.connection = connection
        self.secret_key = secret_key

    def register_user(self, email: str, password: str, name: str | None = None) -> AuthenticatedUser:
        normalized_email = email.strip().lower()
        normalized_name = (name or normalized_email.split("@", 1)[0]).strip()
        if not normalized_email:
            raise ValueError("Email is required.")
        if not password:
            raise ValueError("Password is required.")
        if self._get_user_row_by_email(normalized_email) is not None:
            raise ValueError("User already exists.")

        password_hash = hash_password(password)
        cursor = self.connection.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (normalized_name, normalized_email, password_hash),
        )
        self.connection.commit()
        return self._get_user_by_id(int(cursor.lastrowid))

    def authenticate_user(self, email: str, password: str) -> AuthenticatedUser:
        normalized_email = email.strip().lower()
        row = self._get_user_row_by_email(normalized_email)
        if row is None or not row["password_hash"]:
            raise ValueError("Invalid email or password.")
        if not verify_password(password, str(row["password_hash"])):
            raise ValueError("Invalid email or password.")
        return _row_to_user(row)

    def login_user(self, email: str, password: str) -> str:
        user = self.authenticate_user(email, password)
        return create_access_token(subject=str(user.id), secret_key=self.secret_key)

    def get_current_user(self, token: str) -> AuthenticatedUser:
        payload = decode_access_token(token, self.secret_key)
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.isdigit():
            raise ValueError("Token subject is invalid.")
        return self._get_user_by_id(int(subject))

    def _get_user_by_id(self, user_id: int) -> AuthenticatedUser:
        row = self.connection.execute(
            "SELECT id, email, name, created_at, password_hash FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if row is None:
            raise ValueError("User not found.")
        return _row_to_user(row)

    def _get_user_row_by_email(self, email: str):
        return self.connection.execute(
            "SELECT id, email, name, created_at, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()


def hash_password(password: str, iterations: int = 100_000) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return (
        f"pbkdf2_sha256${iterations}$"
        f"{base64.b64encode(salt).decode('ascii')}$"
        f"{base64.b64encode(digest).decode('ascii')}"
    )


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, digest_text = password_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False

    iterations = int(iterations_text)
    salt = base64.b64decode(salt_text.encode("ascii"))
    expected_digest = base64.b64decode(digest_text.encode("ascii"))
    actual_digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual_digest, expected_digest)


def _row_to_user(row: sqlite3.Row) -> AuthenticatedUser:
    return AuthenticatedUser(
        id=int(row["id"]),
        email=str(row["email"]),
        name=str(row["name"]),
        created_at=str(row["created_at"]),
    )


from auth.dependencies import get_auth_service, get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthUserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthUserResponse:
    try:
        user = auth_service.register_user(payload.email, payload.password, payload.name)
    except ValueError as exc:
        detail = str(exc)
        status_code = status.HTTP_409_CONFLICT if detail == "User already exists." else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=detail) from exc
    return AuthUserResponse(**user.__dict__)


@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        token = auth_service.login_user(payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AuthUserResponse)
def get_me(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthUserResponse:
    return AuthUserResponse(**current_user.__dict__)
