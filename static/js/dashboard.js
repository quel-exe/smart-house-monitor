// Visual-only controls for Phase 1. Later, these can send commands to Flask/ESP32.
const controlButtons = document.querySelectorAll(".toggle-button");
const updatedTime = document.querySelector("#updated-time");

function showUpdateTime() {
    updatedTime.textContent = new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
    });
}

controlButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const isOn = button.getAttribute("aria-pressed") === "true";
        button.setAttribute("aria-pressed", String(!isOn));
        button.classList.toggle("is-on", !isOn);
        button.textContent = isOn ? "Off" : "On";
        showUpdateTime();
    });
});
