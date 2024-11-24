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
        chatBox.innerHTML += `<div class="message user-message">You: ${userMessage}</div>`;
        inputBox.value = '';

        fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userMessage }),
        })
        .then(response => response.json())
        .then(data => {
            chatBox.innerHTML += `<div class="message bot-message">Bot: ${data.response}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;  // Scroll to the bottom
        })
        .catch(error => console.error('Error:', error));
    }
}

