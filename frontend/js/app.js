/**
 * Pascal Real Estate - Chat Application
 * Vanilla JavaScript Chat Client
 */

// API Configuration
const API_BASE_URL = '/api';
const CHAT_ENDPOINT = `${API_BASE_URL}/chat/`;

// State
let conversationId = null;
let isLoading = false;

// DOM Elements
const messagesWrapper = document.getElementById('messagesWrapper');
const messagesContainer = document.getElementById('messagesContainer');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const quickActions = document.getElementById('quickActions');
const propertiesPanel = document.getElementById('propertiesPanel');
const propertiesList = document.getElementById('propertiesList');
const closePanel = document.getElementById('closePanel');
const clearChat = document.getElementById('clearChat');

// ============================================
// Initialization
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    messageInput.focus();
});

function initEventListeners() {
    // Form submission
    chatForm.addEventListener('submit', handleSubmit);
    
    // Quick actions
    quickActions.addEventListener('click', handleQuickAction);
    
    // Panel controls
    closePanel.addEventListener('click', () => togglePanel(false));
    clearChat.addEventListener('click', handleClearChat);
    
    // Input handling
    messageInput.addEventListener('input', updateSendButton);
}

// ============================================
// Message Handling
// ============================================
async function handleSubmit(e) {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message || isLoading) return;
    
    await sendMessage(message);
}

async function handleQuickAction(e) {
    const button = e.target.closest('.quick-action');
    if (!button) return;
    
    const message = button.dataset.message;
    if (message) {
        await sendMessage(message);
    }
}

async function sendMessage(message) {
    console.log('Stored: ')
    console.log(conversationId)
    // Add user message to UI
    addMessage(message, 'user');
    
    // Clear input
    messageInput.value = '';
    updateSendButton();
    
    // Hide quick actions after first message
    quickActions.style.display = 'none';
    
    // Show typing indicator
    const typingElement = showTypingIndicator();
    
    try {
        isLoading = true;
        sendButton.disabled = true;
        
        // Send to API
        const response = await fetch(CHAT_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                channel: 'web',
                session_id: conversationId,
            }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Store conversation ID
        if (data.conversation_id) {
            console.log('Store conversacion')
            console.log(data)
            conversationId = data.conversation_id;
        }
        
        // Remove typing indicator
        typingElement.remove();
        
        // Add bot response
        addMessage(data.response, 'agent');
        
        // Handle properties if present
        if (data.properties && data.properties.length > 0) {
            displayProperties(data.properties);
        }
        
        // Handle appointment confirmation
        if (data.appointment) {
            showAppointmentConfirmation(data.appointment);
        }
        
        // Log debug info
        if (data.debug) {
            console.log('Debug:', data.debug);
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        typingElement.remove();
        addMessage('Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.', 'agent');
    } finally {
        isLoading = false;
        sendButton.disabled = false;
        messageInput.focus();
    }
}

// ============================================
// UI Functions
// ============================================
function addMessage(content, type) {
    const time = new Date().toLocaleTimeString('es-PE', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    const messageGroup = document.createElement('div');
    messageGroup.className = `message-group ${type}`;
    
    const avatar = type === 'agent' ? '🤖' : '👤';
    
    // Format content (handle newlines and markdown-like formatting)
    const formattedContent = formatMessageContent(content);
    
    messageGroup.innerHTML = `
        <div class="message-avatar">
            <span>${avatar}</span>
        </div>
        <div class="message-content">
            <div class="message">
                ${formattedContent}
            </div>
            <span class="message-time">${time}</span>
        </div>
    `;
    
    messagesWrapper.appendChild(messageGroup);
    scrollToBottom();
}

function formatMessageContent(content) {
    // Handle null/undefined
    if (!content) return '';
    
    // Escape HTML
    let formatted = content
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    
    // Convert markdown-like formatting
    // Bold: **text** or *text*
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*(.+?)\*/g, '<strong>$1</strong>');
    
    // Lists (lines starting with - or •)
    const lines = formatted.split('\n');
    let inList = false;
    let result = [];
    
    for (let line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('- ') || trimmed.startsWith('• ') || trimmed.startsWith('* ')) {
            if (!inList) {
                result.push('<ul>');
                inList = true;
            }
            result.push(`<li>${trimmed.substring(2)}</li>`);
        } else {
            if (inList) {
                result.push('</ul>');
                inList = false;
            }
            if (trimmed) {
                result.push(`<p>${trimmed}</p>`);
            }
        }
    }
    if (inList) {
        result.push('</ul>');
    }
    
    return result.join('');
}

