// script.js

document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('input-box').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const inputBox = document.getElementById('input-box');
    const chatBox = document.getElementById('chat-box');
    const userMessage = inputBox.value.trim();

    if (userMessage) {
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
 * @param {HTMLElement} element The HTML element to type into.
 * @param {string} text The text to type out.
 * @param {number} speed The typing speed in milliseconds.
 */
function typewriterEffect(element, text, speed = 20) {
    let i = 0;
    const chatBox = document.getElementById('chat-box');

    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            // Keep the chat scrolled to the bottom as text appears
            chatBox.scrollTop = chatBox.scrollHeight;
            setTimeout(type, speed);
        }
    }
    type();
}
