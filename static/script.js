document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");

    // Function to add a new message to the chat box
    function addMessage(message, isReceived) {
        const messageClass = isReceived ? "received" : "sent";
        const div = document.createElement("div");
        div.classList.add("chat-message", messageClass);
        div.innerHTML = `<p class='display-message'>${message}</p>`;
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Function to simulate bot typing indicator
    function showTypingIndicator() {
        const typingIndicator = document.createElement("div");
        //typingIndicator.classList.add("chat-message", "received");
        typingIndicator.innerHTML = `<div class="typing-indicator">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>`;
        chatBox.appendChild(typingIndicator);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Function to handle user input and send it to the server
    function handleUserInput() {
        const message = userInput.value.trim();
        if (message !== "") {
            addMessage(message, false);
            userInput.value = ""; // Clear input field

            // Show typing indicator
            showTypingIndicator();

            //Send message to server
            fetch("http://127.0.0.1:5000/query", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ question: message })
            })
                .then(response => response.json())
                .then(data => {
                    // Remove typing indicator
                    document.querySelector(".typing-indicator").remove();

                    // Process server response
                    addMessage(data["answer"], true);
                })
                .catch(error => {
                    console.error("Error:", error);
                    document.querySelector(".typing-indicator").remove();
                    addMessage("An error occurred. Please try again later.", true);
                });
        }
    }

    // Event listener for sending messages
    sendBtn.addEventListener("click", handleUserInput);

    // Simulate initial message after a short delay
    setTimeout(() => {
        const initialMessage = `Hello! I’m HeyRoo, your friendly chatbot assistant. I’m an AI created to help answer questions related to the University of Missouri-Kansas City (UMKC). Please feel free to ask me anything about the university, and I’ll do my best to provide accurate information.`;
        addMessage(initialMessage, true);

        const infoMessage = `However, I’m still under development, so there may be times when my responses are inaccurate or incomplete. If you notice any errors or have feedback, please let my developers know so they can continue improving me. I’m excited to assist you with your UMKC-related queries! How can I help you today?`;
        // addMessage(infoMessage, true);
    }, 1000);
});