function showTypingIndicator() {
    const typingGroup = document.createElement('div');
    typingGroup.className = 'message-group agent';
    typingGroup.id = 'typing-indicator';
    
    typingGroup.innerHTML = `
        <div class="message-avatar">
            <span>🤖</span>
        </div>
        <div class="message-content">
            <div class="message">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
    
    messagesWrapper.appendChild(typingGroup);
    scrollToBottom();
    
    return typingGroup;
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function updateSendButton() {
    const hasText = messageInput.value.trim().length > 0;
    sendButton.disabled = !hasText || isLoading;
}

// ============================================
// Properties Panel
// ============================================
function displayProperties(properties) {
    propertiesList.innerHTML = '';
    
    properties.forEach(property => {
        const card = createPropertyCard(property);
        propertiesList.appendChild(card);
    });
    
    togglePanel(true);
}

function createPropertyCard(property) {
    const card = document.createElement('div');
    card.className = 'property-card';
    
    const price = property.price_usd 
        ? `$${property.price_usd.toLocaleString()}` 
        : 'Consultar';
    
    const location = property.district || property.project_name || 'Lima';
    const bedrooms = property.bedrooms || '-';
    const bathrooms = property.bathrooms || '-';
    const area = property.area_m2 || '-';
    
    card.innerHTML = `
        <div class="property-card-header">
            <h3 class="property-title">${property.title || 'Propiedad'}</h3>
            <span class="property-price">${price}</span>
        </div>
        <div class="property-location">
            <span>📍</span>
            <span>${location}</span>
        </div>
        <div class="property-features">
            <span class="feature">
                <span>🛏️</span>
                <span>${bedrooms} hab.</span>
            </span>
            <span class="feature">
                <span>🚿</span>
                <span>${bathrooms} baños</span>
            </span>
            <span class="feature">
                <span>📐</span>
                <span>${area} m²</span>
            </span>
        </div>
        <div class="property-card-actions">
            <button class="btn-secondary" onclick="askAboutProperty('${property.title}')">
                Más info
            </button>
            <button class="btn-primary" onclick="scheduleVisit('${property.title}')">
                Agendar visita
            </button>
        </div>
    `;
    
    return card;
}

function togglePanel(show) {
    if (show) {
        propertiesPanel.classList.add('open');
    } else {
        propertiesPanel.classList.remove('open');
    }
}

// ============================================
// Action Handlers
// ============================================
function askAboutProperty(propertyTitle) {
    const message = `Dame más información sobre "${propertyTitle}"`;
    sendMessage(message);
}

function scheduleVisit(propertyTitle) {
    const message = `Quiero agendar una visita para ver "${propertyTitle}"`;
    sendMessage(message);
}

function showAppointmentConfirmation(appointment) {
    // Could show a special confirmation UI
    console.log('Appointment confirmed:', appointment);
}

function handleClearChat() {
    // Keep only the welcome message
    const welcomeMessage = messagesWrapper.querySelector('.message-group');
    messagesWrapper.innerHTML = '';
    if (welcomeMessage) {
        messagesWrapper.appendChild(welcomeMessage.cloneNode(true));
    }
    
    // Reset state
    conversationId = null;
    quickActions.style.display = 'flex';
    togglePanel(false);
    
    messageInput.focus();
}

// ============================================
// Utility Functions
// ============================================
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Make functions available globally for onclick handlers
window.askAboutProperty = askAboutProperty;
window.scheduleVisit = scheduleVisit;

