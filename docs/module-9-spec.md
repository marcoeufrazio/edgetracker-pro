# Module 9 Spec

## Objetivo
Criar um Strategy Analyzer que identifique padrões de performance nos trades.

## Inputs
Timeline de trades já existente.

Campos usados:
- pnl
- close_time
- open_time
- symbol
- volume
- rr (se existir)

## Análises

### Trade Duration
Calcular duração média dos trades e comparar trades curtos vs longos.

Output:
- avg_trade_duration
- best_duration_bucket
- worst_duration_bucket

### R:R Analysis
Se existir campo rr:

Output:
- best_rr_bucket
- worst_rr_bucket

### Trade Size Analysis
Analisar performance por tamanho de posição.

Output:
- best_size_bucket
- worst_size_bucket

### Trade Streak Behaviour
Analisar impacto de sequências de wins/losses.

Output:
- performance_after_win_streak
- performance_after_loss_streak

## Output esperado

{
 "avg_trade_duration": ...,
 "best_duration_bucket": ...,
 "worst_duration_bucket": ...,
 "best_rr_bucket": ...,
 "worst_rr_bucket": ...,
 "best_size_bucket": ...,
 "worst_size_bucket": ...
}

## Regras

- reutilizar timeline existente
- não recalcular equity
- não duplicar lógica
- usar dados já normalizados