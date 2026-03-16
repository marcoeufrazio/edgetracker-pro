from __future__ import annotations

from auth.auth_service import AuthService, hash_password, verify_password
from database.db import connect_db, initialize_db


def test_password_hashing_does_not_store_plain_text() -> None:
    password_hash = hash_password("secret123")

    assert password_hash != "secret123"
    assert verify_password("secret123", password_hash)
    assert not verify_password("wrong-password", password_hash)


def test_auth_service_registers_and_authenticates_user(tmp_path) -> None:
    connection = connect_db(tmp_path / "auth.db")
    initialize_db(connection)
    service = AuthService(connection=connection, secret_key="test-secret")

    user = service.register_user("marco@example.com", "secret123", name="Marco")
    authenticated_user = service.authenticate_user("marco@example.com", "secret123")
    stored_row = connection.execute(
        "SELECT email, password_hash FROM users WHERE id = ?",
        (user.id,),
    ).fetchone()

    assert user.email == "marco@example.com"
    assert authenticated_user.id == user.id
    assert stored_row["password_hash"] != "secret123"


def test_auth_service_rejects_invalid_credentials(tmp_path) -> None:
    connection = connect_db(tmp_path / "auth.db")
    initialize_db(connection)
    service = AuthService(connection=connection, secret_key="test-secret")
    service.register_user("marco@example.com", "secret123")

    try:
        service.authenticate_user("marco@example.com", "wrong-password")
    except ValueError as exc:
        assert str(exc) == "Invalid email or password."
    else:
        raise AssertionError("Expected invalid credentials to raise ValueError.")
