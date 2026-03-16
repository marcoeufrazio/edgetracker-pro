# Module 5.2 Spec

## Objetivo
Calcular métricas de performance de trading a partir dos trades normalizados importados do MT4.

## Input
Trades normalizados do Módulo 2.

## Output
Calcular pelo menos:
- total_trades
- winning_trades
- losing_trades
- breakeven_trades
- win_rate
- gross_profit
- gross_loss
- net_profit
- average_win
- average_loss
- profit_factor
- expectancy
- max_consecutive_wins
- max_consecutive_losses

## Regras
- winning_trades = trades com pnl > 0
- losing_trades = trades com pnl < 0
- breakeven_trades = trades com pnl = 0
- win_rate = winning_trades / total_trades * 100
- gross_profit = soma dos pnl positivos
- gross_loss = soma absoluta dos pnl negativos
- net_profit = soma total dos pnl
- average_win = média dos pnl positivos
- average_loss = média absoluta dos pnl negativos
- profit_factor = gross_profit / gross_loss
- expectancy = net_profit / total_trades

## Streaks
- max_consecutive_wins = maior sequência seguida de pnl > 0
- max_consecutive_losses = maior sequência seguida de pnl < 0

## Restrições
- reutilizar dados normalizados existentes
- não duplicar lógica desnecessária
- não criar frontend
- não criar API
- não criar base de dados