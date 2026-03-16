# Module 5.1 Spec

## Objetivo
Gerar gráficos de equity curve e drawdown curve a partir da timeline e drawdown series já existentes.

## Input
- Timeline do Módulo 4
- Drawdown series do Módulo 4.1

## Output
Guardar dois ficheiros PNG:
- outputs/charts/equity_curve.png
- outputs/charts/drawdown_curve.png

## Regras
- usar matplotlib
- criar um gráfico simples e legível
- eixo X = trade_number
- equity curve: eixo Y = equity
- drawdown curve: eixo Y = drawdown_pct
- reutilizar os módulos já existentes
- criar funções separadas para gerar e guardar gráficos

## Restrições
- não criar frontend
- não criar API
- não criar base de dados