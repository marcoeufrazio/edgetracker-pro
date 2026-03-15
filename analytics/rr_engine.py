from __future__ import annotations

from dataclasses import dataclass

from analytics.trade_schema import NormalizedTrade


@dataclass(frozen=True)
class RMultipleTradeResult:
    ticket: int
    initial_risk: float
    realized_reward: float
    r_multiple: float


def calculate_trade_r_metrics(trade: NormalizedTrade) -> RMultipleTradeResult | None:
    initial_risk = _calculate_initial_risk(trade)
    if initial_risk is None or initial_risk <= 0:
        return None

    realized_reward = _calculate_realized_reward(trade)
    return RMultipleTradeResult(
        ticket=trade.ticket,
        initial_risk=initial_risk,
        realized_reward=realized_reward,
        r_multiple=realized_reward / initial_risk,
    )


def _calculate_initial_risk(trade: NormalizedTrade) -> float | None:
    if trade.stop_loss is None:
        return None

    if trade.side == "buy":
        risk_distance = trade.open_price - trade.stop_loss
    elif trade.side == "sell":
        risk_distance = trade.stop_loss - trade.open_price
    else:
        return None

    if risk_distance <= 0:
        return None

    return risk_distance * trade.size_lots


def _calculate_realized_reward(trade: NormalizedTrade) -> float:
    if trade.side == "buy":
        reward_distance = trade.close_price - trade.open_price
    else:
        reward_distance = trade.open_price - trade.close_price

    return reward_distance * trade.size_lots
