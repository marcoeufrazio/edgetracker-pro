# Module 18 Spec

## Objetivo
Adicionar segurança multi-utilizador ao EdgeTracker-Pro.

## Regra principal
Cada utilizador autenticado só pode aceder às suas próprias contas e respetivos dados.

## Regras de ownership

### accounts
Cada account deve estar associada a um user_id.

### acessos protegidos
Os endpoints protegidos devem verificar:
- utilizador autenticado
- ownership da conta pedida

## Endpoints a proteger
- POST /analyze-account
- GET /dashboard/{account_id}
- GET /report/{account_id}
- GET /accounts/comparison

## Comportamento esperado

### se a conta pertence ao utilizador
- acesso permitido

### se a conta não pertence ao utilizador
- devolver erro HTTP apropriado (403 ou 404)

## Regras
- reutilizar auth existente
- reutilizar database existente
- não duplicar lógica
- criar helper de permission/ownership
- manter compatibilidade com API atual

## Restrições
- não alterar analytics
- não alterar dashboard neste módulo
- não criar frontend novo