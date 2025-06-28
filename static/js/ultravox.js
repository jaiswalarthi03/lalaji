/**
 * Ultravox Voice Chat Application
 * Handles the client-side functionality for the voice chat application.
 */

// Global variables
let uvSession = null;
let callActive = false;
const DEFAULT_VOICE = "Mark";
const DEFAULT_LANGUAGE = "english"; // Default language
const ULTRAVOX_API_KEY = 'your-ultravox-api-key-here';

// Supported languages with their API configurations
const SUPPORTED_LANGUAGES = {
    "english": { voice: "Mark", apiKey: null },
    "hindi": { voice: "your-hindi-voice-id-here", apiKey: "your-hindi-voice-id-here" },
    "tamil": { voice: "your-tamil-voice-id-here", apiKey: "your-tamil-voice-id-here" }
};

// DOM elements
let startCallButton;
let endCallButton;
let callStatusValue;
let callIdValue;
let transcriptContent;
let loadingSpinner;
let voiceChatPanel;
let languageSelect;

// Initialize the application when Ultravox is ready
window.addEventListener('ultravox_ready', () => {
    console.log('Ultravox is ready, initializing voice chat...');
    initializeVoiceChat();
});

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM content loaded - initializing ultravox.js");
    
    // Get DOM elements
    startCallButton = document.getElementById('startCallButton');
    endCallButton = document.getElementById('endCallButton');
    callStatusValue = document.getElementById('callStatusValue');
    callIdValue = document.getElementById('callIdValue');
    transcriptContent = document.getElementById('transcriptContent');
    loadingSpinner = document.getElementById('loadingSpinner');
    voiceChatPanel = document.querySelector('.voice-chat-panel');
    languageSelect = document.getElementById('language-select');

    // Check if we're in the Indian store
    const storeFlag = document.querySelector('.flag-dropdown .flag-icon-in');
    const currentFlagIcon = document.getElementById('currentFlagIcon');
    console.log("Indian store flag detected:", storeFlag);
    console.log("Current flag icon:", currentFlagIcon);
    
    // Check if we're in the Indian store (either active or as current flag)
    const isIndianStore = storeFlag && storeFlag.classList.contains('active') || 
                          (currentFlagIcon && currentFlagIcon.classList.contains('flag-icon-in'));
    
    console.log("Is Indian store:", isIndianStore);
    
    // Create language selector if we're in the Indian store and it doesn't exist yet
    if (isIndianStore && !languageSelect) {
        console.log("Creating language selector for Indian store");
        createLanguageSelector();
    }

    // Setup event listeners
    setupEventListeners();
    
    // Also listen for store changes to add/remove language selector
    document.querySelectorAll('.flag-button').forEach(button => {
        button.addEventListener('click', function() {
            setTimeout(() => {
                const isIndianStoreNow = document.getElementById('currentFlagIcon').classList.contains('flag-icon-in');
                console.log("Store changed, Indian store now:", isIndianStoreNow);
                
                if (isIndianStoreNow && !document.getElementById('language-select')) {
                    console.log("Creating language selector after store change to India");
                    createLanguageSelector();
                } else if (!isIndianStoreNow && document.getElementById('language-select')) {
                    console.log("Removing language selector after store change from India");
                    const container = document.querySelector('.language-selector-container');
                    if (container) container.remove();
                    languageSelect = null;
                }
            }, 500); // Small delay to ensure DOM is updated
        });
    });
});

function initializeVoiceChat() {
    try {
        if (!window.UltravoxSession) {
            throw new Error('Ultravox is not properly initialized');
        }

        // Create Ultravox session with API key
        const debugMessages = new Set(["debug"]);
        uvSession = new window.UltravoxSession({ experimentalMessages: debugMessages, apiKey: ULTRAVOX_API_KEY });
        setupUltravoxEventListeners();
        
        // Enable start button
        if (startCallButton) {
            startCallButton.disabled = false;
            startCallButton.title = 'Start voice call';
        }
        
        console.log('Voice chat initialized successfully');
    } catch (error) {
        console.error('Failed to initialize voice chat:', error);
        showErrorMessage('Could not initialize voice assistant. Please refresh the page.');
    }
}

/**
 * Toggle the voice chat panel visibility
 */
function toggleVoiceChat() {
    if (voiceChatPanel) {
        voiceChatPanel.classList.toggle('active');
    }
}

/**
 * Set up event listeners for UI elements
 */
function setupEventListeners() {
    if (startCallButton) {
        startCallButton.addEventListener('click', startCall);
    }
    if (endCallButton) {
        endCallButton.addEventListener('click', endCall);
    }
}

