# Fase 4: AI Module (RAG + Agents)

## 📋 Objetivo

Implementar el módulo de inteligencia artificial que incluye:
- Servicio de embeddings para RAG
- Búsqueda semántica de propiedades
- Sistema de agentes con orquestador
- Cache de búsquedas en Redis

---

## ✅ Checklist

### 4.1 Servicio de Embeddings
- [ ] Cliente OpenAI para embeddings
- [ ] Función para generar embeddings de texto
- [ ] Batch processing para múltiples textos

### 4.2 RAG (Retrieval-Augmented Generation)
- [ ] Búsqueda por similitud vectorial en properties
- [ ] Búsqueda por similitud vectorial en projects
- [ ] Filtros combinados (vector + SQL)
- [ ] Cache de resultados en Redis

### 4.3 Sistema de Agentes
- [ ] Orchestrator Agent (clasificador de intents)
- [ ] Onboarding Agent (saludos, small talk)
- [ ] PropertySearch Agent (búsqueda RAG)
- [ ] Schedule Agent (agendar visitas)

### 4.4 Prompts en Español
- [ ] System prompt para cada agente
- [ ] Ejemplos few-shot para clasificación
- [ ] Templates de respuesta estructurada

---

## 📁 Estructura de Archivos

```
src/
├── ai/
│   ├── __init__.py
│   ├── embeddings.py          # Servicio de embeddings
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── search.py          # Búsqueda semántica
│   │   └── cache.py           # Cache de búsquedas
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py            # Agente base
│   │   ├── orchestrator.py    # Orquestador
│   │   ├── onboarding.py      # Agente de onboarding
│   │   ├── property_search.py # Agente de búsqueda
│   │   └── schedule.py        # Agente de agendamiento
│   └── prompts/
│       ├── __init__.py
│       ├── orchestrator.py    # Prompts del orquestador
│       ├── onboarding.py
│       ├── property_search.py
│       └── schedule.py
```

---

## 🤖 Arquitectura de Agentes

```
                    ┌─────────────────┐
                    │  User Message   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Orchestrator  │
                    │     Agent       │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
   │  Onboarding │  │  Property   │  │  Schedule   │
   │    Agent    │  │   Search    │  │    Agent    │
   └─────────────┘  └──────┬──────┘  └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  RAG Search │
                    │  (pgvector) │
                    └─────────────┘
```

---

## 🔧 Implementación

### Servicio de Embeddings

```python
# src/ai/embeddings.py
from openai import AsyncOpenAI
from src.config import get_settings

settings = get_settings()
client = AsyncOpenAI(api_key=settings.openai_api_key)

async def generate_embedding(text: str) -> list[float]:
    """Generate embedding for a text."""
    response = await client.embeddings.create(
        model=settings.embedding_model,
        input=text
    )
    return response.data[0].embedding

async def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple texts."""
    response = await client.embeddings.create(
        model=settings.embedding_model,
        input=texts
    )
    return [item.embedding for item in response.data]
```

### Búsqueda RAG

```python
# src/ai/rag/search.py
from sqlalchemy import select, text
from src.database.models import Property, Project
from src.ai.embeddings import generate_embedding

async def search_properties_with_rag(
    session,
    query: str,
    filters: dict | None = None,
    limit: int = 5
) -> list[Property]:
    """Search properties using vector similarity."""
    
    # Generate embedding for query
    query_embedding = await generate_embedding(query)
    
    # Build query with vector similarity
    stmt = select(Property).order_by(
        Property.embedding.cosine_distance(query_embedding)
    ).limit(limit)
    
    # Apply filters if provided
    if filters:
        if filters.get("num_bedrooms"):
            # Join with typology and filter
            pass
        if filters.get("max_price"):
            stmt = stmt.where(Property.pricing <= filters["max_price"])
        if filters.get("district"):
            # Join with project and filter
            pass
    
    result = await session.execute(stmt)
    return result.scalars().all()
```

### Orchestrator Agent

