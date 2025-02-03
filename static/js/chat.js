const ws = new WebSocket('ws://' + window.location.host + '/ws');
const messageBox = document.getElementById('message-box');
const messageInput = document.getElementById('message-input');

ws.onmessage = function(event) {
    const message = document.createElement('div');
    message.textContent = event.data;
    messageBox.appendChild(message);
    messageBox.scrollTop = messageBox.scrollHeight;
};

function sendMessage() {
    const message = messageInput.value;
    if (message.trim()) {
        ws.send(message);
        messageInput.value = '';
    }
}

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});