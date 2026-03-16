# Module 12 Spec

## Objetivo
Adicionar filtros e uma tabela de trades ao dashboard Streamlit.

## Inputs
Reutilizar os trades normalizados já existentes.

## Filtros
Permitir filtrar por:
- symbol
- result_type (all / wins / losses)
- day_of_week
- hour_of_day
- date range

## Tabela de trades
Mostrar uma tabela com pelo menos estas colunas:
- ticket
- symbol
- type
- open_time
- close_time
- pnl

Se existirem, incluir também:
- volume
- r_multiple
- duration_minutes

## Regras
- reutilizar pipeline existente
- não duplicar cálculos
- manter compatibilidade com dashboard atual
- filtros devem afetar a tabela mostrada
- os filtros devem ser opcionais
- o dashboard deve continuar a funcionar mesmo sem filtros ativos

## Restrições
- não criar API
- não criar base de dados