```python
# src/ai/agents/orchestrator.py
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class Intent(str, Enum):
    ONBOARDING_SMALL_TALK = "ONBOARDING_SMALL_TALK"
    PROPERTY_SEARCH = "PROPERTY_SEARCH"
    SCHEDULE_VISIT = "SCHEDULE_VISIT"

CLASSIFICATION_PROMPT = """
Eres un clasificador de intenciones para un asistente inmobiliario.

Clasifica el siguiente mensaje del usuario en una de estas categorías:
- ONBOARDING_SMALL_TALK: Saludos, preguntas generales, small talk
- PROPERTY_SEARCH: Búsqueda de propiedades, consultas sobre departamentos, precios, ubicaciones
- SCHEDULE_VISIT: Quiere agendar una visita o cita

IMPORTANTE: Si el saludo incluye una intención clara de búsqueda, clasifica como PROPERTY_SEARCH.

Ejemplos:
- "Hola!" → ONBOARDING_SMALL_TALK
- "Buenas tardes" → ONBOARDING_SMALL_TALK
- "Qué pueden hacer?" → ONBOARDING_SMALL_TALK
- "Hola, busco un depa de 2 habitaciones" → PROPERTY_SEARCH
- "Tienen departamentos en Miraflores?" → PROPERTY_SEARCH
- "Cuánto cuesta el de 3 dormitorios?" → PROPERTY_SEARCH
- "Quiero agendar una visita" → SCHEDULE_VISIT
- "Puedo ir a verlo el sábado?" → SCHEDULE_VISIT

Mensaje: {message}

Responde SOLO con la categoría, sin explicación.
"""

class OrchestratorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.prompt = ChatPromptTemplate.from_template(CLASSIFICATION_PROMPT)
    
    async def classify(self, message: str) -> Intent:
        chain = self.prompt | self.llm
        response = await chain.ainvoke({"message": message})
        return Intent(response.content.strip())
```

### Property Search Agent

```python
# src/ai/agents/property_search.py
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.ai.rag.search import search_properties_with_rag

SEARCH_PROMPT = """
Eres un asistente inmobiliario experto. Ayudas a los usuarios a encontrar su departamento ideal.

Contexto de propiedades encontradas:
{properties_context}

Historial de conversación:
{conversation_history}

Mensaje del usuario: {message}

Instrucciones:
1. Presenta las propiedades de forma clara y atractiva
2. Destaca las características más relevantes según la consulta
3. Sugiere opciones si no hay coincidencias exactas
4. Pregunta si desean más información o agendar una visita

Responde en español de forma amigable y profesional.
"""

class PropertySearchAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        self.prompt = ChatPromptTemplate.from_template(SEARCH_PROMPT)
    
    async def search(self, session, message: str, conversation_history: list) -> dict:
        # 1. Search properties with RAG
        properties = await search_properties_with_rag(session, message)
        
        # 2. Build context
        properties_context = self._build_context(properties)
        
        # 3. Generate response
        chain = self.prompt | self.llm
        response = await chain.ainvoke({
            "properties_context": properties_context,
            "conversation_history": conversation_history,
            "message": message
        })
        
        return {
            "type": "PROPERTY_SEARCH_RESULT",
            "response": response.content,
            "properties": [self._property_to_dict(p) for p in properties]
        }
```

---

## 📝 Estructura de Respuesta

```python
# Respuesta estructurada del sistema
{
    "type": "PROPERTY_SEARCH_RESULT",  # o ONBOARDING, SCHEDULE_CONFIRMATION
    "summary": "Encontré 3 propiedades en Miraflores",
    "response": "¡Hola! Tengo excelentes opciones para ti...",
    "items": [
        {
            "id": "uuid",
            "project_name": "Torre Pacífico",
            "title": "Depa 2BR vista mar",
            "price_usd": 185000,
            "bedrooms": 2,
            "district": "Miraflores"
        }
    ],
    "suggested_actions": ["ver_detalles", "agendar_visita"],
    "debug": {
        "intent": "PROPERTY_SEARCH",
        "rag_results_count": 3,
        "cached": false
    }
}
```

---

## 🧪 Verificación

```bash
# 1. Test de embeddings
python -c "from src.ai.embeddings import generate_embedding; import asyncio; print(len(asyncio.run(generate_embedding('test'))))"

# 2. Test de clasificación
python -m scripts.test_orchestrator

# 3. Test de búsqueda RAG
python -m scripts.test_rag_search
```

---

## 📚 Referencias

- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [pgvector Similarity Search](https://github.com/pgvector/pgvector#querying)

