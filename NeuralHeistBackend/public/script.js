document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const levelSelector = document.getElementById('security-level');

    function appendMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender);
        msgDiv.innerHTML = text.replace(/\n/g, '<br>');
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        return msgDiv;
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        // Display user message
        appendMessage('user', text);
        userInput.value = '';
        userInput.disabled = true;
        sendBtn.disabled = true;

        const level = parseInt(levelSelector.value, 10);
        
        // Show typing indicator
        const typingIndicator = appendMessage('system', '<span class="typing-indicator">[PROCESSING INPUT...]</span>');

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    level: level,
                    message: text
                })
            });

            const data = await response.json();
            chatBox.removeChild(typingIndicator);

            if (!response.ok) {
                appendMessage('system', `ERROR: ${data.detail || 'Connection failed.'}`);
            } else {
                appendMessage('ai', data.response);
            }

        } catch (error) {
            chatBox.removeChild(typingIndicator);
            appendMessage('system', 'ERROR: Mainframe connection lost. Please try again.');
        } finally {
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }

    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Handle level change logic
    levelSelector.addEventListener('change', () => {
        appendMessage('system', `[SECURITY CLEARANCE UPDATED TO LEVEL ${levelSelector.value}]`);
        userInput.focus();
    });
});
