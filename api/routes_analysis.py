from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel, Field, model_validator

from api.routes_accounts import resolve_statement_path
from dashboard.data_loader import DEFAULT_INITIAL_BALANCE, DashboardData, load_dashboard_data


router = APIRouter()


class AnalyzeAccountRequest(BaseModel):
    statement_path: str | None = None
    account_id: str | None = None
    initial_balance: float = Field(default=DEFAULT_INITIAL_BALANCE, gt=0)
    cycle_target: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_source(self) -> "AnalyzeAccountRequest":
        if self.statement_path is None and self.account_id is None:
            raise ValueError("Either statement_path or account_id is required.")
        return self


@router.post("/analyze-account")
def analyze_account(request: AnalyzeAccountRequest) -> dict[str, object]:
    statement_path = resolve_statement_path(
        account_id=request.account_id,
        statement_path=request.statement_path,
    )
    dashboard_data = load_dashboard_data(
        statement_path=statement_path,
        initial_balance=request.initial_balance,
        cycle_target=request.cycle_target,
    )
    return serialize_dashboard_payload(
        account_id=request.account_id or Path(statement_path).stem,
        statement_path=statement_path,
        dashboard_data=dashboard_data,
    )


@router.get("/dashboard/{account_id}")
def get_dashboard(
    account_id: str,
    initial_balance: float = DEFAULT_INITIAL_BALANCE,
    cycle_target: float | None = None,
) -> dict[str, object]:
    statement_path = resolve_statement_path(account_id=account_id)
    dashboard_data = load_dashboard_data(
        statement_path=statement_path,
        initial_balance=initial_balance,
        cycle_target=cycle_target,
    )
    return serialize_dashboard_payload(
        account_id=account_id,
        statement_path=statement_path,
        dashboard_data=dashboard_data,
    )


def serialize_dashboard_payload(
    *,
    account_id: str,
    statement_path: str | Path,
    dashboard_data: DashboardData,
) -> dict[str, object]:
    return {
        "account_id": account_id,
        "statement_path": str(statement_path),
        "performance": asdict(dashboard_data.performance),
        "streaks": asdict(dashboard_data.streaks),
        "trade_intelligence": serialize_trade_intelligence(dashboard_data.trade_intelligence),
        "strategy_analyzer": serialize_strategy_analyzer(dashboard_data.strategy_analyzer),
        "account_metrics": asdict(dashboard_data.account_metrics),
        "current_risk_zone": dashboard_data.current_risk_zone,
        "current_drawdown_pct": dashboard_data.current_drawdown_pct,
        "equity_timeline": [
            {
                "trade_number": point.trade_number,
                "close_time": point.close_time.isoformat(sep=" "),
                "pnl": point.pnl,
                "cumulative_pnl": point.cumulative_pnl,
                "equity": point.equity,
            }
            for point in dashboard_data.equity_timeline
        ],
        "drawdown_series": [
            {
                "trade_number": point.trade_number,
                "close_time": point.close_time.isoformat(sep=" "),
                "pnl": point.pnl,
                "cumulative_pnl": point.cumulative_pnl,
                "equity": point.equity,
                "peak_equity": point.peak_equity,
                "drawdown_abs": point.drawdown_abs,
                "drawdown_pct": point.drawdown_pct,
                "risk_zone": point.risk_zone,
            }
            for point in dashboard_data.drawdown_series
        ],
    }


def serialize_trade_intelligence(trade_intelligence: object) -> dict[str, object]:
    return asdict(trade_intelligence)


def serialize_strategy_analyzer(strategy_analyzer: object) -> dict[str, object]:
    return asdict(strategy_analyzer)
