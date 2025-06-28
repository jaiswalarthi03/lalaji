// Gemini API Integration
// This file handles integration with the Google Gemini AI model for chat functionality

// Configuration and state
const geminiConfig = {
    isInitialized: false,
    isLoading: false,
    contextLength: 10, // Number of messages to keep for context
    customerContext: [], // Store conversation history for customer
    supplierContext: [], // Store conversation history for supplier
};

// Initialize Gemini integration
function initGeminiAPI() {
    if (geminiConfig.isInitialized) return;
    
    console.log("Initializing Gemini API integration");
    
    // Set initialization flag
    geminiConfig.isInitialized = true;
    
    // Add event listeners to replace the default ones in script.js
    overrideDefaultChatHandlers();
    
    // Load inventory data for context
    loadInventoryForContext();
}

// Override default chat handlers
function overrideDefaultChatHandlers() {
    const customerSendBtn = document.getElementById('customerSendBtn');
    const customerChatInput = document.getElementById('customerChatInput');
    const supplierSendBtn = document.getElementById('supplierSendBtn');
    const supplierChatInput = document.getElementById('supplierChatInput');
    
    if (customerSendBtn) {
        customerSendBtn.removeEventListener('click', window.sendCustomerMessage);
        customerSendBtn.addEventListener('click', () => processCustomerMessage());
    }
    
    if (customerChatInput) {
        customerChatInput.removeEventListener('keypress', window.customerInputKeyPress);
        customerChatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                processCustomerMessage();
            }
        });
    }
    
    if (supplierSendBtn) {
        supplierSendBtn.removeEventListener('click', window.sendSupplierMessage);
        supplierSendBtn.addEventListener('click', () => processSupplierMessage());
    }
    
    if (supplierChatInput) {
        supplierChatInput.removeEventListener('keypress', window.supplierInputKeyPress);
        supplierChatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                processSupplierMessage();
            }
        });
    }
}

// Load inventory data to provide context for the AI
function loadInventoryForContext() {
    fetch('/api/inventory')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log("Loaded inventory data for AI context");
            }
        })
        .catch(error => {
            console.error('Error loading inventory data for context:', error);
        });
}

// Process customer message
function processCustomerMessage() {
    const customerChatInput = document.getElementById('customerChatInput');
    const customerChatContainer = document.getElementById('customerChatContainer');
    
    const message = customerChatInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(customerChatContainer, message, false);
    customerChatInput.value = '';
    
    // Add to context
    geminiConfig.customerContext.push({
        role: "user",
        content: message
    });
    
    // Trim context if needed
    if (geminiConfig.customerContext.length > geminiConfig.contextLength * 2) {
        geminiConfig.customerContext = geminiConfig.customerContext.slice(-geminiConfig.contextLength);
    }
    
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
            context: geminiConfig.customerContext
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        removeLoadingIndicator(loadingId);
        
        if (data.status === 'success') {
            // Add response to chat
            addChatMessage(customerChatContainer, data.response, true);
            
            // Add to context
            geminiConfig.customerContext.push({
                role: "assistant",
                content: data.response
            });
            
            // Activate avatar animation
            activateAvatar();
            
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

// Process supplier message
function processSupplierMessage() {
    const supplierChatInput = document.getElementById('supplierChatInput');
    const supplierChatContainer = document.getElementById('supplierChatContainer');
    
    const message = supplierChatInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(supplierChatContainer, message, false);
    supplierChatInput.value = '';
    
    // Add to context
    geminiConfig.supplierContext.push({
        role: "user",
        content: message
    });
    
    // Trim context if needed
    if (geminiConfig.supplierContext.length > geminiConfig.contextLength * 2) {
        geminiConfig.supplierContext = geminiConfig.supplierContext.slice(-geminiConfig.contextLength);
    }
    
    // Show loading indicator
    const loadingId = showLoadingIndicator(supplierChatContainer);
    
    // Process message with backend
    fetch('/api/supplier/message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            message: message,
            context: geminiConfig.supplierContext
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        removeLoadingIndicator(loadingId);
        
        if (data.status === 'success') {
            // Add response to chat
            addChatMessage(supplierChatContainer, data.response, true);
            
            // Add to context
            geminiConfig.supplierContext.push({
                role: "assistant",
                content: data.response
            });
            
            // Activate avatar animation
            activateAvatar();
            
            // Update metrics if available
            updateInventoryMetrics();
        } else {
            addChatMessage(supplierChatContainer, "Sorry, there was an error processing your request.", true);
        }
    })
    .catch(error => {
        // Remove loading indicator
        removeLoadingIndicator(loadingId);
        console.error('Error:', error);
        addChatMessage(supplierChatContainer, "Sorry, there was an error processing your request.", true);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Gemini API
    initGeminiAPI();
});
