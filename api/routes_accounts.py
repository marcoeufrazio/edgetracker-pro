from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from analytics.account_comparison import build_account_comparison
from analytics.importers import resolve_mt4_statement_path
from analytics.multi_account import _extract_account_id, analyze_multiple_accounts
from auth.auth_service import AuthenticatedUser
from auth.dependencies import get_current_user, get_optional_current_user
from auth.permissions import get_repository
from database.repository import Repository
from dashboard.data_loader import DEFAULT_INITIAL_BALANCE


router = APIRouter()

STATEMENTS_DIR = Path("data/imports")
UPLOADS_DIR = STATEMENTS_DIR / "uploads"
SUPPORTED_STATEMENT_SUFFIXES = {".html", ".htm"}


@router.post("/upload-statement")
async def upload_statement(
    file: UploadFile = File(...),
    current_user: AuthenticatedUser | None = Depends(get_optional_current_user),
    repository: Repository = Depends(get_repository),
) -> dict[str, object]:
    filename = Path(file.filename or "statement.html").name
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_STATEMENT_SUFFIXES:
        raise HTTPException(status_code=400, detail="Only MT4 HTML statement files are supported.")

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    target_path = UPLOADS_DIR / filename
    target_path.write_bytes(await file.read())
    account_id = _extract_account_id(target_path)

    if current_user is not None:
        repository.save_account(
            user_id=current_user.id,
            account_ref=account_id,
            statement_path=str(target_path),
        )

    return {
        "filename": target_path.name,
        "statement_path": str(target_path),
        "account_id": account_id,
    }


@router.get("/accounts/comparison")
def get_accounts_comparison(
    initial_balance: float = DEFAULT_INITIAL_BALANCE,
    cycle_target: float | None = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    repository: Repository = Depends(get_repository),
) -> dict[str, object]:
    statement_paths = [
        str(resolve_mt4_statement_path(account.statement_path))
        for account in repository.list_accounts(current_user.id)
        if account.statement_path
    ]
    analyses = analyze_multiple_accounts(
        statement_paths=statement_paths,
        initial_balance=initial_balance,
        cycle_target=cycle_target,
    )
    comparison = build_account_comparison(analyses)
    return {
        "comparison_table": comparison.comparison_table,
        "aggregated_metrics": comparison.aggregated_metrics,
        "performance_ranking": comparison.performance_ranking,
    }


def list_available_statement_paths() -> list[Path]:
    if not STATEMENTS_DIR.exists():
        return []

    discovered_paths = {
        path
        for suffix in SUPPORTED_STATEMENT_SUFFIXES
        for path in STATEMENTS_DIR.rglob(f"*{suffix}")
        if path.is_file()
    }
    return sorted(discovered_paths)


def resolve_statement_path(*, account_id: str | None = None, statement_path: str | Path | None = None) -> Path:
    if statement_path is not None:
        return resolve_mt4_statement_path(statement_path)

    if not account_id:
        raise HTTPException(status_code=400, detail="Either statement_path or account_id is required.")

    statement_index = build_statement_index()
    resolved_path = statement_index.get(account_id)
    if resolved_path is None:
        raise HTTPException(status_code=404, detail=f"Account '{account_id}' was not found.")
    return resolved_path


def build_statement_index() -> dict[str, Path]:
    statement_index: dict[str, Path] = {}
    for path in list_available_statement_paths():
        statement_index.setdefault(_extract_account_id(path), path)
    return statement_index
