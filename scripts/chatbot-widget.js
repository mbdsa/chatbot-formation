const toggleBtn = document.getElementById("toggle-chat");
const chatWidget = document.getElementById("chat-widget");
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

// Toggle chat widget on click
toggleBtn.addEventListener("click", () => {
    console.log("✅ Clique détecté sur l’avatar !");
    chatWidget.style.display = chatWidget.style.display === "none" ? "flex" : "none";
  });
  

// Envoi du message
sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});

async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  addMessage(message, "user");

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });

  const data = await res.json();
  
  if (data.response) {
    addMessage(data.response, "bot");
  }
  

  userInput.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;
}

function addMessage(text, type) {
  const msg = document.createElement("div");
  msg.className = `bubble ${type}`;
  msg.textContent = text;
  chatBox.appendChild(msg);
}
