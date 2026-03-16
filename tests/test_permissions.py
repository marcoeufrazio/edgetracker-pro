from __future__ import annotations

from auth.auth_service import AuthenticatedUser
from auth.permissions import ensure_account_ownership, resolve_owned_statement_path
from database.db import connect_db, initialize_db
from database.repository import Repository


def test_ensure_account_ownership_allows_owned_account(tmp_path) -> None:
    connection = connect_db(tmp_path / "permissions.db")
    initialize_db(connection)
    repository = Repository(connection)
    user = repository.create_user("Marco", "marco@example.com")
    repository.create_account(user.id, "24601985", statement_path="data/imports/mt4_statement.htm")

    account = ensure_account_ownership(
        "24601985",
        AuthenticatedUser(id=user.id, email=user.email, name=user.name, created_at=user.created_at or ""),
        repository,
    )

    assert account.account_ref == "24601985"


def test_ensure_account_ownership_rejects_foreign_account(tmp_path) -> None:
    connection = connect_db(tmp_path / "permissions.db")
    initialize_db(connection)
    repository = Repository(connection)
    owner = repository.create_user("Owner", "owner@example.com")
    intruder = repository.create_user("Intruder", "intruder@example.com")
    repository.create_account(owner.id, "24601985", statement_path="data/imports/mt4_statement.htm")

    try:
        ensure_account_ownership(
            "24601985",
            AuthenticatedUser(id=intruder.id, email=intruder.email, name=intruder.name, created_at=intruder.created_at or ""),
            repository,
        )
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 403
    else:
        raise AssertionError("Expected foreign account access to be rejected.")


def test_resolve_owned_statement_path_uses_owned_mapping(tmp_path) -> None:
    connection = connect_db(tmp_path / "permissions.db")
    initialize_db(connection)
    repository = Repository(connection)
    user = repository.create_user("Marco", "marco@example.com")
    repository.create_account(user.id, "24601985", statement_path="data/imports/mt4_statement.htm")

    account, statement_path = resolve_owned_statement_path(
        current_user=AuthenticatedUser(id=user.id, email=user.email, name=user.name, created_at=user.created_at or ""),
        repository=repository,
        account_id="24601985",
    )

    assert account.account_ref == "24601985"
    assert statement_path.name == "mt4_statement.htm"
