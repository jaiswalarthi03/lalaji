document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".load-chat").forEach(el => {
        el.addEventListener("click", function (e) {
            e.preventDefault();
            console.log("User clicked");

            const customerId = this.dataset.customerId;
            const distributorId = this.dataset.distributorId;

            if (customerId) {
                fetch(`/customer/${customerId}`)
                    .then(response => response.text())
                    .then(html => {
                        document.getElementById("customer-list").style.display = "none";
                        const chatDiv = document.getElementById("customer-chat");
                        chatDiv.innerHTML = html;
                        chatDiv.style.display = "block";
                        window.currentCustomerId = customerId;
                        setupCustomerSend();
                    });
            } else if (distributorId) {
                fetch(`/distributor/${distributorId}`)
                    .then(response => response.text())
                    .then(html => {
                        document.getElementById("distributor-list").style.display = "none";
                        const chatDiv = document.getElementById("distributor-chat");
                        chatDiv.innerHTML = html;
                        chatDiv.style.display = "block";
                        window.currentDistributorId = distributorId;
                        setupDistributorSend();
                    });
            }
        });
    });
});

// Back button handlers
// These should be present in the chat HTML as <i class="fas fa-arrow-left" id="backToCustomerList"></i> etc.
document.addEventListener("click", function (e) {
    if (e.target && e.target.id === "backToCustomerList") {
        document.getElementById("customer-chat").style.display = "none";
        document.getElementById("customer-list").style.display = "block";
    }
    if (e.target && e.target.id === "backToDistributorList") {
        document.getElementById("distributor-chat").style.display = "none";
        document.getElementById("distributor-list").style.display = "block";
    }
});

// Customer send message handler
function setupCustomerSend() {
    const sendBtn = document.getElementById("customerSendBtn");
    const input = document.getElementById("customerChatInput");
    if (!sendBtn || !input) return;
    
    sendBtn.onclick = function () {
        const message = input.value.trim();
        if (!message || !window.currentCustomerId) return;
        
        // Add user message to chat immediately
        const chatContainer = document.getElementById("customerChatContainer");
        addUserMessage(chatContainer, message);
        input.value = '';
        
        // Show typing indicator
        showTypingIndicator(chatContainer);
        
        // Send to new conversational API
        fetch(`/api/customer/${window.currentCustomerId}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            hideTypingIndicator(chatContainer);
            
            if (data.status === 'success') {
                // Add bot response
                addBotMessage(chatContainer, data.response, data.order_processed);
                
                // Handle conversation ending
                if (data.conversation_ended) {
                    input.disabled = true;
                    sendBtn.disabled = true;
                    input.placeholder = "Conversation ended";
                    
                    // Show restart option after delay
                    setTimeout(() => {
                        const restartDiv = document.createElement('div');
                        restartDiv.className = 'bot-msg';
                        restartDiv.innerHTML = `
                            <div class="msg-bubble" style="text-align: center;">
                                <button onclick="restartConversation()" class="btn btn-sm btn-primary">
                                    Start New Conversation
                                </button>
                            </div>
                        `;
                        chatContainer.appendChild(restartDiv);
                        scrollChatToBottom("customerChatContainer");
                    }, 2000);
                }
            } else {
                addBotMessage(chatContainer, "Sorry, I encountered an error. Please try again.", false);
            }
            
            scrollChatToBottom("customerChatContainer");
        })
        .catch(error => { 
            hideTypingIndicator(chatContainer);
            addBotMessage(chatContainer, "Sorry, I'm having trouble connecting. Please try again.", false);
            console.error('Error:', error); 
        });
    };
    
    input.onkeypress = function (e) {
        if (e.key === 'Enter') sendBtn.onclick();
    };
}

// Helper functions for chat messages
function addUserMessage(container, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'user-msg';
    messageDiv.innerHTML = `<div class="msg-bubble">${message}</div>`;
    container.appendChild(messageDiv);
}

function addBotMessage(container, message, isOrderConfirmation = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'bot-msg';
    
    // Check if the message contains HTML tags
    if (message.includes('<div') || message.includes('<span') || message.includes('<h')) {
        // It's HTML content, use it directly
        const bubbleClass = isOrderConfirmation ? 'msg-bubble order-confirmation' : 'msg-bubble';
        messageDiv.innerHTML = `<div class="${bubbleClass}">${message}</div>`;
    } else {
        // Handle markdown-like formatting for plain text
        message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        message = message.replace(/\n/g, '<br>');
        
        const bubbleClass = isOrderConfirmation ? 'msg-bubble order-confirmation' : 'msg-bubble';
        messageDiv.innerHTML = `<div class="${bubbleClass}">${message}</div>`;
    }
    
    container.appendChild(messageDiv);
}

function showTypingIndicator(container) {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'bot-msg typing-indicator';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = '<span></span><span></span><span></span>';
    container.appendChild(typingDiv);
}

function hideTypingIndicator(container) {
    const typingIndicator = container.querySelector('#typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Restart conversation function
window.restartConversation = function() {
    const chatContainer = document.getElementById("customerChatContainer");
    const input = document.getElementById("customerChatInput");
    const sendBtn = document.getElementById("customerSendBtn");
    
    // Clear chat container
    chatContainer.innerHTML = '';
    
    // Re-enable input
    input.disabled = false;
    sendBtn.disabled = false;
    input.placeholder = "Type a message...";
    
    // Send restart message to get welcome
    if (window.currentCustomerId) {
        fetch(`/api/customer/${window.currentCustomerId}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: "restart" })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                addBotMessage(chatContainer, data.response);
                scrollChatToBottom("customerChatContainer");
            }
        });
    }
}

