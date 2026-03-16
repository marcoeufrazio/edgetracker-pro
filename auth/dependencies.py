from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.auth_service import AuthService, AuthenticatedUser
from database.db import DEFAULT_DATABASE_NAME, connect_db, initialize_db


DEFAULT_AUTH_SECRET = os.getenv("EDGETRACKER_AUTH_SECRET", "edgetracker-dev-secret")
bearer_scheme = HTTPBearer(auto_error=False)


def get_database_path(request: Request) -> Path:
    value = getattr(request.app.state, "database_path", Path("data") / DEFAULT_DATABASE_NAME)
    return Path(value)


def get_auth_secret(request: Request) -> str:
    return str(getattr(request.app.state, "auth_secret", DEFAULT_AUTH_SECRET))


def get_db_connection(database_path: Path = Depends(get_database_path)):
    connection = connect_db(database_path)
    initialize_db(connection)
    try:
        yield connection
    finally:
        connection.close()


def get_auth_service(
    connection: sqlite3.Connection = Depends(get_db_connection),
    secret_key: str = Depends(get_auth_secret),
) -> AuthService:
    return AuthService(connection=connection, secret_key=secret_key)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
        )

    try:
        return auth_service.get_current_user(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthenticatedUser | None:
    if credentials is None:
        return None

    try:
        return auth_service.get_current_user(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
