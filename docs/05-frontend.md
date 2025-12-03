# Fase 5: Frontend Vanilla

## 📋 Objetivo

Crear una interfaz web simple usando HTML, CSS y JavaScript vanilla para probar el sistema de chat sin depender de la API de Telegram.

---

## ✅ Checklist

### 5.1 Estructura HTML
- [ ] Layout de chat moderno
- [ ] Input de mensaje
- [ ] Área de mensajes con scroll
- [ ] Indicador de "escribiendo..."

### 5.2 Estilos CSS
- [ ] Diseño responsive
- [ ] Burbujas de chat diferenciadas
- [ ] Animaciones suaves
- [ ] Dark/Light mode

### 5.3 JavaScript
- [ ] Conexión con API /api/chat
- [ ] Manejo de sesión (lead_id, conversation_id)
- [ ] Renderizado de mensajes
- [ ] Renderizado de propiedades (cards)
- [ ] Auto-scroll

### 5.4 Funcionalidades
- [ ] Enviar mensaje con Enter
- [ ] Mostrar historial de conversación
- [ ] Mostrar propiedades como cards
- [ ] Botones de acción (ver más, agendar)

---

## 📁 Estructura de Archivos

```
frontend/
├── index.html
├── css/
│   └── styles.css
├── js/
│   ├── app.js           # Lógica principal
│   ├── api.js           # Llamadas a la API
│   └── ui.js            # Renderizado de UI
└── assets/
    └── icons/
```

---

## 🎨 Diseño

### Wireframe

```
┌────────────────────────────────────────────┐
│  🏠 Pascal Real Estate Assistant           │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │ 🤖 ¡Hola! Soy el asistente de       │  │
│  │    Pascal. ¿En qué puedo ayudarte?  │  │
│  └──────────────────────────────────────┘  │
│                                            │
│          ┌──────────────────────────────┐  │
│          │ Busco un depa de 2 hab en   │  │
│          │ Miraflores                   │  │
│          └──────────────────────────────┘  │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │ 🤖 ¡Excelente elección! Encontré    │  │
│  │    estas opciones para ti:          │  │
│  │                                      │  │
│  │  ┌────────────┐  ┌────────────┐     │  │
│  │  │ 🏢 Torre   │  │ 🏢 Ocean  │     │  │
│  │  │ Pacífico   │  │ View      │     │  │
│  │  │ 2BR       │  │ 2BR       │     │  │
│  │  │ $185,000  │  │ $195,000  │     │  │
│  │  │ [Ver más] │  │ [Ver más] │     │  │
│  │  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────────┘  │
│                                            │
├────────────────────────────────────────────┤
│  [Escribe tu mensaje...          ] [Enviar]│
└────────────────────────────────────────────┘
```

---

## 🔧 Implementación

### HTML Base

```html
<!-- frontend/index.html -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pascal Real Estate Assistant</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <div class="chat-container">
        <header class="chat-header">
            <h1>🏠 Pascal Real Estate</h1>
            <p>Asistente Virtual</p>
        </header>
        
        <main class="chat-messages" id="messages">
            <!-- Messages will be rendered here -->
        </main>
        
        <footer class="chat-input">
            <input 
                type="text" 
                id="messageInput" 
                placeholder="Escribe tu mensaje..."
                autocomplete="off"
            >
            <button id="sendButton">Enviar</button>
        </footer>
    </div>
    
    <script src="js/api.js"></script>
    <script src="js/ui.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
```

### API Client

```javascript
// frontend/js/api.js
const API_BASE = 'http://localhost:8000/api';

class ChatAPI {
    constructor() {
        this.sessionId = localStorage.getItem('sessionId') || this.generateSessionId();
        localStorage.setItem('sessionId', this.sessionId);
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }
    
    async sendMessage(message) {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: this.sessionId
            })
        });
        
        if (!response.ok) {
            throw new Error('Error sending message');
        }
        
        return response.json();
    }
    
    async getConversationHistory() {
        const response = await fetch(`${API_BASE}/chat/history/${this.sessionId}`);
        return response.json();
    }
}

const chatAPI = new ChatAPI();
```

### UI Renderer

```javascript
// frontend/js/ui.js
class ChatUI {
    constructor(messagesContainer) {
        this.container = messagesContainer;
    }
    
    addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
        messageDiv.innerHTML = this.formatMessage(content);
        this.container.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Handle structured responses with properties
        if (content.properties && content.properties.length > 0) {
            return `
                <p>${content.response}</p>
                <div class="property-cards">
                    ${content.properties.map(p => this.renderPropertyCard(p)).join('')}
                </div>
            `;
        }
        return `<p>${content.response || content}</p>`;
    }
    
    renderPropertyCard(property) {
        return `
            <div class="property-card">
                <h4>${property.title}</h4>
                <p class="project">${property.project_name}</p>
                <p class="price">$${property.price_usd?.toLocaleString()}</p>
                <p class="details">${property.bedrooms} hab · ${property.district}</p>
                <button onclick="viewProperty('${property.id}')">Ver más</button>
            </div>
        `;
    }
    
    showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant typing';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        this.container.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTyping() {
        const typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
    }
    
    scrollToBottom() {
        this.container.scrollTop = this.container.scrollHeight;
    }
}
```

### App Principal

```javascript
// frontend/js/app.js
document.addEventListener('DOMContentLoaded', () => {
    const messagesContainer = document.getElementById('messages');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    
    const ui = new ChatUI(messagesContainer);
    
    // Welcome message
    ui.addMessage({
        response: '¡Hola! 👋 Soy el asistente virtual de Pascal Real Estate. ¿En qué puedo ayudarte hoy? Puedo ayudarte a buscar departamentos, darte información sobre proyectos o agendar una visita.'
    });
    
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Show user message
        ui.addMessage(message, true);
        messageInput.value = '';
        
        // Show typing indicator
        ui.showTyping();
        
        try {
            const response = await chatAPI.sendMessage(message);
            ui.hideTyping();
            ui.addMessage(response);
        } catch (error) {
            ui.hideTyping();
            ui.addMessage({ response: 'Lo siento, hubo un error. Por favor intenta de nuevo.' });
        }
    }
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});
```

---

## 🧪 Verificación

```bash
# 1. Servir frontend (usando Python)
cd frontend && python -m http.server 3000

# 2. Abrir en navegador
open http://localhost:3000

# 3. Probar conversaciones:
#    - "Hola"
#    - "Busco un departamento de 2 habitaciones en Miraflores"
#    - "Quiero agendar una visita"
```

---

## 📚 Referencias

- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [CSS Grid](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [CSS Animations](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Animations)

