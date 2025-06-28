// DOM Elements

const customerChatInput = document.getElementById('customerChatInput');
const customerSendBtn = document.getElementById('customerSendBtn');
const customerChatContainer = document.getElementById('customerChatContainer');

const distributorChatInput = document.getElementById('distributorChatInput');
const distributorSendBtn = document.getElementById('distributorSendBtn');
const distributorChatContainer = document.getElementById('distributorChatContainer');

const callButton = document.getElementById('callButton');
const metricsContainer = document.getElementById('metrics');
const storeNameElements = document.querySelectorAll('.store-name');
const storeFlagsDropdown = document.getElementById('storeFlagsDropdown');

// Voice control state
let voiceControlActive = false;
let currentDashboardAction = null;

// Event Listeners
if (customerSendBtn) {
    customerSendBtn.addEventListener('click', () => sendCustomerMessage());
}

if (customerChatInput) {
    customerChatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendCustomerMessage();
        }
    });
}

if (distributorSendBtn) {
    distributorSendBtn.addEventListener('click', () => sendDistributorMessage());
}

if (distributorChatInput) {
    distributorChatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendDistributorMessage();
        }
    });
}

if (callButton) {
    callButton.addEventListener('click', async () => {
        try {
            console.log('Call button clicked, checking UltravoxSession availability...');
            
            // Initialize Ultravox if needed
            if (!window.uvSession && window.UltravoxSession) {
                console.log('Creating new UltravoxSession...');
                window.uvSession = new window.UltravoxSession({ experimentalMessages: new Set(["debug"]) });
                console.log('UltravoxSession created successfully');
            } else if (!window.UltravoxSession) {
                console.error('UltravoxSession class is not available. Waiting for module to load...');
                // Wait a bit and try again
                await new Promise(resolve => setTimeout(resolve, 1000));
                if (!window.UltravoxSession) {
                    throw new Error('UltravoxSession is not available. Please refresh the page.');
                }
            }

            // Show loading state
            callButton.disabled = true;
            callButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            console.log('Making request to /start_call endpoint...');
            // Start call with default voice
            const response = await fetch('/start_call', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ voice: 'Mark' })
            });
            
            console.log('Response received:', response.status);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to start voice call');
            }

            const callDetails = await response.json();
            console.log('Call details received:', callDetails);
            
            // Join call and activate features
            if (window.uvSession) {
                console.log('Joining call with URL:', callDetails.joinUrl);
                await window.uvSession.joinCall(callDetails.joinUrl);
                activateAvatar();
                window.uvSession.addEventListener('transcripts', handleVoiceTranscript);
                
                // Update UI
                callButton.classList.add('active');
                const disconnectBtn = document.getElementById('disconnectButton');
                if (disconnectBtn) disconnectBtn.classList.remove('hidden');
                
                // Show success notification
                showSuccessNotification('Voice assistant ready! Start speaking your query.');
                console.log('Voice call started successfully');
            }
        } catch (error) {
            console.error('Voice call error:', error);
            showErrorNotification('Could not start voice assistant: ' + error.message);
        } finally {
            callButton.disabled = false;
            callButton.innerHTML = '<i class="fas fa-phone"></i>';
        }
    });
}

// Add disconnect button handler
const disconnectButton = document.getElementById('disconnectButton');
if (disconnectButton) {
    disconnectButton.addEventListener('click', async () => {
        try {
            if (window.uvSession) {
                await window.uvSession.leaveCall();
                window.uvSession.removeEventListener('transcripts', handleVoiceTranscript);
                
                // Update UI
                callButton.classList.remove('active');
                disconnectButton.classList.add('hidden');
                deactivateAvatar();
                
                showSuccessNotification('Voice assistant disconnected');
            }
        } catch (error) {
            console.error('Error disconnecting voice call:', error);
            showErrorNotification('Could not disconnect voice assistant');
        }
    });
}

// Handle voice transcripts
function handleVoiceTranscript(event) {
    const transcripts = event.target._transcripts;
    if (!transcripts?.length) return;
    
    // Get latest user query
    const userQuery = transcripts
        .filter(t => t?.speaker === "user")
        .map(t => t?.text?.toLowerCase())
        .pop();
        
    if (!userQuery) return;
    
    // Route query to appropriate handler
    if (userQuery.includes('order') || userQuery.includes('buy')) {
        processOrder(userQuery);
    } else if (userQuery.includes('stock') || userQuery.includes('inventory')) {
        checkInventory(userQuery);
    } else if (userQuery.includes('price') || userQuery.includes('cost')) {
        checkPrice(userQuery);
    }
}

