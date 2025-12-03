# Fase 3: Seed Data

## 📋 Objetivo

Crear datos de prueba realistas para poder probar el sistema completo, especialmente la funcionalidad de RAG (búsqueda semántica de propiedades).

---

## ✅ Checklist

### 3.1 Script de Seed
- [ ] Crear proyectos inmobiliarios (3-5 proyectos)
- [ ] Crear tipologías (1BR, 2BR, 3BR, etc.)
- [ ] Crear propiedades (10-20 propiedades)
- [ ] Generar embeddings para proyectos
- [ ] Generar embeddings para propiedades
- [ ] Crear lead de prueba
- [ ] Crear conversación de ejemplo

### 3.2 Datos Realistas
- [ ] Proyectos en diferentes distritos de Lima
- [ ] Precios realistas en USD
- [ ] Descripciones en español
- [ ] Variedad de tipologías

---

## 📁 Estructura de Archivos

```
scripts/
├── seed_data.py           # Script principal de seeding
├── data/
│   ├── projects.json      # Datos de proyectos
│   ├── typologies.json    # Datos de tipologías
│   └── properties.json    # Datos de propiedades
```

---

## 🏢 Datos de Ejemplo

### Proyectos

```json
[
  {
    "name": "Torre Pacífico",
    "description": "Moderno edificio residencial de 20 pisos con vista al mar. Acabados de primera, áreas comunes premium incluyendo piscina, gimnasio y zona de parrillas.",
    "district": "Miraflores",
    "address": "Av. Malecón de la Reserva 1234",
    "reference": "Frente al Parque del Amor",
    "details": "Entrega inmediata. Financiamiento directo disponible.",
    "includes_parking": true,
    "has_showroom": true
  },
  {
    "name": "Jardines de Surco",
    "description": "Condominio familiar con amplias áreas verdes. Departamentos espaciosos ideales para familias. Club house, juegos para niños y seguridad 24/7.",
    "district": "Santiago de Surco",
    "address": "Av. El Polo 567",
    "reference": "A 2 cuadras del Jockey Plaza",
    "details": "Proyecto en construcción. Entrega 2025.",
    "includes_parking": true,
    "has_showroom": true
  },
  {
    "name": "Loft San Isidro",
    "description": "Edificio boutique de solo 8 pisos. Diseño contemporáneo con lofts de doble altura. Ubicación privilegiada en zona financiera.",
    "district": "San Isidro",
    "address": "Calle Los Laureles 890",
    "reference": "A una cuadra del Golf",
    "details": "Últimas unidades disponibles.",
    "includes_parking": true,
    "has_showroom": false
  }
]
```

### Tipologías

```json
[
  {
    "name": "Studio",
    "description": "Departamento tipo estudio, ideal para solteros o parejas",
    "type": "studio",
    "num_bedrooms": 0,
    "num_bathrooms": 1,
    "area_m2": "35-45"
  },
  {
    "name": "1 Dormitorio",
    "description": "Departamento de un dormitorio con sala-comedor integrado",
    "type": "1BR",
    "num_bedrooms": 1,
    "num_bathrooms": 1,
    "area_m2": "45-60"
  },
  {
    "name": "2 Dormitorios",
    "description": "Departamento familiar de dos dormitorios",
    "type": "2BR",
    "num_bedrooms": 2,
    "num_bathrooms": 2,
    "area_m2": "65-85"
  },
  {
    "name": "3 Dormitorios",
    "description": "Amplio departamento de tres dormitorios para familias grandes",
    "type": "3BR",
    "num_bedrooms": 3,
    "num_bathrooms": 2,
    "area_m2": "90-120"
  }
]
```

### Propiedades

```json
[
  {
    "project": "Torre Pacífico",
    "typology": "2 Dormitorios",
    "title": "Depa 2BR con vista al mar - Piso 15",
    "type": "departamento",
    "description": "Hermoso departamento de 2 dormitorios con vista panorámica al océano. Sala amplia, cocina equipada, 2 baños completos. Incluye 1 estacionamiento.",
    "pricing": 185000,
    "view_type": "mar",
    "floor_no": "15"
  },
  {
    "project": "Torre Pacífico",
    "typology": "3 Dormitorios",
    "title": "Penthouse 3BR - Último piso",
    "type": "penthouse",
    "description": "Espectacular penthouse de 3 dormitorios con terraza privada. Vista 360°, acabados de lujo, cocina italiana. Incluye 2 estacionamientos.",
    "pricing": 450000,
    "view_type": "mar",
    "floor_no": "20"
  },
  {
    "project": "Jardines de Surco",
    "typology": "2 Dormitorios",
    "title": "Depa 2BR familiar - Vista jardín",
    "type": "departamento",
    "description": "Departamento ideal para familias. 2 dormitorios amplios, sala-comedor con salida a balcón, vista a áreas verdes del condominio.",
    "pricing": 125000,
    "view_type": "jardín",
    "floor_no": "5"
  },
  {
    "project": "Jardines de Surco",
    "typology": "3 Dormitorios",
    "title": "Depa 3BR esquinero - Doble vista",
    "type": "departamento",
    "description": "Amplio departamento esquinero de 3 dormitorios. Doble vista, muy iluminado, walk-in closet en dormitorio principal.",
    "pricing": 175000,
    "view_type": "jardín",
    "floor_no": "8"
  },
  {
    "project": "Loft San Isidro",
    "typology": "1 Dormitorio",
    "title": "Loft 1BR doble altura",
    "type": "loft",
    "description": "Exclusivo loft de doble altura con 1 dormitorio en mezzanine. Diseño moderno, grandes ventanales, ubicación premium.",
    "pricing": 165000,
    "view_type": "ciudad",
    "floor_no": "4"
  },
  {
    "project": "Loft San Isidro",
    "typology": "Studio",
    "title": "Studio ejecutivo",
    "type": "studio",
    "description": "Studio completamente equipado para ejecutivos. Cocina americana, baño completo, área de trabajo integrada.",
    "pricing": 95000,
    "view_type": "ciudad",
    "floor_no": "3"
  }
]
```

---

## 🔧 Implementación

### Script de Seed

```python
# scripts/seed_data.py
import asyncio
import json
from pathlib import Path
from src.database.connection import get_async_session
from src.database.repositories.projects import ProjectRepository
from src.database.repositories.properties import PropertyRepository
from src.database.repositories.typologies import TypologyRepository
from src.services.embedding_service import EmbeddingService

async def seed_database():
    """Seed the database with test data."""
    
    async with get_async_session() as session:
        # 1. Seed typologies
        # 2. Seed projects (with embeddings)
        # 3. Seed properties (with embeddings)
        # 4. Create test lead
        pass

if __name__ == "__main__":
    asyncio.run(seed_database())
```

---

## 🧪 Verificación

```bash
# 1. Ejecutar seed
python -m scripts.seed_data

# 2. Verificar datos en DB
docker exec -it pascal_postgres psql -U postgres -d pascal_db \
  -c "SELECT name, district FROM projects;"

# 3. Verificar embeddings
docker exec -it pascal_postgres psql -U postgres -d pascal_db \
  -c "SELECT title, embedding IS NOT NULL as has_embedding FROM properties;"
```

---

## 📚 Referencias

- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [pgvector](https://github.com/pgvector/pgvector)

