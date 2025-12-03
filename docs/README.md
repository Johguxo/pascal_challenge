# 📚 Pascal - Documentación del Proyecto

## Real Estate Conversational Agent

Este documento describe la arquitectura, fases de desarrollo y decisiones técnicas del proyecto.

---

## 📖 Índice

1. [Arquitectura del Sistema](./architecture.md)
2. [Fases de Desarrollo](./phases/README.md)
   - [Fase 1: Conexiones DB + Redis](./phases/phase-1-connections.md)
   - [Fase 2: API REST FastAPI](./phases/phase-2-api.md)
   - [Fase 3: Seed Data](./phases/phase-3-seed.md)
   - [Fase 4: Módulo AI/RAG](./phases/phase-4-ai-rag.md)
   - [Fase 5: Frontend Vanilla](./phases/phase-5-frontend.md)
   - [Fase 6: BFF Telegram](./phases/phase-6-bff-telegram.md)
3. [Decisiones Técnicas](./technical-decisions.md)
4. [Guía de Configuración](./setup-guide.md)

---

## 🎯 Objetivo del Proyecto

Construir un **bot conversacional de IA** para una inmobiliaria que:

- Recibe mensajes en español vía Telegram (y otros canales futuros)
- Clasifica intenciones usando un **Orquestador de Agentes**
- Busca propiedades usando **RAG con PostgreSQL + pgvector**
- Permite agendar visitas
- Mantiene contexto de conversación con **Redis**

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| **Backend** | Python 3.11+ / FastAPI |
| **Base de Datos** | PostgreSQL 16 + pgvector |
| **Cache** | Redis 7 |
| **ORM** | SQLAlchemy 2.0 (async) |
| **AI/LLM** | LangChain + OpenAI |
| **Bot** | python-telegram-bot |
| **Contenedores** | Docker Compose |

---

## 📁 Estructura del Proyecto

```
telegram-agent/
├── docs/                    # Documentación
├── scripts/                 # Scripts de utilidad
├── src/
│   ├── api/                 # FastAPI endpoints
│   ├── services/            # Lógica de negocio
│   │   └── ai/              # Módulo AI (agentes, RAG)
│   ├── database/
│   │   ├── models.py        # Modelos SQLAlchemy
│   │   ├── connection.py    # Conexión DB
│   │   └── repositories/    # Patrón Repository
│   ├── cache/               # Redis cache
│   ├── bff/                 # Backend for Frontend (Telegram, etc.)
│   └── config.py            # Configuración
├── frontend/                # Frontend vanilla (chat UI)
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

## 🚀 Estado Actual

| Fase | Estado | Descripción |
|------|--------|-------------|
| Fase 1 | 🔄 En progreso | Conexiones DB + Redis |
| Fase 2 | ⏳ Pendiente | API REST FastAPI |
| Fase 3 | ⏳ Pendiente | Seed Data |
| Fase 4 | ⏳ Pendiente | Módulo AI/RAG |
| Fase 5 | ⏳ Pendiente | Frontend Vanilla |
| Fase 6 | ⏳ Pendiente | BFF Telegram |

---

## 👤 Autor

Johan Gonzales

---

*Última actualización: Diciembre 2024*