// Process order queries
async function processOrder(query) {
    try {
        const response = await fetch('/api/voice/order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        const data = await response.json();
        addVoiceResponse(query, data.response);
    } catch (error) {
        console.error('Order processing error:', error);
        showErrorNotification('Could not process order');
    }
}

// Check inventory queries
async function checkInventory(query) {
    try {
        const response = await fetch('/api/voice/inventory', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        const data = await response.json();
        addVoiceResponse(query, data.response);
        if (data.updateMetrics) updateInventoryMetrics();
    } catch (error) {
        console.error('Inventory check error:', error);
        showErrorNotification('Could not check inventory');
    }
}

// Check price queries
async function checkPrice(query) {
    try {
        const response = await fetch('/api/voice/price', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        const data = await response.json();
        addVoiceResponse(query, data.response);
    } catch (error) {
        console.error('Price check error:', error);
        showErrorNotification('Could not check price');
    }
}

// Add voice interaction to chat
function addVoiceResponse(query, response) {
    if (!customerChatContainer) return;
    addChatMessage(customerChatContainer, query, false);
    addChatMessage(customerChatContainer, response, true);
}

// Activate avatar animation
function activateAvatar() {
    const avatarContainer = document.getElementById('avatarContainer');
    if (!avatarContainer) return;
    
    // Add active class
    avatarContainer.classList.add('active');
    
    // Start ring animation
    const rings = avatarContainer.querySelector('.avatar-rings');
    if (rings) {
        rings.classList.add('active');
    }
}

// Deactivate avatar animation
function deactivateAvatar() {
    const avatarContainer = document.getElementById('avatarContainer');
    if (!avatarContainer) return;
    
    // Remove active class
    avatarContainer.classList.remove('active');
    
    // Stop ring animation
    const rings = avatarContainer.querySelector('.avatar-rings');
    if (rings) {
        rings.classList.remove('active');
    }
}

// Store flag event listeners
if (storeFlagsDropdown) {
    const flagButtons = storeFlagsDropdown.querySelectorAll('.dropdown-item');
    flagButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const countryCode = e.currentTarget.getAttribute('data-country-code');
            changeStore(countryCode);
        });
    });
}

// Chat Functions
function sendCustomerMessage() {
    const message = customerChatInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(customerChatContainer, message, false);
    customerChatInput.value = '';
    
    // Show loading indicator
    const loadingId = showLoadingIndicator(customerChatContainer);
    
    // Process message with backend
    fetch('/api/customer/message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            message: message,
            is_telegram: false // Regular message, not from Telegram
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        removeLoadingIndicator(loadingId);
        
        if (data.status === 'success') {
            // Add response to chat
            addChatMessage(customerChatContainer, data.response, true);
            
            // Update metrics if available
            updateInventoryMetrics();
        } else {
            addChatMessage(customerChatContainer, "Sorry, there was an error processing your request.", true);
        }
    })
    .catch(error => {
        // Remove loading indicator
        removeLoadingIndicator(loadingId);
        console.error('Error:', error);
        addChatMessage(customerChatContainer, "Sorry, there was an error processing your request.", true);
    });
}

function sendDistributorMessage() {
    const message = distributorChatInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(distributorChatContainer, message, false);
    distributorChatInput.value = '';
    
    // Show loading indicator
    const loadingId = showLoadingIndicator(distributorChatContainer);
    
    // Process message with backend
    fetch('/api/distributor/message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            message: message,
            is_telegram: false // Regular message, not from Telegram
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        removeLoadingIndicator(loadingId);
        
        if (data.status === 'success') {
            // Add response to chat
            addChatMessage(distributorChatContainer, data.response, true);
            
            // Update metrics if available
            updateInventoryMetrics();
        } else {
            addChatMessage(distributorChatContainer, "Sorry, there was an error processing your request.", true);
        }
    })
    .catch(error => {
        // Remove loading indicator
        removeLoadingIndicator(loadingId);
        console.error('Error:', error);
        addChatMessage(distributorChatContainer, "Sorry, there was an error processing your request.", true);
    });
}

