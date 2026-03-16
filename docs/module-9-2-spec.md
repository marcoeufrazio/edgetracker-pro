# Module 9.2 Spec

## Objetivo
Calcular R-multiple sintético baseado no average loss.

## Cálculo

average_loss = média das perdas absolutas

Para cada trade:

R = pnl / average_loss

## Exemplo

average_loss = -5

trade pnl = +10
R = 10 / 5 = 2R

trade pnl = -5
R = -1R

## Output

- average_r
- best_r
- worst_r
- distribution_r

## Regras

- ignorar trades com pnl = 0
- usar valor absoluto de average_loss
- não recalcular equity