/**
 * Set up event listeners for the Ultravox session
 */
function setupUltravoxEventListeners() {
    if (!uvSession) return;
    
    // Status event listener
    uvSession.addEventListener('status', (e) => {
        updateCallStatus(e.target._status);
    });
    
    // Transcripts event listener
    uvSession.addEventListener('transcripts', (e) => {
        updateTranscript(e.target._transcripts);
    });
    
    // Debug messages event listener
    uvSession.addEventListener('experimental_message', (msg) => {
        console.log('Debug: ', JSON.stringify(msg));
    });
}

/**
 * Start a new call
 */
async function startCall() {
    if (callActive) return;
    try {
        // Hide any previous error messages
        const errorContainer = document.getElementById('errorContainer');
        if (errorContainer) errorContainer.style.display = 'none';

        // Show loading state
        startCallButton.disabled = true;
        if (loadingSpinner) loadingSpinner.classList.remove('hidden');
        updateCallStatus && updateCallStatus('Initializing');

        // Get selected voice and language
        const voiceSelect = document.getElementById('voice-select');
        const selectedVoice = voiceSelect ? voiceSelect.value : DEFAULT_VOICE;
        
        const selectedLanguage = languageSelect ? languageSelect.value : DEFAULT_LANGUAGE;
        const languageConfig = SUPPORTED_LANGUAGES[selectedLanguage] || SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE];
        
        // Get store name from the page to use as bot name
        const storeName = document.getElementById('storeName')?.textContent || 'Your Store';
        console.log(`Starting call with voice: ${selectedVoice}, language: ${selectedLanguage}, bot name: ${storeName}`);
        
        // Initialize uvSession if needed
        if (!uvSession) {
            if (window.UltravoxSession) {
                const debugMessages = new Set(["debug"]);
                uvSession = new window.UltravoxSession({ experimentalMessages: debugMessages, apiKey: ULTRAVOX_API_KEY });
                setupUltravoxEventListeners && setupUltravoxEventListeners();
            } else {
                throw new Error("UltravoxSession is not available. Please refresh the page.");
            }
        }

        // Request a new call from the server
        const response = await fetch('/start_call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-API-Key': ULTRAVOX_API_KEY },
            body: JSON.stringify({ 
                voice: selectedVoice,
                language: selectedLanguage
            })
        });
        if (!response.ok) {
            let errorMessage = `Error ${response.status}: ${response.statusText}`;
            try {
                const errorData = await response.json();
                if (errorData.error) errorMessage = errorData.error;
            } catch {}
            throw new Error(errorMessage);
        }
        const callDetails = await response.json();
        if (callIdValue) callIdValue.textContent = callDetails.callId || 'Connected';
        if (uvSession) {
            await uvSession.joinCall(callDetails.joinUrl);
            callActive = true;
            if (startCallButton) startCallButton.classList.add('hidden');
            if (endCallButton) endCallButton.classList.remove('hidden');
            if (transcriptContent) transcriptContent.textContent = '';
            updateCallStatus && updateCallStatus('Connected');
        } else {
            throw new Error('Ultravox session not initialized');
        }
    } catch (error) {
        console.error('Error starting call:', error);
        showErrorMessage && showErrorMessage(error.message || 'Failed to start call', 'error');
        updateCallStatus && updateCallStatus('Error');
    } finally {
        if (loadingSpinner) loadingSpinner.classList.add('hidden');
        if (startCallButton) startCallButton.disabled = false;
    }
}

/**
 * End the current call
 */
async function endCall() {
    if (!callActive) return;
    
    try {
        // Show loading state
        endCallButton.disabled = true;
        loadingSpinner?.classList.remove('hidden');
        
        // Leave the call
        if (uvSession) {
            await uvSession.leaveCall();
            callActive = false;
            
            // Update UI states
            startCallButton.classList.remove('hidden');
            endCallButton.classList.add('hidden');
            updateCallStatus('Disconnected');
            if (callIdValue) callIdValue.textContent = 'Not connected';
        }
    } catch (error) {
        console.error('Error ending call:', error);
        showErrorMessage('Failed to end call', 'error');
    } finally {
        // Hide loading state
        loadingSpinner?.classList.add('hidden');
        endCallButton.disabled = false;
    }
}

/**
 * Update the call status display
 */
