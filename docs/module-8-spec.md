# Module 8 Spec

## Objetivo
Criar um módulo de Trade Intelligence que analisa padrões no histórico de trades.

## Inputs
Trade timeline já existente.

Campos usados:
- close_time
- symbol (se existir)
- pnl

## Análises

### Day of Week
Calcular performance por dia da semana.

Output:
- best_day
- worst_day

### Hour of Day
Calcular performance por hora.

Output:
- best_hour
- worst_hour

### Symbol Performance
Se existir campo symbol:

Output:
- best_symbol
- worst_symbol

### Win Rate by Day

Output:
- winrate_by_day

## Output
Estrutura final:

{
 "best_day": "...",
 "worst_day": "...",
 "best_hour": "...",
 "worst_hour": "...",
 "best_symbol": "...",
 "worst_symbol": "...",
 "winrate_by_day": {...}
}

## Regras
- reutilizar timeline existente
- não recalcular equity
- não duplicar lógica