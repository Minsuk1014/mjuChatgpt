document.getElementById("send-btn").addEventListener("click", function() {
    const userMessage = document.getElementById("user-input").value;
    if (userMessage.trim() === "") return;

    const chatLog = document.getElementById("chat-log");
    const userDiv = document.createElement("div");
    userDiv.classList.add("user-message");
    userDiv.textContent = userMessage;
    chatLog.appendChild(userDiv);

    // 서버로 메시지 전송
    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userMessage }),
    })
    .then(response => response.json())
    .then(data => {
        const botDiv = document.createElement("div");
        botDiv.classList.add("bot-message");
        botDiv.textContent = data.reply;
        chatLog.appendChild(botDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
    });

    document.getElementById("user-input").value = "";
});