// Distributor send message handler
function setupDistributorSend() {
    const sendBtn = document.getElementById("distributorSendBtn");
    const input = document.getElementById("distributorChatInput");
    if (!sendBtn || !input) return;
    
    sendBtn.onclick = function () {
        const message = input.value.trim();
        if (!message || !window.currentDistributorId) return;
        
        // Add user message to chat immediately
        const chatContainer = document.getElementById("distributorChatContainer");
        addUserMessage(chatContainer, message);
        input.value = '';
        
        // Show typing indicator
        showTypingIndicator(chatContainer);
        
        // Send to new conversational API
        fetch(`/api/distributor/${window.currentDistributorId}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            hideTypingIndicator(chatContainer);
            
            if (data.status === 'success') {
                // Add bot response
                addBotMessage(chatContainer, data.response, data.restock_processed);
                
                // Handle conversation ending
                if (data.conversation_ended) {
                    input.disabled = true;
                    sendBtn.disabled = true;
                    input.placeholder = "Conversation ended";
                    
                    // Show restart option after delay
                    setTimeout(() => {
                        const restartDiv = document.createElement('div');
                        restartDiv.className = 'bot-msg';
                        restartDiv.innerHTML = `
                            <div class="msg-bubble" style="text-align: center;">
                                <button onclick="restartDistributorConversation()" class="btn btn-sm btn-success">
                                    Start New Conversation
                                </button>
                            </div>
                        `;
                        chatContainer.appendChild(restartDiv);
                        scrollChatToBottom("distributorChatContainer");
                    }, 2000);
                }
            } else {
                addBotMessage(chatContainer, "Sorry, I encountered an error. Please try again.", false);
            }
            
            scrollChatToBottom("distributorChatContainer");
        })
        .catch(error => { 
            hideTypingIndicator(chatContainer);
            addBotMessage(chatContainer, "Sorry, I'm having trouble connecting. Please try again.", false);
            console.error('Error:', error); 
        });
    };
    
    input.onkeypress = function (e) {
        if (e.key === 'Enter') sendBtn.onclick();
    };
}

// Restart distributor conversation function
window.restartDistributorConversation = function() {
    const chatContainer = document.getElementById("distributorChatContainer");
    const input = document.getElementById("distributorChatInput");
    const sendBtn = document.getElementById("distributorSendBtn");
    
    // Clear chat container
    chatContainer.innerHTML = '';
    
    // Re-enable input
    input.disabled = false;
    sendBtn.disabled = false;
    input.placeholder = "Type a message...";
    
    // Send restart message to get welcome
    if (window.currentDistributorId) {
        fetch(`/api/distributor/${window.currentDistributorId}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: "restart" })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                addBotMessage(chatContainer, data.response);
                scrollChatToBottom("distributorChatContainer");
            }
        });
    }
}

function scrollChatToBottom(containerId) {
    const chatBox = document.getElementById(containerId);
    if (!chatBox) return;

    setTimeout(() => {
        requestAnimationFrame(() => {
            chatBox.scrollTop = chatBox.scrollHeight;
        });
    }, 50);
}