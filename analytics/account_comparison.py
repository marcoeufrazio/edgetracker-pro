from __future__ import annotations

from dataclasses import dataclass

from analytics.multi_account import AccountAnalysis


@dataclass(frozen=True)
class AccountComparison:
    comparison_table: list[dict[str, object]]
    aggregated_metrics: dict[str, object]
    performance_ranking: list[dict[str, object]]


def build_account_comparison(accounts: list[AccountAnalysis]) -> AccountComparison:
    comparison_table = [_build_account_row(account) for account in accounts]
    aggregated_metrics = _build_aggregated_metrics(accounts)
    performance_ranking = _build_performance_ranking(accounts)

    return AccountComparison(
        comparison_table=comparison_table,
        aggregated_metrics=aggregated_metrics,
        performance_ranking=performance_ranking,
    )


def _build_account_row(account: AccountAnalysis) -> dict[str, object]:
    performance = account.dashboard_data.performance
    metrics = account.dashboard_data.account_metrics
    return {
        "account_id": account.account_id,
        "total_trades": performance.total_trades,
        "win_rate": round(performance.win_rate, 2),
        "profit_factor": round(performance.profit_factor, 4),
        "net_profit": round(performance.net_profit, 2),
        "max_drawdown_pct": round(metrics.max_drawdown_pct, 2),
        "traffic_light": metrics.traffic_light,
        "risk_zone": account.dashboard_data.current_risk_zone,
        "health_score": account.health_score,
        "health_classification": account.health_classification,
    }


def _build_aggregated_metrics(accounts: list[AccountAnalysis]) -> dict[str, object]:
    total_accounts = len(accounts)
    total_trades = sum(account.dashboard_data.performance.total_trades for account in accounts)
    combined_net_profit = sum(account.dashboard_data.performance.net_profit for account in accounts)
    average_win_rate = (
        sum(account.dashboard_data.performance.win_rate for account in accounts) / total_accounts
        if total_accounts
        else 0.0
    )
    average_profit_factor = (
        sum(account.dashboard_data.performance.profit_factor for account in accounts) / total_accounts
        if total_accounts
        else 0.0
    )
    ranking = _build_performance_ranking(accounts)

    return {
        "total_accounts": total_accounts,
        "total_trades": total_trades,
        "combined_net_profit": round(combined_net_profit, 2),
        "average_win_rate": round(average_win_rate, 2),
        "average_profit_factor": round(average_profit_factor, 4),
        "best_account": ranking[0]["account_id"] if ranking else None,
        "worst_account": ranking[-1]["account_id"] if ranking else None,
    }


def _build_performance_ranking(accounts: list[AccountAnalysis]) -> list[dict[str, object]]:
    ranked_accounts = sorted(
        accounts,
        key=lambda account: (
            account.health_score,
            account.dashboard_data.performance.net_profit,
            account.dashboard_data.performance.profit_factor,
        ),
        reverse=True,
    )

    return [
        {
            "rank": index,
            "account_id": account.account_id,
            "health_score": account.health_score,
            "net_profit": round(account.dashboard_data.performance.net_profit, 2),
            "profit_factor": round(account.dashboard_data.performance.profit_factor, 4),
        }
        for index, account in enumerate(ranked_accounts, start=1)
    ]
