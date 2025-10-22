document.getElementById("send-button").addEventListener("click", sendMessage);
document.getElementById("input-box").addEventListener("keypress", function (event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});

const mainContainerWrapper = document.getElementById("main-container-wrapper");
const historyContent = document.getElementById("history-content");
let historyLoaded = false;

mainContainerWrapper.addEventListener("mouseenter", fetchHistory);

function fetchHistory() {
  if (historyLoaded) {
    return;
  }

  historyContent.innerHTML = '<p class="loading-text">Loading...</p>';

  fetch("http://127.0.0.1:5000/history")
    .then((response) => response.json())
    .then((history) => {
      historyContent.innerHTML = "";
      if (history.length === 0) {
        historyContent.innerHTML = '<p class="loading-text">No chat history found.</p>';
      } else {
        history.forEach((item) => {
          const itemDiv = document.createElement("div");
          itemDiv.className = "history-item";

          // CRITICAL CHANGE: Use the 'display_time' field sent by the server (which contains IST)
          const timestamp = item.display_time;

          const userDiv = document.createElement("div");
          userDiv.className = "history-user";
          userDiv.innerText = `You (${timestamp.replace("(", "").replace(")", "")}): ${item.user_message}`;
          itemDiv.appendChild(userDiv);

          const botDiv = document.createElement("div");
          botDiv.className = "history-bot";
          botDiv.innerText = `Bot: ${item.bot_response}`;
          itemDiv.appendChild(botDiv);

          historyContent.appendChild(itemDiv);
        });
      }
      historyLoaded = true;
    })
    .catch((error) => {
      console.error("Error fetching history:", error);
      historyContent.innerHTML = '<p class="loading-text" style="color:red;">Error loading history. Check your MySQL connection and /history endpoint.</p>';
    });
}

function sendMessage() {
  const inputBox = document.getElementById("input-box");
  const chatBox = document.getElementById("chat-box");
  const userMessage = inputBox.value.trim();

  if (userMessage) {
    historyLoaded = false;

    chatBox.innerHTML += `<div class="message user-message">You: ${userMessage}</div>`;
    inputBox.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: userMessage }),
    })
      .then((response) => response.json())
      .then((data) => {
        const botMessageContainer = document.createElement("div");
        botMessageContainer.className = "message bot-message";
        botMessageContainer.innerHTML = "Luna: ";
        chatBox.appendChild(botMessageContainer);

        typewriterEffect(botMessageContainer, data.response);
      })
      .catch((error) => {
        console.error("Error:", error);
        const errorContainer = document.createElement("div");
        errorContainer.className = "message bot-message";
        errorContainer.innerText = "Luna: Sorry, something went wrong. Could not connect to the server.";
        chatBox.appendChild(errorContainer);
        chatBox.scrollTop = chatBox.scrollHeight;
      });
  }
}

function typewriterEffect(element, text, speed = 20) {
  let i = 0;
  const chatBox = document.getElementById("chat-box");

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
