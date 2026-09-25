const controlButtons = document.querySelectorAll(".toggle-button");
const updatedTime = document.querySelector("#updated-time");
const sendReadingButton = document.querySelector("#send-reading-button");
const sendStatus = document.querySelector("#send-status");
const refreshHistoryButton = document.querySelector("#refresh-history-button");
const historyStatus = document.querySelector("#history-status");
const historyCharts = document.querySelector("#history-charts");
const historyTableWrap = document.querySelector("#history-table-wrap");
const historyTableBody = document.querySelector("#history-table-body");
let historyFeeds = [];

function showUpdateTime() {
    updatedTime.textContent = new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
    });
}

function formatNumber(value, digits = 1) {
    return value === null || value === undefined ? "—" : Number(value).toFixed(digits);
}

function formatTime(timestamp) {
    if (!timestamp) return "—";
    return new Date(timestamp).toLocaleString([], {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

function drawChart(canvasId, values, color) {
    const canvas = document.querySelector(`#${canvasId}`);
    const context = canvas.getContext("2d");
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const pixelRatio = window.devicePixelRatio || 1;
    canvas.width = Math.round(width * pixelRatio);
    canvas.height = Math.round(height * pixelRatio);
    context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
    context.clearRect(0, 0, width, height);

    const points = values.filter((value) => Number.isFinite(value));
    if (!points.length) {
        context.fillStyle = "#64748b";
        context.font = "14px Arial";
        context.textAlign = "center";
        context.fillText("No readings available", width / 2, height / 2);
        return;
    }

    const padding = { top: 16, right: 16, bottom: 30, left: 48 };
    let minimum = Math.min(...points);
    let maximum = Math.max(...points);
    if (minimum === maximum) {
        minimum -= minimum === 0 ? 1 : Math.abs(minimum) * 0.1;
        maximum += maximum === 0 ? 1 : Math.abs(maximum) * 0.1;
    }
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;
    const xFor = (index) => padding.left + (values.length === 1 ? chartWidth / 2 : (index / (values.length - 1)) * chartWidth);
    const yFor = (value) => padding.top + ((maximum - value) / (maximum - minimum)) * chartHeight;

    context.strokeStyle = "#e2e8f0";
    context.lineWidth = 1;
    for (let step = 0; step <= 2; step += 1) {
        const y = padding.top + (step / 2) * chartHeight;
        context.beginPath();
        context.moveTo(padding.left, y);
        context.lineTo(width - padding.right, y);
        context.stroke();
    }

    context.fillStyle = "#64748b";
    context.font = "12px Arial";
    context.textAlign = "right";
    context.fillText(maximum.toFixed(1), padding.left - 8, padding.top + 4);
    context.fillText(minimum.toFixed(1), padding.left - 8, padding.top + chartHeight + 4);
    context.textAlign = "left";
    context.fillText("Oldest", padding.left, height - 8);
    context.textAlign = "right";
    context.fillText("Latest", width - padding.right, height - 8);

    context.strokeStyle = color;
    context.lineWidth = 2.5;
    context.lineJoin = "round";
    let drawing = false;
    values.forEach((value, index) => {
        if (!Number.isFinite(value)) {
            drawing = false;
            return;
        }
        const x = xFor(index);
        const y = yFor(value);
        if (!drawing) {
            context.beginPath();
            context.moveTo(x, y);
            drawing = true;
        } else {
            context.lineTo(x, y);
        }
        context.stroke();
    });
}

function renderHistory(feeds) {
    historyCharts.hidden = false;
    historyTableWrap.hidden = false;
    const readings = feeds.map((feed) => ({
        temperature: feed.temperature,
        humidity: feed.humidity,
        motion: feed.motion,
        lightLevel: feed.light_level,
    }));
    drawChart("temperature-chart", readings.map((reading) => reading.temperature), "#ef4444");
    drawChart("humidity-chart", readings.map((reading) => reading.humidity), "#2563eb");
    drawChart("motion-chart", readings.map((reading) => reading.motion), "#8b5cf6");
    drawChart("light-level-chart", readings.map((reading) => reading.lightLevel), "#f59e0b");

    historyTableBody.replaceChildren();
    [...feeds].reverse().forEach((feed) => {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${formatTime(feed.created_at)}</td><td>${formatNumber(feed.temperature)} °C</td><td>${formatNumber(feed.humidity)} %</td><td>${feed.motion === null ? "—" : (feed.motion ? "Detected" : "No motion")}</td><td>${formatNumber(feed.light_level, 0)}</td>`;
        historyTableBody.append(row);
    });
}

async function loadHistory() {
    refreshHistoryButton.disabled = true;
    historyStatus.classList.remove("is-error");
    historyStatus.textContent = "Loading ThingSpeak history…";
    try {
        const response = await fetch("/api/thingspeak/history?results=20");
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "Could not load ThingSpeak history.");

        historyFeeds = result.feeds;
        if (!historyFeeds.length) {
            historyStatus.textContent = "No ThingSpeak readings yet. Send a reading, then refresh this section.";
            historyCharts.hidden = true;
            historyTableWrap.hidden = true;
            return;
        }
        renderHistory(historyFeeds);
        historyStatus.textContent = `Showing ${historyFeeds.length} recent ThingSpeak reading${historyFeeds.length === 1 ? "" : "s"}.`;
    } catch (error) {
        historyStatus.classList.add("is-error");
        historyStatus.textContent = error.message;
        historyCharts.hidden = true;
        historyTableWrap.hidden = true;
    } finally {
        refreshHistoryButton.disabled = false;
    }
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
        loadHistory();
    } catch (error) {
        sendStatus.classList.add("is-error");
        sendStatus.textContent = error.message;
    } finally {
        sendReadingButton.disabled = false;
    }
});

refreshHistoryButton.addEventListener("click", loadHistory);
window.addEventListener("resize", () => {
    if (historyFeeds.length) renderHistory(historyFeeds);
});
loadHistory();
