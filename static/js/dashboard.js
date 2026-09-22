const controlButtons = document.querySelectorAll(".toggle-button");
const updatedTime = document.querySelector("#updated-time");

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
