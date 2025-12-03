"""
FastAPI application main entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.database.connection import init_db
from src.cache import get_redis_client
from src.api.routes import (
    leads,
    conversations,
    messages,
    projects,
    properties,
    typologies,
    appointments,
    chat,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting Pascal Real Estate API...")
    await init_db()
    print("✅ Database initialized")
    
    # Check Redis connection
    redis = get_redis_client()
    if await redis.ping():
        print("✅ Redis connected")
    else:
        print("⚠️  Redis connection failed")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")
    await redis.disconnect()


app = FastAPI(
    title="Pascal Real Estate API",
    description="""
    API para el asistente conversacional de bienes raíces.
    
    ## Funcionalidades
    
    * **Leads** - Gestión de clientes potenciales
    * **Conversations** - Sesiones de chat
    * **Messages** - Mensajes de conversación
    * **Projects** - Proyectos inmobiliarios
    * **Properties** - Propiedades disponibles
    * **Typologies** - Tipos de propiedades
    * **Appointments** - Citas y visitas
    * **Chat** - Endpoint principal de conversación
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["Conversations"])
app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(properties.router, prefix="/api/properties", tags=["Properties"])
app.include_router(typologies.router, prefix="/api/typologies", tags=["Typologies"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Pascal Real Estate API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    redis = get_redis_client()
    redis_ok = await redis.ping()
    
    return {
        "status": "healthy" if redis_ok else "degraded",
        "database": "connected",
        "redis": "connected" if redis_ok else "disconnected",
    }

