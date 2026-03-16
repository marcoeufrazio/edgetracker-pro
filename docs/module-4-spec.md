# Module 4 Spec

## Objetivo
Reconstruir a curva de equity/capital a partir dos trades importados do MT4.

## Input
Trades normalizados vindos do Módulo 2.

## Output
Uma série temporal ordenada com:
- trade_number
- close_time
- pnl
- cumulative_pnl
- equity

## Regras
- Os trades devem ser ordenados por close_time
- A curva deve ser construída pela soma acumulada dos resultados
- Deve existir opção para usar initial_balance
- O output deve ser reutilizável para métricas e gráficos
- Não criar frontend
- Não criar API
- Não criar base de dados