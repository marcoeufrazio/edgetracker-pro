# Formulas Reference

## Equity
Equity_t = Equity_(t-1) + PnL_t

## Peak
Peak_t = max(Peak_(t-1), Equity_t)

## Drawdown absoluto
DrawdownAbs_t = Peak_t - Equity_t

## Drawdown percentual
DrawdownPct_t = (Peak_t - Equity_t) / Peak_t * 100

## Ulcer Index
UlcerIndex = sqrt(mean(DrawdownPct_t^2))

## MAR Ratio
MAR = CAGR / MaxDrawdownPct

## Traffic Light
if current_profit < green_target * 0.6 => red
if current_profit < green_target => yellow
else => green