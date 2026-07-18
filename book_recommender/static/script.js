document.getElementById("chat-toggle").addEventListener("click", function() {
    const chat = document.getElementById("chatbot");
    chat.style.display = chat.style.display === "none" || chat.style.display === "" ? "block" : "none";
});

document.getElementById("chat-input").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        const message = this.value;
        fetch("/chatbot", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById("chatbot-response").innerText = data.response;
        });
        this.value = "";
    }
});

function startVoice() {
    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.lang = 'en-US';
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById("book").value = transcript;
        };
        recognition.start();
    } else {
        alert("Sorry, your browser does not support speech recognition.");
    }
}

function toggleDark() {
    document.body.classList.toggle("dark-mode");
    
}

// ✅ FAVORITES BUTTON: Submit hidden form when "Add to Favorites" is clicked
function addToFavorites(title, authors, thumbnail) {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = "/add_favorite";

    const titleInput = document.createElement("input");
    titleInput.type = "hidden";
    titleInput.name = "title";
    titleInput.value = title;

    const authorInput = document.createElement("input");
    authorInput.type = "hidden";
    authorInput.name = "authors";
    authorInput.value = authors;

    const thumbInput = document.createElement("input");
    thumbInput.type = "hidden";
    thumbInput.name = "thumbnail";
    thumbInput.value = thumbnail;

    form.appendChild(titleInput);
    form.appendChild(authorInput);
    form.appendChild(thumbInput);
    document.body.appendChild(form);
    form.submit();
}
