# Fase 5: Frontend Vanilla JS

## Descripción

Interface de chat web moderna usando HTML, CSS y JavaScript vanilla. Permite probar el sistema conversacional sin necesidad de Telegram.

## Acceso

```
http://localhost:8000/chat
```

## Estructura de Archivos

```
frontend/
├── index.html          # Página principal
├── css/
│   └── styles.css      # Estilos (variables CSS, responsive)
├── js/
│   └── app.js          # Lógica de la aplicación
└── assets/             # Imágenes y recursos
```

## Características

### 🎨 Diseño

- **Paleta cálida**: Colores terracota/coral para inmobiliaria
- **Tipografía**: Outfit (Google Fonts)
- **Responsive**: Adaptable a móvil y desktop
- **Dark sidebar**: Navegación elegante

### 💬 Chat

- Mensajes con animaciones de entrada
- Indicador de escritura (typing indicator)
- Formateo de markdown (bold, listas)
- Timestamp en cada mensaje

### 🏠 Propiedades

- Panel lateral deslizable
- Cards de propiedad con:
  - Título y precio
  - Ubicación
  - Características (habitaciones, baños, área)
  - Botones de acción

### ⚡ Acciones Rápidas

- Botones predefinidos para consultas comunes
- Se ocultan después del primer mensaje

## Arquitectura JavaScript

```javascript
// Estado de la aplicación
let conversationId = null;  // ID de conversación activa
let isLoading = false;      // Estado de carga

// Flujo de mensaje
sendMessage(text)
  → addMessage(text, 'user')      // UI: mensaje del usuario
  → showTypingIndicator()         // UI: "escribiendo..."
  → fetch('/api/chat/')           // API call
  → addMessage(response, 'agent') // UI: respuesta
  → displayProperties(props)      // UI: panel de propiedades
```

## API Utilizada

### POST /api/chat/

**Request:**
```json
{
  "message": "Busco un departamento de 2 habitaciones",
  "channel": "web",
  "session_id": "uuid-opcional"
}
```

**Response:**
```json
{
  "type": "PROPERTY_SEARCH_RESULT",
  "response": "Encontré estas opciones...",
  "properties": [
    {
      "id": "uuid",
      "title": "Depa 2BR Vista Mar",
      "project_name": "Torre Pacífico",
      "price_usd": 185000,
      "bedrooms": 2,
      "bathrooms": 2,
      "district": "Miraflores",
      "area_m2": "65-85"
    }
  ],
  "conversation_id": "uuid"
}
```

## CSS Variables

```css
:root {
  /* Colores primarios */
  --primary-500: #f85a47;    /* Coral principal */
  --primary-600: #e53e2a;    /* Hover */
  
  /* Neutrales */
  --neutral-100: #f5f5f4;    /* Fondo claro */
  --neutral-800: #292524;    /* Texto */
  --neutral-900: #1c1917;    /* Sidebar */
  
  /* Acentos */
  --accent-teal: #0d9488;    /* Usuario */
  --success: #22c55e;        /* Online */
}
```

## Responsive Breakpoints

| Breakpoint | Cambios |
|------------|---------|
| > 1024px | Layout completo con sidebar y panel |
| 768-1024px | Panel más estrecho |
| < 768px | Sin sidebar, panel fullscreen |

## Interacciones

### Envío de Mensaje
1. Usuario escribe mensaje
2. Click en enviar o Enter
3. Mensaje aparece en UI (animación)
4. Typing indicator mientras carga
5. Respuesta del agente con animación

### Panel de Propiedades
1. Si la respuesta incluye `properties[]`
2. Panel se desliza desde la derecha
3. Cards con información de cada propiedad
4. Botones: "Más info" y "Agendar visita"

### Limpiar Chat
1. Click en icono de basura
2. Se elimina todo excepto mensaje de bienvenida
3. Se resetea `conversationId`
4. Vuelven las acciones rápidas

## Pruebas Manuales

1. **Saludo**: "Hola" → Respuesta de bienvenida
2. **Búsqueda**: "Busco 2 habitaciones en Miraflores" → Propiedades + Panel
3. **Proyecto**: "Info de Torre Pacífico" → Detalles del proyecto
4. **Agendar**: "Quiero agendar visita" → Flujo de agendamiento

## Próximos Pasos

- [ ] Soporte para imágenes de propiedades
- [ ] Historial de conversaciones guardado
- [ ] Modo oscuro toggle
- [ ] Notificaciones push
- [ ] PWA (Progressive Web App)
