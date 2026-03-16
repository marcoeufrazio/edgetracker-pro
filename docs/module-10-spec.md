# Module 10 Spec

## Objetivo
Adicionar Strategy Analyzer e Trade Intelligence ao dashboard Streamlit.

## Inputs
Reutilizar os módulos já existentes:
- trade_intelligence
- strategy_analyzer
- health_score
- performance
- drawdown_series
- charts

## Mostrar no dashboard

### Secção: Trade Intelligence
- best_day
- worst_day
- best_hour
- worst_hour
- best_symbol
- worst_symbol

### Secção: Strategy Analyzer
- average_trade_duration
- best_duration_bucket
- worst_duration_bucket
- best_size_bucket
- worst_size_bucket
- best continuation after win streak
- worst continuation after win streak
- best recovery after loss streak
- worst continuation after loss streak

## Regras
- reutilizar pipeline existente
- não duplicar cálculos
- formatar textos para leitura humana
- manter o dashboard simples e claro

## Restrições
- não criar API
- não criar base de dados