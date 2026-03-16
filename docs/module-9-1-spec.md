# Module 9.1 Spec

## Objetivo
Calcular initial risk, realized reward e R-multiple para trades que tenham dados suficientes.

## Inputs
Trades normalizados.

Campos usados:
- type
- open_price
- close_price
- stop_loss
- symbol (opcional)

## Regras de cálculo

### Buy trade
- initial_risk = open_price - stop_loss
- realized_reward = close_price - open_price

### Sell trade
- initial_risk = stop_loss - open_price
- realized_reward = open_price - close_price

### R-multiple
- r_multiple = realized_reward / initial_risk

## Regras gerais
- Se stop_loss estiver vazio, nulo ou igual a 0, não calcular
- Se initial_risk <= 0, não calcular
- Nestes casos devolver r_multiple = None
- Não usar pnl monetário nesta fase
- Trabalhar em distância/preço

## Output por trade
Cada trade enriquecido deve poder ter:
- initial_risk
- realized_reward
- r_multiple

## Output agregado
Calcular também:
- total_trades
- trades_with_r
- trades_without_r
- average_r_multiple
- best_r_multiple
- worst_r_multiple

## Restrições
- reutilizar trades normalizados existentes
- não duplicar lógica
- não criar frontend
- não criar API
- não criar base de dados