function updateCallStatus(status) {
    if (!callStatusValue) return;
    
    callStatusValue.textContent = status;
    callStatusValue.className = 'status-value';
    
    switch (status.toLowerCase()) {
        case 'connecting':
            callStatusValue.classList.add('status-connecting');
            break;
        case 'connected':
            callStatusValue.classList.add('status-connected');
            break;
        case 'disconnected':
        case 'error':
            callStatusValue.classList.add('status-disconnected');
            break;
        default:
            callStatusValue.classList.add('status-waiting');
    }
}

/**
 * Update the transcript display
 */
function updateTranscript(transcripts) {
    if (!transcripts || !Array.isArray(transcripts) || !transcriptContent) return;
    
    // Filter out user messages and empty transcripts
    const assistantTranscripts = transcripts
        .filter(t => t && t.speaker !== "user")
        .map(t => t ? t.text : "")
        .join("\n");
    
    transcriptContent.textContent = assistantTranscripts || 'Waiting for response...';
    transcriptContent.scrollTop = transcriptContent.scrollHeight;
}

/**
 * Display an error message to the user
 */
function showErrorMessage(message, type = 'error') {
    // Create or get error element
    let errorContainer = document.getElementById('errorContainer');
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.id = 'errorContainer';
        errorContainer.className = 'error-container';
        
        // Add it after call-control section
        const callControlSection = document.querySelector('.call-control');
        if (callControlSection) {
            callControlSection.parentNode.insertBefore(errorContainer, callControlSection.nextSibling);
        }
    }
    
    // Set error class based on type
    errorContainer.className = `error-container error-${type}`;
    
    // Set error message with icon
    errorContainer.innerHTML = `
        <div class="error-icon">⚠️</div>
        <div class="error-message">${message}</div>
        <button class="error-dismiss" onclick="this.parentElement.style.display='none'">×</button>
    `;
    
    errorContainer.style.display = 'flex';
}

/**
 * Create language selector dropdown
 */
function createLanguageSelector() {
    console.log("Attempting to create language selector dropdown");
    
    // For Indian store, insert the language selector in the voice chat panel
    const voiceSelection = document.querySelector('.voice-selection');
    console.log("Voice selection container:", voiceSelection);
    
    if (!voiceSelection) {
        console.error("No voice selection container found. Cannot create language selector.");
        return;
    }
    
    // Create language selector container
    const languageContainer = document.createElement('div');
    languageContainer.className = 'language-selector-container mb-3';
    
    // Create language selector
    languageSelect = document.createElement('select');
    languageSelect.id = 'language-select';
    languageSelect.className = 'language-select form-select';
    
    // Add language options
    for (const [langCode, langData] of Object.entries(SUPPORTED_LANGUAGES)) {
        const option = document.createElement('option');
        option.value = langCode;
        option.textContent = langCode.charAt(0).toUpperCase() + langCode.slice(1);
        if (langCode === DEFAULT_LANGUAGE) {
            option.selected = true;
        }
        languageSelect.appendChild(option);
        console.log(`Added language option: ${langCode}`);
    }
    
    // Add label
    const label = document.createElement('label');
    label.htmlFor = 'language-select';
    label.className = 'form-label';
    label.textContent = 'Select Language:';
    
    // Add elements to container
    languageContainer.appendChild(label);
    languageContainer.appendChild(languageSelect);
    
    // Insert after voice selection
    voiceSelection.after(languageContainer);
    console.log("Language selector added after voice selection");
    
    // Add event listener for language change
    languageSelect.addEventListener('change', onLanguageChange);
}

/**
 * Handle language change event
 */
function onLanguageChange(event) {
    const selectedLanguage = event.target.value;
    const languageConfig = SUPPORTED_LANGUAGES[selectedLanguage];
    
    console.log(`Language changed to: ${selectedLanguage}`);
    
    // If a call is active, end it first
    if (callActive) {
        endCall().then(() => {
            // After the call ends, update the UI to reflect the new language
            updateVoiceSelectionForLanguage(selectedLanguage);
        });
    } else {
        // Update UI immediately if no call is active
        updateVoiceSelectionForLanguage(selectedLanguage);
    }
}

/**
 * Update voice selection based on selected language
 */
function updateVoiceSelectionForLanguage(language) {
    const languageConfig = SUPPORTED_LANGUAGES[language] || SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE];
    
    // Update voice selection if available
    const voiceSelect = document.getElementById('voice-select');
    if (voiceSelect && languageConfig && languageConfig.voice) {
        // Find the option with matching value
        const options = voiceSelect.options;
        for (let i = 0; i < options.length; i++) {
            if (options[i].value === languageConfig.voice) {
                voiceSelect.selectedIndex = i;
                break;
            }
        }
    }
}