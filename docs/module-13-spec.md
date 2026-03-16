# Module 13 Spec

## Objetivo
Criar exportação de relatórios e ficheiros de dados do EdgeTracker-Pro.

## Outputs mínimos
Gerar:

1. metrics_summary.csv
2. trades_export.csv
3. report_summary.md

Guardar em:
outputs/reports/

## Conteúdo

### metrics_summary.csv
Deve incluir pelo menos:
- total_trades
- winning_trades
- losing_trades
- win_rate
- gross_profit
- gross_loss
- net_profit
- profit_factor
- expectancy
- health_score
- health_classification
- max_drawdown_pct
- ulcer_index

### trades_export.csv
Deve incluir pelo menos:
- ticket
- symbol
- type
- open_time
- close_time
- pnl

Se existirem, incluir também:
- volume
- duration_minutes
- r_multiple

### report_summary.md
Deve incluir:
- resumo das métricas principais
- health score
- health diagnostic
- trade intelligence
- strategy analyzer
- data de geração do relatório

## Regras
- reutilizar pipeline existente
- não duplicar lógica
- não criar PDF nesta fase
- criar ficheiros legíveis e reutilizáveis

## Restrições
- não criar API
- não criar base de dados