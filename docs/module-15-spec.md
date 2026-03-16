# Module 15 Spec

## Objetivo
Adicionar persistência de dados ao EdgeTracker-Pro usando SQLite.

## Tecnologia
Usar sqlite3 da biblioteca standard do Python.

## Estrutura
Criar persistência para:

- users
- accounts
- trades
- metrics
- reports

## Tabelas mínimas

### users
- id
- email
- created_at

### accounts
- id
- user_id
- account_id
- source_file
- created_at

### trades
- id
- account_id
- ticket
- symbol
- type
- open_time
- close_time
- volume
- pnl
- duration_minutes
- r_multiple

### metrics
- id
- account_id
- win_rate
- profit_factor
- expectancy
- net_profit
- max_drawdown_pct
- ulcer_index
- health_score
- health_classification
- traffic_light
- risk_zone

### reports
- id
- account_id
- report_path
- created_at

## Regras
- reutilizar pipeline existente
- não duplicar lógica analítica
- permitir inserir e ler dados
- criar funções simples no repository
- usar SQLite local nesta fase

## Restrições
- não criar frontend
- não criar API neste módulo
- não criar autenticação ainda