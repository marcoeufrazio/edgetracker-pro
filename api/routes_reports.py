from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from analytics.report_builder import build_report_bundle
from analytics.report_formatter import format_report_summary_markdown
from api.routes_accounts import resolve_statement_path
from api.routes_analysis import serialize_strategy_analyzer, serialize_trade_intelligence
from dashboard.data_loader import DEFAULT_INITIAL_BALANCE


router = APIRouter()


@router.get("/report/{account_id}")
def get_report(
    account_id: str,
    initial_balance: float = DEFAULT_INITIAL_BALANCE,
    cycle_target: float | None = None,
) -> dict[str, object]:
    statement_path = resolve_statement_path(account_id=account_id)
    bundle = build_report_bundle(
        statement_path=statement_path,
        initial_balance=initial_balance,
        cycle_target=cycle_target,
    )
    return {
        "account_id": account_id,
        "statement_path": str(Path(statement_path)),
        "generated_at": bundle.generated_at,
        "metrics_summary": bundle.metrics_summary,
        "health_score": {
            "health_score": bundle.health_score.health_score,
            "health_classification": bundle.health_score.health_classification,
        },
        "health_diagnostic": bundle.health_diagnostic,
        "trade_intelligence": serialize_trade_intelligence(bundle.trade_intelligence),
        "strategy_analyzer": serialize_strategy_analyzer(bundle.strategy_analyzer),
        "report_summary_markdown": format_report_summary_markdown(bundle),
    }