function changeStore(countryCode) {
    // Show loading notification
    showProcessingNotification('Changing store...');
    
    fetch('/api/change_store', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ country_code: countryCode }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update store name throughout the UI
            const storeNameElements = document.querySelectorAll('.store-name');
            storeNameElements.forEach(element => {
                element.textContent = data.store.name;
            });
            
            // Add highlight-animation class for animation effect
            storeNameElements.forEach(element => {
                // Add store-name-display class for styling if not already present
                element.classList.add('store-name-display');
                
                // Reset animation by removing and re-adding the class
                element.classList.remove('highlight-animation');
                
                // Trigger browser reflow to restart animation
                void element.offsetWidth;
                
                // Add the animation class
                element.classList.add('highlight-animation');
                
                // Clean up after animation completes
                setTimeout(() => {
                    element.classList.remove('highlight-animation');
                }, 1500);
            });
            
            // Update store name in title
            const pageTitle = document.getElementById('storeTitle');
            if (pageTitle) {
                pageTitle.textContent = data.store.name;
            }
            
            // Update the active flag in the dropdown
            const flagButtons = document.querySelectorAll('.flag-button');
            flagButtons.forEach(button => {
                button.classList.remove('active');
                if (button.getAttribute('data-country-code') === countryCode) {
                    button.classList.add('active');
                }
            });
            
            // Update the current flag icon
            const currentFlagIcon = document.getElementById('currentFlagIcon');
            if (currentFlagIcon) {
                currentFlagIcon.className = `flag-icon flag-icon-${countryCode.toLowerCase()}`;
            }
            
            // Update country titles
            const countryTitles = document.querySelectorAll('.country-name');
            countryTitles.forEach(element => {
                element.textContent = data.store.country;
            });
            
            // Update currency symbol throughout the page
            const currencyElements = document.querySelectorAll('.currency-symbol');
            currencyElements.forEach(element => {
                element.textContent = data.store.currency;
            });
            
            // Update all currency symbols in formatted prices
            document.querySelectorAll('.metric-value span').forEach(element => {
                if (element.id === 'inventoryValue') {
                    const numericValue = element.textContent.replace(/[^0-9,.]/g, '');
                    element.textContent = `${data.store.currency}${numericValue}`;
                }
            });
            
            // Update inventory stats display
            updateInventoryMetrics();
            
            // Update avatar image based on country code
            const avatarImage = document.querySelector('.avatar-image img');
            if (avatarImage) {
                // Set the new avatar image based on the country code
                const avatarPath = `/static/images/avatar-${countryCode.toLowerCase()}.png`;
                // Fallback to default if the specific image doesn't exist
                avatarImage.onerror = () => {
                    avatarImage.src = '/static/images/avatar-default.png';
                };
                avatarImage.src = avatarPath;
            }
            
            // Show notification
            showSuccessNotification(`Store changed to ${data.store.name} in ${data.store.country}`);
            
            // Log for debugging
            console.log(`Store changed to ${data.store.name} (${data.store.country}) with currency ${data.store.currency}`);
        } else {
            showErrorNotification(data.message || 'Failed to change store');
        }
    })
    .catch(error => {
        console.error('Error changing store:', error);
        showErrorNotification('Error changing store');
    });
}

function addChatMessage(container, message, isIncoming) {
    // Remove empty state if present
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) {
        container.removeChild(emptyState);
    }
    
    // Create message element
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message');
    
    if (isIncoming) {
        messageElement.classList.add('message-incoming');
    } else {
        messageElement.classList.add('message-outgoing');
    }
    
    // Add message content with proper formatting
    messageElement.innerHTML = formatMessageText(message);
    
    // Add message to container
    container.appendChild(messageElement);
    
    // Add subtle animation for new messages
    setTimeout(() => {
        messageElement.classList.add('visible');
    }, 10);
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

