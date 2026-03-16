from __future__ import annotations

from pathlib import Path

from fastapi import Depends, HTTPException, status

from analytics.importers import resolve_mt4_statement_path
from analytics.multi_account import _extract_account_id
from auth.auth_service import AuthenticatedUser
from auth.dependencies import get_current_user, get_db_connection
from database.models import AccountRecord
from database.repository import Repository


def get_repository(connection=Depends(get_db_connection)) -> Repository:
    return Repository(connection)


def ensure_account_ownership(
    account_id: str,
    current_user: AuthenticatedUser,
    repository: Repository,
) -> AccountRecord:
    try:
        return repository.get_account_for_user(current_user.id, account_id)
    except ValueError:
        if repository.account_exists_for_ref(account_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this account.",
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account '{account_id}' was not found.",
        )


def resolve_owned_statement_path(
    *,
    current_user: AuthenticatedUser,
    repository: Repository,
    account_id: str | None = None,
    statement_path: str | Path | None = None,
) -> tuple[AccountRecord, Path]:
    if statement_path is not None:
        resolved_input = resolve_mt4_statement_path(statement_path)
        extracted_account_id = _extract_account_id(resolved_input)
        account = ensure_account_ownership(extracted_account_id, current_user, repository)
        if account.statement_path:
            return account, resolve_mt4_statement_path(account.statement_path)
        return account, resolved_input

    if account_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either statement_path or account_id is required.",
        )

    account = ensure_account_ownership(account_id, current_user, repository)
    if not account.statement_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Statement path is not configured for account '{account_id}'.",
        )
    return account, resolve_mt4_statement_path(account.statement_path)


def list_owned_statement_paths(
    current_user: AuthenticatedUser = Depends(get_current_user),
    repository: Repository = Depends(get_repository),
) -> list[Path]:
    statement_paths: list[Path] = []
    for account in repository.list_accounts(current_user.id):
        if not account.statement_path:
            continue
        statement_paths.append(resolve_mt4_statement_path(account.statement_path))
    return statement_paths
