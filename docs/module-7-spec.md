# Module 7 Spec

## Objetivo
Criar um Trading Health Score e um diagnóstico textual a partir das métricas já existentes.

## Input
Usar as métricas já calculadas no projeto:
- profit_factor
- expectancy
- max_drawdown_pct
- ulcer_index
- risk_zone
- traffic_light

## Output
Calcular:
- health_score (0 a 100)
- health_classification
- health_diagnostic_text

## Regras do score
Usar uma primeira versão simples baseada em pontos:

### Profit Factor
- >= 1.5 → +25
- >= 1.2 e < 1.5 → +18
- >= 1.0 e < 1.2 → +10
- < 1.0 → +0

### Expectancy
- > 0 → +20
- = 0 → +10
- < 0 → +0

### Max Drawdown %
- < 5 → +20
- >= 5 e < 10 → +12
- >= 10 e < 15 → +5
- >= 15 → +0

### Ulcer Index
- < 3 → +15
- >= 3 e < 6 → +10
- >= 6 e < 10 → +5
- >= 10 → +0

### Risk Zone
- green → +10
- yellow → +5
- red → +0

### Traffic Light
- green → +10
- yellow → +5
- red → +0

## Classificação
- >= 85 → Elite
- >= 70 e < 85 → Boa
- >= 50 e < 70 → Frágil
- < 50 → Crítica

## Diagnóstico
Gerar um texto curto explicando os principais motivos do score.

## Restrições
- reutilizar o pipeline existente
- não duplicar lógica
- não criar frontend
- não criar API
- não criar base de dados