// Format message text to add links, emojis, and line breaks
function formatMessageText(text) {
    // Convert line breaks to <br>
    text = text.replace(/\n/g, '<br>');
    
    // Make URLs clickable
    text = text.replace(
        /(https?:\/\/[^\s]+)/g, 
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    
    return text;
}

// Loading indicator functions
function showLoadingIndicator(container) {
    const loadingId = `loading-${Date.now()}`;
    const loadingElement = document.createElement('div');
    loadingElement.id = loadingId;
    loadingElement.classList.add('chat-message', 'message-incoming', 'loading');
    loadingElement.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
    
    container.appendChild(loadingElement);
    container.scrollTop = container.scrollHeight;
    
    return loadingId;
}

function removeLoadingIndicator(loadingId) {
    const loadingElement = document.getElementById(loadingId);
    if (loadingElement) {
        loadingElement.remove();
    }
}

// Update inventory metrics with animation
function updateInventoryMetrics() {
    fetch('/api/metrics')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && metricsContainer) {
                // Update metric values
                const { metrics } = data;
                
                const totalItemsEl = document.getElementById('totalItems');
                const lowStockCountEl = document.getElementById('lowStockCount');
                const inventoryValueEl = document.getElementById('inventoryValue');
                const turnoverRateEl = document.getElementById('turnoverRate');
                
                if (totalItemsEl) totalItemsEl.textContent = metrics.total_items;
                if (lowStockCountEl) lowStockCountEl.textContent = metrics.low_stock_count;
                if (inventoryValueEl) {
                    // Use currency symbol from API response if available
                    const currency = metrics.currency_symbol || '₹';
                    inventoryValueEl.textContent = `${currency}${metrics.inventory_value.toLocaleString()}`;
                }
                if (turnoverRateEl) turnoverRateEl.textContent = `${metrics.turnover_rate}x`;
                
                // Add update animation to metrics
                const metricCards = metricsContainer.querySelectorAll('.metric-card');
                metricCards.forEach(card => {
                    card.classList.add('updating');
                    setTimeout(() => {
                        card.classList.remove('updating');
                    }, 1000);
                });
            }
        })
        .catch(error => {
            console.error('Error fetching metrics:', error);
        });
}

// Initialize example chats when empty
function initializeExampleChats() {
    // Only initialize if containers are empty (have empty-state class)
    if (customerChatContainer && customerChatContainer.querySelector('.empty-state')) {
        addChatMessage(customerChatContainer, "Hello, I would like to order some Lotte Chocopie.", false);
        
        // Get store name for more personalized response
        const storeName = document.querySelector('.store-name')?.textContent || 'Lalaji';
        addChatMessage(customerChatContainer, `I have found Lotte Chocopie in stock at ${storeName}. We have 24 packs available at ₹40 each. How many would you like to order?`, true);
    }
    
    if (distributorChatContainer && distributorChatContainer.querySelector('.empty-state')) {
        addChatMessage(distributorChatContainer, "I have a new shipment of rice bags available. Do you need to restock?", false);
        
        // Get store name for more personalized response
        const storeName = document.querySelector('.store-name')?.textContent || 'Lalaji';
        addChatMessage(distributorChatContainer, `Yes, we're running low on rice at ${storeName}. Please send your current price list and available quantities.`, true);
    }
}

