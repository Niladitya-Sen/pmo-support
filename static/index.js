let messages = {};
let count = 0;
let keys = ["email", "otp", "message"];

function scrollDown() {
    const chatBox = document.getElementById("chatBox");
    chatBox.scrollTop = chatBox.scrollHeight;
}

function setReply(message) {
    const chatBox = document.getElementById("chatBox");
    chatBox.innerHTML += `<p class="chatBubble bot">${message}</p>`;
    scrollDown();
}

async function getReply(message) {
    messages = {
        ...messages,
        [keys[count]]: message
    };

    const response = await fetch('http://127.0.0.1:5000/support/api/chatbot', {
        method: 'POST',
        body: JSON.stringify(messages),
        headers: {
            'Content-Type': 'application/json'
        }
    });

    const data = await response.json();

    if (data.status === 'success') {
        count++;
    }

    if (data.message) {
        if (typeof data.message === 'object') {
            let m = "";
            for (const msg of data.message) {
                m += msg + "<br>";
            }
            setReply(m);
        } else {
            setReply(data.message);
        }
        if (messages.message) {
            setReply('Do you want to enter another ticket?');
            messages = {
                ...messages,
                message: null
            };
            count = 2;
        }
    }
}


document.getElementById("chatInputForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const message = document.getElementById("message").value;
    if (!message) return;
    const chatBox = document.getElementById("chatBox");
    chatBox.innerHTML += `<p class="chatBubble">${message}</p>`;
    getReply(message);
    document.getElementById("message").value = "";
    scrollDown();
});

window.onload = () => {
    setReply('Please enter your email id');
}
