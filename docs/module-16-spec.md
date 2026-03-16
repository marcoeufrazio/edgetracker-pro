# Module 16 — API Layer

## Objetivo

Adicionar uma camada de API ao EdgeTracker-Pro usando **FastAPI**, permitindo aceder às funcionalidades analíticas através de endpoints HTTP.

A API reutiliza diretamente os módulos existentes de analytics e não duplica cálculos.

---

# Arquitetura

A API expõe endpoints que utilizam diretamente o pipeline analítico existente.
