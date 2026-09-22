const controlButtons = document.querySelectorAll(".toggle-button");
const updatedTime = document.querySelector("#updated-time");
const sendReadingButton = document.querySelector("#send-reading-button");
const sendStatus = document.querySelector("#send-status");

function showUpdateTime() {
    updatedTime.textContent = new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
    });
}

controlButtons.forEach((button) => {
    button.addEventListener("click", async () => {
        const isOn = button.getAttribute("aria-pressed") === "true";
        const enabled = !isOn;

        button.disabled = true;
        try {
            const response = await fetch(`/api/devices/${button.dataset.device}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ enabled }),
            });
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || "Device update failed.");
            }

            button.setAttribute("aria-pressed", String(enabled));
            button.classList.toggle("is-on", enabled);
            button.textContent = enabled ? "On" : "Off";
            showUpdateTime();
        } catch (error) {
            window.alert(error.message);
        } finally {
            button.disabled = false;
        }
    });
});

sendReadingButton.addEventListener("click", async () => {
    sendReadingButton.disabled = true;
    sendStatus.classList.remove("is-error");
    sendStatus.textContent = "Sending...";

    try {
        const response = await fetch("/api/thingspeak/update", { method: "POST" });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "ThingSpeak update failed.");
        }

        sendStatus.textContent = `Sent successfully (entry #${result.entry_id}).`;
        showUpdateTime();
    } catch (error) {
        sendStatus.classList.add("is-error");
        sendStatus.textContent = error.message;
    } finally {
        sendReadingButton.disabled = false;
    }
});
