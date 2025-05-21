const orb = document.getElementById("orb");
const subtitleBox = document.getElementById("subtitles");
const stopButton = document.getElementById("stop-button");
let currentAudio = null;

function startListening() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        askButton.click();
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        setOrbState("idle");
    };

    recognition.start();
    setOrbState("listening");
}

function setOrbState(state) {
    if (!orb) return;
    orb.classList.remove("orb-idle", "orb-thinking", "orb-speaking", "orb-listening");
    orb.classList.add("orb-" + state);
}

async function speak(text) {
    try {
        setOrbState("thinking");
        subtitleBox.textContent = text;
        const response = await fetch("/speak", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });
        const data = await response.json();
        if (data.audio) {
            setOrbState("speaking");
            if (currentAudio) currentAudio.pause();
            currentAudio = new Audio(data.audio);
            currentAudio.play();
            currentAudio.onended = () => {
                setOrbState("idle");
                startListening();
            };
        } else {
            setOrbState("speaking");
            setTimeout(() => {
                setOrbState("idle");
                startListening();
            }, 3000);
        }
    } catch (err) {
        console.error("Error:", err);
        setOrbState("idle");
    }
}

stopButton.addEventListener("click", () => {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    subtitleBox.textContent = "";
    setOrbState("idle");
});

const heyLuminaBtn = document.getElementById("hey-lumina-button");
if (heyLuminaBtn) {
    heyLuminaBtn.addEventListener("click", async () => {
        await speak("Let me ask a few quick questions to match you to the right tier...");
        setTimeout(() => {
            speak("Do you already have a business, or are you just getting started?");
        }, 3500);
    });
}

const askButton = document.getElementById("ask-lumina");
const userInput = document.getElementById("user-input");

if (askButton && userInput) {
    askButton.addEventListener("click", async () => {
        const question = userInput.value.trim();
        if (question.length > 0) {
            try {
                const response = await fetch("/ask", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question }),
                });
                const data = await response.json();
                if (data.reply) {
                    speak(data.reply);
                    showCTA(data.cta);
                }
            } catch (err) {
                console.error("Error:", err);
            }
            userInput.value = "";
        }
    });

    userInput.add
