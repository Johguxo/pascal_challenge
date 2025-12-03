# Fase 1: Database & Redis Connections

## 📋 Objetivo

Establecer todas las conexiones necesarias a PostgreSQL y Redis, completar los repositorios para todas las entidades, y verificar que todo funcione correctamente.

---

## ✅ Checklist

### 1.1 Infraestructura Docker
- [x] Docker Compose con PostgreSQL (pgvector)
- [x] Docker Compose con Redis
- [x] Volúmenes persistentes
- [x] Health checks

### 1.2 Conexión PostgreSQL
- [x] Engine async (asyncpg)
- [x] Engine sync (para scripts)
- [x] Session factory
- [x] Context manager para sesiones

### 1.3 Modelos SQLAlchemy
- [x] Lead
- [x] Conversation
- [x] Message
- [x] Project
- [x] Property
- [x] Typology
- [x] Appointment
- [x] Vector columns para RAG (Project, Property)

### 1.4 Repositorios (CRUD)
- [x] LeadRepository
- [x] ConversationRepository
- [x] MessageRepository
- [x] ProjectRepository
- [x] PropertyRepository
- [x] TypologyRepository
- [x] AppointmentRepository
- [x] BaseRepository (clase base con operaciones CRUD comunes)

### 1.5 Conexión Redis
- [x] Cliente Redis async
- [x] Servicio de cache para conversaciones (ConversationCache)
- [x] Servicio de cache para búsquedas (SearchCache)

### 1.6 Script de inicialización
- [x] Creación de extensión pgvector
- [x] Creación de enum message_type
- [x] Creación de tablas (via SQLAlchemy)

---

## 📊 Esquema de Base de Datos

### Diagrama ER

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│   leads     │──1:N──│  conversations   │──1:N──│  messages   │
└─────────────┘       └──────────────────┘       └─────────────┘
      │                       │
      │                       │
      │               ┌───────┴───────┐
      │               ▼               │
      │         ┌──────────┐          │
      └────────▶│appointments│◀────────┘
                └──────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ projects │─│properties│─│typologies│
    └──────────┘ └──────────┘ └──────────┘
```

### Tablas

#### leads
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | Primary key |
| name | TEXT | Nombre del lead |
| email | TEXT | Email |
| phone | TEXT | Teléfono |
| telegram_chat_id | VARCHAR(100) | ID de chat de Telegram (único) |
| created_at | TIMESTAMPTZ | Fecha de creación |
| updated_at | TIMESTAMPTZ | Última actualización |

#### conversations
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | Primary key |
| lead_id | UUID | FK → leads |
| most_recent_project_id | UUID | FK → projects (último proyecto consultado) |
| last_message_at | TIMESTAMPTZ | Último mensaje |
| is_answered_by_lead | BOOLEAN | Si el lead respondió |
| created_at | TIMESTAMPTZ | Fecha de creación |
| updated_at | TIMESTAMPTZ | Última actualización |

#### messages
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | Primary key |
| conversation_id | UUID | FK → conversations |
| type | ENUM | 'human' o 'ai-assistant' |
| content | TEXT | Contenido del mensaje |
| created_at | TIMESTAMPTZ | Fecha de creación |

#### projects
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | Primary key |
| name | TEXT | Nombre del proyecto |
| description | TEXT | Descripción |
| district | TEXT | Distrito |
| address | TEXT | Dirección |
| reference | TEXT | Referencia |
| details | TEXT | Detalles adicionales |
| video_url | TEXT | URL de video |
| brochure_url | TEXT | URL de brochure |
| includes_parking | BOOLEAN | Incluye estacionamiento |
| has_showroom | BOOLEAN | Tiene showroom |
| **embedding** | VECTOR(1536) | **Embedding para RAG** |

#### properties
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | Primary key |
| project_id | UUID | FK → projects |
| typology_id | UUID | FK → typologies |
| title | TEXT | Título |
| type | TEXT | Tipo de propiedad |
| description | TEXT | Descripción |
| pricing | INTEGER | Precio |
| view_type | TEXT | Tipo de vista |
| floor_no | TEXT | Número de piso |
| **embedding** | VECTOR(1536) | **Embedding para RAG** |

#### typologies
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | Primary key |
| name | TEXT | Nombre (ej: "2BR Standard") |
| description | TEXT | Descripción |
| type | TEXT | Tipo |
| num_bedrooms | SMALLINT | Número de habitaciones |
| num_bathrooms | SMALLINT | Número de baños |
| area_m2 | TEXT | Área en m² |

#### appointments
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | Primary key |
| lead_id | UUID | FK → leads |
| conversation_id | UUID | FK → conversations |
| project_id | UUID | FK → projects |
| property_id | UUID | FK → properties |
| scheduled_for | TIMESTAMPTZ | Fecha/hora de la cita |
| notes | TEXT | Notas adicionales |
| created_at | TIMESTAMPTZ | Fecha de creación |

---

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# OpenAI
OPENAI_API_KEY=your_openai_key

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/pascal_db
DATABASE_URL_SYNC=postgresql+psycopg2://postgres:postgres@localhost:5432/pascal_db

# Redis
REDIS_URL=redis://localhost:6379/0

# App
DEBUG=true
CONVERSATION_HISTORY_LIMIT=5
SEARCH_CACHE_TTL_SECONDS=3600
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini
```

---

## 📝 Implementación

### Archivos creados/completados en esta fase:

```
src/
├── database/
│   ├── connection.py          ✅ Completado
│   ├── models.py              ✅ Completado
│   └── repositories/
│       ├── __init__.py        ✅ Completado
│       ├── base.py            ✅ Completado (repositorio base genérico)
│       ├── leads.py           ✅ Completado
│       ├── conversations.py   ✅ Completado
│       ├── messages.py        ✅ Completado
│       ├── projects.py        ✅ Completado (incluye búsqueda por embedding)
│       ├── properties.py      ✅ Completado (incluye RAG search)
│       ├── typologies.py      ✅ Completado
│       └── appointments.py    ✅ Completado
├── cache/
│   ├── __init__.py            ✅ Completado
│   ├── redis_client.py        ✅ Completado
│   ├── conversation_cache.py  ✅ Completado
│   └── search_cache.py        ✅ Completado
scripts/
├── __init__.py                ✅ Completado
├── init_db.sql                ✅ Completado
└── test_connections.py        ✅ Completado
```

---

## 🧪 Verificación

### Comandos para verificar la fase:

```bash
# 1. Levantar servicios
docker-compose up -d

# 2. Verificar PostgreSQL
docker exec -it pascal_postgres psql -U postgres -d pascal_db -c "\dt"

# 3. Verificar Redis
docker exec -it pascal_redis redis-cli ping

# 4. Ejecutar script de prueba
python -m scripts.test_connections
```

---

## 📚 Referencias

- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [pgvector Python](https://github.com/pgvector/pgvector-python)
- [Redis-py Async](https://redis-py.readthedocs.io/en/stable/examples/asyncio_examples.html)

