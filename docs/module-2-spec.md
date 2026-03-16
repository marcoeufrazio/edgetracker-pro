# Module 2 Spec

## Objetivo
Ler um ficheiro HTML exportado do MT4 e converter os trades para um formato padrão.

## Input inicial
- HTML de statement/export do MT4

## Output padrão
Cada trade deve ficar com estes campos:
- ticket
- open_time
- close_time
- symbol
- type
- volume
- open_price
- close_price
- stop_loss
- take_profit
- commission
- swap
- pnl

## Regras
- O módulo deve ler HTML do MT4
- O módulo deve encontrar a tabela de trades
- O módulo deve ignorar linhas de resumo e totais
- O módulo deve validar os campos essenciais
- O módulo deve normalizar os dados para um formato único
- Não criar frontend
- Não criar API
- Não criar base de dados# Module 2 Spec

## Objetivo
Ler um ficheiro HTML exportado do MT4 e converter os trades para um formato padrão.

## Input inicial
- HTML de statement/export do MT4

## Output padrão
Cada trade deve ficar com estes campos:
- ticket
- open_time
- close_time
- symbol
- type
- volume
- open_price
- close_price
- stop_loss
- take_profit
- commission
- swap
- pnl

## Regras
- O módulo deve ler HTML do MT4
- O módulo deve encontrar a tabela de trades
- O módulo deve ignorar linhas de resumo e totais
- O módulo deve validar os campos essenciais
- O módulo deve normalizar os dados para um formato único
- Não criar frontend
- Não criar API
- Não criar base de dados