// Notifications
function showSuccessNotification(message) {
    const notification = document.createElement('div');
    notification.classList.add('notification', 'success');
    notification.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showErrorNotification(message) {
    const notification = document.createElement('div');
    notification.classList.add('notification', 'error');
    notification.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showProcessingNotification() {
    const notification = document.createElement('div');
    notification.classList.add('notification', 'processing');
    notification.innerHTML = `<i class="fas fa-cog fa-spin"></i> Processing...`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    return notification;
}

// Add dynamic styles
function addDynamicStyles() {
    const style = document.createElement('style');
    style.textContent = `
        /* Message animation */
        .chat-message {
            opacity: 0;
            transform: translateY(10px);
            transition: opacity 0.3s ease-out, transform 0.3s ease-out;
        }
        
        .chat-message.visible {
            opacity: 1;
            transform: translateY(0);
        }
        
        /* Metric card update animation */
        .metric-card.updating {
            animation: metricUpdate 1s ease-out;
        }
        
        @keyframes metricUpdate {
            0% {
                background-color: rgba(79, 70, 229, 0.02);
                box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.3);
            }
            50% {
                background-color: rgba(79, 70, 229, 0.08);
                box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.5);
            }
            100% {
                background-color: transparent;
                box-shadow: var(--shadow-sm);
            }
        }
        
        /* Notification styles */
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            font-weight: 500;
            opacity: 0;
            transform: translateY(-10px);
            transition: all 0.3s ease;
        }
        
        .notification.show {
            opacity: 1;
            transform: translateY(0);
        }
        
        .notification.success {
            background-color: #ecfdf5;
            border-left: 4px solid #10b981;
            color: #047857;
        }
        
        .notification.error {
            background-color: #fef2f2;
            border-left: 4px solid #ef4444;
            color: #b91c1c;
        }
        
        .notification.processing {
            background-color: #eff6ff;
            border-left: 4px solid #3b82f6;
            color: #1d4ed8;
        }
        
        .notification i {
            margin-right: 8px;
        }
        
        /* Flag selector styles */
        .flag-icon {
            margin-right: 8px;
            box-shadow: 0 0 2px rgba(0,0,0,0.2);
        }
        
        .flag-button.active {
            background-color: rgba(79, 70, 229, 0.1);
            font-weight: bold;
        }
    `;
    
    document.head.appendChild(style);
}

// Initialize voice control for dashboard buttons
function initializeVoiceControl() {
    // Set up voice command listeners
    if (window.UltravoxSession && window.uvSession) {
        window.uvSession.addEventListener('transcripts', (e) => {
            const transcripts = e.target._transcripts;
            if (!transcripts || !Array.isArray(transcripts)) return;
            
            // Process only user transcripts
            const userTranscripts = transcripts
                .filter(t => t && t.speaker === "user")
                .map(t => t ? t.text.toLowerCase() : "");
            
            // Process voice commands
            processVoiceCommands(userTranscripts[userTranscripts.length - 1]);
        });
    }
}

// Process voice commands for dashboard actions
function processVoiceCommands(transcript) {
    if (!transcript || !voiceControlActive) return;
    
    // Map commands to dashboard actions
    if (transcript.includes('inventory') || transcript.includes('stock')) {
        navigateTo('/inventory');
        currentDashboardAction = 'inventory';
    } else if (transcript.includes('reports') || transcript.includes('analytics')) {
        navigateTo('/reports');
        currentDashboardAction = 'reports';
    } else if (transcript.includes('settings') || transcript.includes('configuration')) {
        navigateTo('/settings');
        currentDashboardAction = 'settings';
    } else if (transcript.includes('dashboard') || transcript.includes('home')) {
        navigateTo('/');
        currentDashboardAction = 'dashboard';
    }
}

// Helper function to navigate to different sections
function navigateTo(path) {
    const baseUrl = window.location.origin;
    window.location.href = baseUrl + path;
}

// Initialize when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add dynamic CSS effects
    addDynamicStyles();
    
    // Setup tabs if they exist
    const tabEl = document.querySelector('#inventoryTabs');
    if (tabEl) {
        const tabs = new bootstrap.Tab(tabEl);
    }
    
    // Initialize country flag dropdown buttons
    const flagButtons = document.querySelectorAll('.flag-button');
    flagButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const countryCode = this.getAttribute('data-country-code');
            if (countryCode) {
                changeStore(countryCode);
            }
        });
    });

    // Initialize example chats after a short delay
    setTimeout(initializeExampleChats, 1000);
    
    // Initialize metrics on load
    updateInventoryMetrics();
});

// Initialize voice chat component
document.addEventListener('DOMContentLoaded', () => {
    // Initialize voice chat toggle
    const voiceChatToggle = document.querySelector('.voice-chat-toggle');
    if (voiceChatToggle) {
        voiceChatToggle.addEventListener('click', () => {
            const voiceChatPanel = document.querySelector('.voice-chat-panel');
            if (voiceChatPanel) {
                voiceChatPanel.classList.toggle('active');
            }
        });
    }

    // Ensure the call button is properly initialized
    const startCallButton = document.getElementById('startCallButton');
    if (startCallButton) {
        console.log('Initializing start call button...');
        startCallButton.addEventListener('click', startCall);
    }

    // Initialize end call button
    const endCallButton = document.getElementById('endCallButton');
    if (endCallButton) {
        console.log('Initializing end call button...');
        endCallButton.addEventListener('click', endCall);
    }
});

// Function to handle Telegram messages
function handleTelegramMessage(message, isCustomer = true) {
    const container = isCustomer ? customerChatContainer : distributorChatContainer;
    const endpoint = isCustomer ? '/api/customer/message' : '/api/distributor/message';
    
    // Add message to chat
    addChatMessage(container, message, false);
    
    // Show loading indicator
    const loadingId = showLoadingIndicator(container);
    
    // Process message with backend
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            message: message,
            is_telegram: true // This is a Telegram message
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        removeLoadingIndicator(loadingId);
        
        if (data.status === 'success') {
            // Add response to chat
            addChatMessage(container, data.response, true);
        } else {
            addChatMessage(container, "Sorry, there was an error processing your request.", true);
        }
    })
    .catch(error => {
        // Remove loading indicator
        removeLoadingIndicator(loadingId);
        console.error('Error:', error);
        addChatMessage(container, "Sorry, there was an error processing your request.", true);
    });
}
