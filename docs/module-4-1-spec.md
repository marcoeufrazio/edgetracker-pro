# Module 4.1 Spec

## Objetivo
Adicionar uma série completa de drawdown à timeline da equity curve.

## Input
Timeline/equity curve gerada no Módulo 4.

## Output
Para cada ponto, devolver:
- trade_number
- close_time
- pnl
- cumulative_pnl
- equity
- peak_equity
- drawdown_abs
- drawdown_pct

## Regras
- peak_equity deve ser o maior valor de equity até ao ponto atual
- drawdown_abs = peak_equity - equity
- drawdown_pct = (peak_equity - equity) / peak_equity * 100
- se peak_equity for 0, drawdown_pct deve ser 0
- criar também classificação simples de zona de risco por ponto

## Risk zones
Usar esta regra inicial:
- green: drawdown_pct < 5
- yellow: drawdown_pct >= 5 e < 10
- red: drawdown_pct >= 10

## Restrições
- reutilizar a timeline existente
- não duplicar lógica já existente
- não criar frontend
- não criar API
- não criar base de dados