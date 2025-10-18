// script.js

document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('input-box').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

// History fetching logic
const mainContainerWrapper = document.getElementById('main-container-wrapper');
const historyContent = document.getElementById('history-content');
let historyLoaded = false;

// Attach event listener to the wrapper to trigger history load on mouse entry
mainContainerWrapper.addEventListener('mouseenter', fetchHistory);

function fetchHistory() {
    // Only load history if it hasn't been loaded yet in this session
    if (historyLoaded) {
        return;
    }
    
    // Display loading text while fetching
    historyContent.innerHTML = '<p class="loading-text">Loading...</p>';

    // Call the new backend endpoint
    fetch('http://127.0.0.1:5000/history')
        .then(response => response.json())
        .then(history => {
            historyContent.innerHTML = '';
            if (history.length === 0) {
                historyContent.innerHTML = '<p class="loading-text">No chat history found.</p>';
            } else {
                history.forEach(item => {
                    // Create container for each chat exchange
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'history-item';
                    
                    // Format Timestamp
                    const date = new Date(item.timestamp);
                    const timestamp = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

                    // Add user message
                    const userDiv = document.createElement('div');
                    userDiv.className = 'history-user';
                    userDiv.innerText = `You (${timestamp}): ${item.user_message}`;
                    itemDiv.appendChild(userDiv);

                    // Add bot response
                    const botDiv = document.createElement('div');
                    botDiv.className = 'history-bot';
                    botDiv.innerText = `Bot: ${item.bot_response}`;
                    itemDiv.appendChild(botDiv);

                    historyContent.appendChild(itemDiv);
                });
            }
            historyLoaded = true;
        })
        .catch(error => {
            console.error('Error fetching history:', error);
            historyContent.innerHTML = '<p class="loading-text" style="color:red;">Error loading history. Check your MySQL connection and /history endpoint.</p>';
        });
}


function sendMessage() {
    const inputBox = document.getElementById('input-box');
    const chatBox = document.getElementById('chat-box');
    const userMessage = inputBox.value.trim();

    if (userMessage) {
        // Reset historyLoaded flag to reload history after a new message is sent
        historyLoaded = false; 

        // Display user message immediately
        chatBox.innerHTML += `<div class="message user-message">You: ${userMessage}</div>`;
        inputBox.value = '';
        chatBox.scrollTop = chatBox.scrollHeight;

        // Send message to the server
        fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userMessage }),
        })
        .then(response => response.json())
        .then(data => {
            // Create a new container for the bot's message
            const botMessageContainer = document.createElement('div');
            botMessageContainer.className = 'message bot-message';
            botMessageContainer.innerHTML = 'Bot: '; // Add the prefix
            chatBox.appendChild(botMessageContainer);
            
            // Use the typewriter effect for the response
            typewriterEffect(botMessageContainer, data.response);
        })
        .catch(error => {
            console.error('Error:', error);
            // Display an error message in the chat
            const errorContainer = document.createElement('div');
            errorContainer.className = 'message bot-message';
            errorContainer.innerText = 'Bot: Sorry, something went wrong. Could not connect to the server.';
            chatBox.appendChild(errorContainer);
            chatBox.scrollTop = chatBox.scrollHeight;
        });
    }
}

/**
 * Creates a typewriter effect for the bot's response.
 */
function typewriterEffect(element, text, speed = 20) {
    let i = 0;
    const chatBox = document.getElementById('chat-box');

    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            chatBox.scrollTop = chatBox.scrollHeight;
            setTimeout(type, speed);
        }
    }
    type();
}
