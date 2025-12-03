# Fase 6: Telegram BFF (Backend for Frontend)

## Descripción

Capa de integración con Telegram Bot API que actúa como un adaptador entre la API de chat y Telegram. Esta arquitectura permite reutilizar la lógica del core con otros canales (WhatsApp, Instagram) en el futuro.

## Arquitectura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Telegram      │────▶│   BFF Layer     │────▶│   Core API      │
│   Bot API       │     │   /telegram     │     │   /api/chat     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   Formatters    │
                        │   Keyboards     │
                        └─────────────────┘
```

## Estructura de Archivos

```
src/bff/
├── __init__.py
└── telegram/
    ├── __init__.py
    ├── bot.py          # Cliente de Telegram API
    ├── handlers.py     # Procesadores de mensajes
    ├── formatters.py   # Formateadores Markdown
    ├── keyboards.py    # Teclados inline/reply
    └── router.py       # Router FastAPI (webhook)
```

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/telegram/webhook` | Recibe updates de Telegram |
| GET | `/telegram/webhook/info` | Info del webhook actual |
| POST | `/telegram/webhook/set` | Configurar webhook URL |
| DELETE | `/telegram/webhook` | Eliminar webhook |
| GET | `/telegram/bot/me` | Info del bot |

## Configuración

### 1. Crear Bot en Telegram

1. Abre Telegram y busca `@BotFather`
2. Envía `/newbot`
3. Sigue las instrucciones para nombrar tu bot
4. Guarda el token que te proporciona

### 2. Actualizar `.env`

```env
# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_WEBHOOK_SECRET=mi_secret_opcional
```

### 3. Configurar Webhook

El webhook requiere una URL HTTPS pública. Opciones:

**Opción A: ngrok (desarrollo)**
```bash
# Instalar ngrok
brew install ngrok

# Exponer puerto local
ngrok http 8000
```

**Opción B: Servidor con HTTPS**
```bash
# Configurar webhook
curl -X POST "http://localhost:8000/telegram/webhook/set?webhook_url=https://tudominio.com/telegram/webhook"
```

## Comandos del Bot

| Comando | Descripción |
|---------|-------------|
| `/start` | Mensaje de bienvenida + menú |
| `/menu` | Mostrar menú principal |
| `/buscar` | Iniciar búsqueda de propiedades |
| `/proyectos` | Ver proyectos disponibles |
| `/agendar` | Agendar una visita |
| `/ayuda` | Ver lista de comandos |

## Teclados Inline

### Menú Principal
```
┌─────────────────────┐
│ 🔍 Buscar propiedad │
├─────────────────────┤
│ 🏢 Ver proyectos    │
├─────────────────────┤
│ 📅 Mis citas        │
├─────────────────────┤
│ 💬 Hablar con asesor│
└─────────────────────┘
```

### Propiedades Encontradas
```
┌─────────────────────────────┐
│ 🏠 Depa 2BR Vista Mar - ... │
├─────────────────────────────┤
│ 🏠 Depa 1BR Moderno - ...   │
├─────────────────────────────┤
│ 📅 Agendar visita │ 🔍 Más  │
└─────────────────────────────┘
```

## Flujo de Mensajes

```
1. Usuario envía mensaje a Telegram
2. Telegram envía update a /telegram/webhook
3. Handler parsea el update (mensaje o callback)
4. Se envía "typing" indicator
5. Se procesa via ChatService (/api/chat internamente)
6. Se formatea respuesta para Telegram (Markdown)
7. Se agregan teclados inline si hay propiedades
8. Se envía respuesta al usuario
```

## Formateo de Mensajes

### Propiedad Individual
```markdown
🏠 *Depa 2BR Vista Mar - Piso 15*
🏢 Proyecto: Torre Pacífico
📍 Miraflores
💰 *$185,000*
🛏 2 hab | 🚿 2 baños | 📐 65-85 m²
```

### Confirmación de Cita
```markdown
✅ *¡Cita Agendada!*

🏢 *Proyecto:* Torre Pacífico
📅 *Fecha:* Sábado 07/12/2025
🕐 *Hora:* 10:00 AM
📍 *Dirección:* Av. Larco 123, Miraflores

_Te contactaremos para confirmar los detalles._
```

## Callbacks

Los botones inline envían callbacks con formato `action:value`:

| Callback | Acción |
|----------|--------|
| `property:uuid` | Ver detalle de propiedad |
| `project:uuid` | Ver detalle de proyecto |
| `schedule:tomorrow` | Agendar para mañana |
| `time:morning` | Seleccionar horario mañana |
| `menu:search` | Ir a búsqueda |
| `action:cancel` | Cancelar operación |
| `confirm:yes` | Confirmar |

## Pruebas

### Con ngrok
```bash
# Terminal 1: Servidor
uvicorn src.api.main:app --reload --port 8000

# Terminal 2: ngrok
ngrok http 8000

# Terminal 3: Configurar webhook (usar URL de ngrok)
curl -X POST "http://localhost:8000/telegram/webhook/set?webhook_url=https://xxxx.ngrok.io/telegram/webhook"

# Verificar
curl http://localhost:8000/telegram/webhook/info
```

### Simular Update (sin Telegram)
```bash
curl -X POST http://localhost:8000/telegram/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456789,
    "message": {
      "message_id": 1,
      "from": {"id": 123, "first_name": "Test", "username": "test_user"},
      "chat": {"id": 123, "type": "private"},
      "date": 1699000000,
      "text": "Hola, busco un departamento en Miraflores"
    }
  }'
```

## Seguridad

### Verificación de Webhook
```python
# El header X-Telegram-Bot-Api-Secret-Token se verifica automáticamente
# si TELEGRAM_WEBHOOK_SECRET está configurado en .env
```

### Rate Limiting
- Telegram tiene límites: ~30 mensajes/segundo al mismo chat
- El bot responde con status 200 incluso si hay errores internos
- Esto previene que Telegram reintente enviar updates

## Próximos Pasos

- [ ] Soporte para envío de imágenes de propiedades
- [ ] Ubicación en mapa (location message)
- [ ] Notificaciones push de citas
- [ ] Integración con pagos (Telegram Payments)
- [ ] WhatsApp BFF (mismo patrón)
