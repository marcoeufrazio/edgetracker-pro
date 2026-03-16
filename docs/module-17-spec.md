# Module 17 Spec

## Objetivo
Adicionar autenticação ao EdgeTracker-Pro com registo, login e proteção básica da API.

## Tecnologia
- FastAPI
- JWT
- password hashing

## Estrutura
Criar pasta:

auth/

Ficheiros:
- auth/__init__.py
- auth/auth_service.py
- auth/jwt_handler.py
- auth/dependencies.py

## Funcionalidades

### Register
Endpoint:
POST /auth/register

Input:
- email
- password

Output:
- user_id
- email
- message

### Login
Endpoint:
POST /auth/login

Input:
- email
- password

Output:
- access_token
- token_type

### Current User
Endpoint:
GET /auth/me

Output:
- user_id
- email

## Regras
- guardar utilizadores na base de dados SQLite existente
- password deve ser guardada hashed, nunca em plain text
- usar JWT para autenticação
- criar helper para obter utilizador atual a partir do token
- preparar a API para proteção futura por utilizador

## Restrições
- não alterar o motor analítico
- não alterar o dashboard neste módulo
- manter compatibilidade com API e database existentes