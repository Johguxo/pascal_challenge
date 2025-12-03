# Pascal Real Estate Conversational Agent

## 📋 Descripción del Proyecto

Bot conversacional de Telegram para una inmobiliaria, construido con Python, FastAPI, LangChain y PostgreSQL con capacidades de RAG (Retrieval-Augmented Generation).

---

## 🎯 Objetivo

Crear un asistente de IA 24/7 que pueda:
- Responder consultas en español sobre propiedades inmobiliarias
- Buscar propiedades usando búsqueda semántica (RAG)
- Agendar visitas a propiedades
- Mantener conversaciones contextuales

---

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                     EXTERNAL LAYER (BFF)                    │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Telegram BFF   │  WhatsApp BFF   │   (futuro: otros)       │
└────────┬────────┴────────┬────────┴─────────────────────────┘
         │                 │
         ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    CORE API (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│  /api/conversations  │  /api/messages  │  /api/properties   │
│  /api/leads          │  /api/search    │  /api/appointments │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVICES LAYER                           │
├─────────────────┬─────────────────┬─────────────────────────┤
│  AI Module      │  Search Service │   Appointment Service   │
│  (Agents, RAG)  │  (Embeddings)   │                         │
└────────┬────────┴────────┬────────┴─────────────────────────┘
         │                 │
         ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                               │
├─────────────────┬─────────────────┬─────────────────────────┤
│   PostgreSQL    │     Redis       │   Repositories          │
│   (pgvector)    │   (Cache)       │   (SQLAlchemy)          │
└─────────────────┴─────────────────┴─────────────────────────┘
```

---

## 🔧 Stack Tecnológico

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| **Backend Framework** | FastAPI | API REST async, alta performance |
| **ORM** | SQLAlchemy 2.0 | Async, type-safe, migrations |
| **Base de Datos** | PostgreSQL + pgvector | Datos + búsqueda vectorial |
| **Cache** | Redis | Estado de conversación + cache de búsquedas |
| **LLM Framework** | LangChain | Orquestación de agentes |
| **LLM Provider** | OpenAI GPT-4o-mini | Modelo de lenguaje |
| **Embeddings** | OpenAI text-embedding-3-small | Vectorización para RAG |
| **Contenedores** | Docker Compose | PostgreSQL + Redis |

---

## 📁 Estructura del Proyecto

```
telegram-agent/
├── docs/                    # 📚 Documentación del proyecto
│   ├── 00-overview.md       # Este archivo
│   ├── 01-database.md       # Fase 1: Conexiones DB + Redis
│   ├── 02-api.md            # Fase 2: API REST FastAPI
│   ├── 03-seed-data.md      # Fase 3: Datos de prueba
│   ├── 04-ai-module.md      # Fase 4: RAG + Agentes
│   ├── 05-frontend.md       # Fase 5: Frontend Vanilla
│   └── 06-telegram-bff.md   # Fase 6: BFF Telegram
├── src/
│   ├── api/                 # Endpoints FastAPI
│   ├── services/            # Lógica de negocio
│   ├── ai/                  # Módulo AI (agentes, RAG)
│   ├── database/            # Modelos y repositorios
│   ├── cache/               # Servicio Redis
│   └── config.py            # Configuración
├── bff/
│   └── telegram/            # BFF para Telegram
├── frontend/                # Frontend vanilla
├── scripts/                 # Scripts de utilidad
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

## 🚀 Fases de Desarrollo

| Fase | Nombre | Estado | Descripción |
|------|--------|--------|-------------|
| 1 | [Database & Redis](./01-database.md) | ✅ Completado | Conexiones, repositorios, cache |
| 2 | [API REST](./02-api.md) | ✅ Completado | Endpoints CRUD FastAPI |
| 3 | [Seed Data](./03-seed-data.md) | ✅ Completado | Datos de prueba |
| 4 | [AI Module](./04-ai-module.md) | ✅ Completado | RAG, embeddings, agentes (Multi-provider) |
| 5 | [Frontend](./05-frontend.md) | ✅ Completado | UI de chat vanilla |
| 6 | [Telegram BFF](./06-telegram-bff.md) | ✅ Completado | Integración Telegram |

---

## 🎨 Patrones de Diseño Utilizados

1. **Repository Pattern** - Abstracción de acceso a datos
2. **Service Layer** - Lógica de negocio separada
3. **BFF (Backend for Frontend)** - Capa de integración externa
4. **Dependency Injection** - FastAPI dependencies
5. **Factory Pattern** - Creación de agentes AI
6. **Strategy Pattern** - Diferentes agentes para diferentes intents

---

## 📊 Modelo de Datos

Ver [01-database.md](./01-database.md) para el esquema completo.

**Entidades principales:**
- `leads` - Usuarios/clientes potenciales
- `conversations` - Sesiones de chat
- `messages` - Mensajes individuales
- `projects` - Proyectos inmobiliarios
- `properties` - Propiedades específicas
- `typologies` - Tipos de propiedades (2BR, 3BR, etc.)
- `appointments` - Citas agendadas

