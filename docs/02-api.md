# Fase 2: API REST (FastAPI)

## 📋 Objetivo

Crear endpoints REST para todas las entidades del sistema, siguiendo las mejores prácticas de FastAPI con validación Pydantic, dependency injection y documentación automática.

---

## ✅ Checklist

### 2.1 Configuración FastAPI
- [ ] App principal con lifecycle
- [ ] Router modular
- [ ] Middleware CORS
- [ ] Exception handlers
- [ ] Dependency injection para DB sessions

### 2.2 Schemas Pydantic
- [ ] LeadSchema (Create, Update, Response)
- [ ] ConversationSchema
- [ ] MessageSchema
- [ ] ProjectSchema
- [ ] PropertySchema
- [ ] TypologySchema
- [ ] AppointmentSchema

### 2.3 Endpoints

#### Leads
- [ ] `GET /api/leads` - Listar leads
- [ ] `GET /api/leads/{id}` - Obtener lead
- [ ] `POST /api/leads` - Crear lead
- [ ] `PUT /api/leads/{id}` - Actualizar lead
- [ ] `DELETE /api/leads/{id}` - Eliminar lead
- [ ] `GET /api/leads/telegram/{chat_id}` - Buscar por Telegram ID

#### Conversations
- [ ] `GET /api/conversations` - Listar conversaciones
- [ ] `GET /api/conversations/{id}` - Obtener conversación
- [ ] `POST /api/conversations` - Crear conversación
- [ ] `GET /api/conversations/{id}/messages` - Mensajes de conversación
- [ ] `GET /api/conversations/lead/{lead_id}` - Conversaciones de un lead

#### Messages
- [ ] `POST /api/messages` - Crear mensaje
- [ ] `GET /api/messages/{id}` - Obtener mensaje

#### Projects
- [ ] `GET /api/projects` - Listar proyectos
- [ ] `GET /api/projects/{id}` - Obtener proyecto
- [ ] `POST /api/projects` - Crear proyecto
- [ ] `PUT /api/projects/{id}` - Actualizar proyecto

#### Properties
- [ ] `GET /api/properties` - Listar propiedades
- [ ] `GET /api/properties/{id}` - Obtener propiedad
- [ ] `POST /api/properties` - Crear propiedad
- [ ] `GET /api/properties/project/{project_id}` - Propiedades de un proyecto

#### Typologies
- [ ] `GET /api/typologies` - Listar tipologías
- [ ] `GET /api/typologies/{id}` - Obtener tipología
- [ ] `POST /api/typologies` - Crear tipología

#### Appointments
- [ ] `GET /api/appointments` - Listar citas
- [ ] `GET /api/appointments/{id}` - Obtener cita
- [ ] `POST /api/appointments` - Crear cita
- [ ] `PUT /api/appointments/{id}` - Actualizar cita
- [ ] `GET /api/appointments/lead/{lead_id}` - Citas de un lead

#### Chat (Core endpoint)
- [ ] `POST /api/chat` - Procesar mensaje de chat (orquestador)

---

## 📁 Estructura de Archivos

```
src/
├── api/
│   ├── __init__.py
│   ├── main.py              # App FastAPI principal
│   ├── dependencies.py      # Dependency injection
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py          # Schemas base
│   │   ├── leads.py
│   │   ├── conversations.py
│   │   ├── messages.py
│   │   ├── projects.py
│   │   ├── properties.py
│   │   ├── typologies.py
│   │   ├── appointments.py
│   │   └── chat.py          # Request/Response del chat
│   └── routes/
│       ├── __init__.py
│       ├── leads.py
│       ├── conversations.py
│       ├── messages.py
│       ├── projects.py
│       ├── properties.py
│       ├── typologies.py
│       ├── appointments.py
│       └── chat.py
```

---

## 🔧 Implementación

### App Principal

```python
# src/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.database.connection import init_db
from src.api.routes import leads, conversations, messages, projects, properties, typologies, appointments, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown

app = FastAPI(
    title="Pascal Real Estate API",
    description="API para el asistente conversacional de bienes raíces",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["Conversations"])
app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(properties.router, prefix="/api/properties", tags=["Properties"])
app.include_router(typologies.router, prefix="/api/typologies", tags=["Typologies"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
```

### Ejemplo de Schema

```python
# src/api/schemas/leads.py
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class LeadBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    telegram_chat_id: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(LeadBase):
    pass

class LeadResponse(LeadBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```

### Ejemplo de Router

```python
# src/api/routes/leads.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from src.api.dependencies import get_lead_repository
from src.api.schemas.leads import LeadCreate, LeadUpdate, LeadResponse
from src.database.repositories.leads import LeadRepository

router = APIRouter()

@router.get("/", response_model=List[LeadResponse])
async def list_leads(
    skip: int = 0,
    limit: int = 100,
    repo: LeadRepository = Depends(get_lead_repository)
):
    return await repo.get_all(skip=skip, limit=limit)

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    repo: LeadRepository = Depends(get_lead_repository)
):
    lead = await repo.get_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
```

---

## 🧪 Verificación

### Comandos para verificar la fase:

```bash
# 1. Ejecutar servidor
uvicorn src.api.main:app --reload

# 2. Abrir documentación
open http://localhost:8000/docs

# 3. Probar endpoints con cURL
curl -X GET http://localhost:8000/api/leads
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{"name": "Juan", "email": "juan@test.com"}'
```

---

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic V2](https://docs.pydantic.dev/latest/)

