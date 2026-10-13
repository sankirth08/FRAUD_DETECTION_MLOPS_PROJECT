
import { checkApiHealth, predictFraud } from "../frontend/src/api/api.js";

const form = document.getElementById("fraud-form");
const analyzeButton = document.getElementById("analyze-button");
const errorMessage = document.getElementById("error-message");
const apiStatus = document.getElementById("api-status");
const sidebarIndicator = document.getElementById("sidebar-indicator");
const sessionPredictions = [];
let decisionThreshold = 0.8;
let activityChart;
let distributionChart;
let analyticsChart;

function setApiStatus(online) {
    apiStatus.dataset.state = online ? "online" : "offline";
    apiStatus.querySelector("span:last-child").textContent = online ? "API connected" : "API unavailable";
    sidebarIndicator.classList.toggle("online", online);
    sidebarIndicator.classList.toggle("offline", !online);
    document.getElementById("footer-api").textContent = online ? "API connection active" : "API connection unavailable";
}

function setThreshold(value) {
    decisionThreshold = value;
    const label = `${(value * 100).toFixed(0)}%`;
    document.getElementById("threshold-value").textContent = label;
    document.getElementById("analytics-threshold").textContent = label;
    document.getElementById("result-threshold").textContent = `${label} flag threshold`;
    document.querySelector(".threshold-marker").style.left = `${value * 100}%`;
}

function createCharts() {
    if (!window.Chart) {
        document.querySelectorAll(".chart-empty").forEach((message) => {
            message.textContent = "Chart.js could not be loaded. Check the connection and refresh.";
        });
        return;
    }

    Chart.defaults.color = "#7f8ca7";
    Chart.defaults.font.family = "DM Sans, Segoe UI, sans-serif";
    Chart.defaults.font.size = 9;

    const activityCanvas = document.getElementById("activity-chart");
    const activityContext = activityCanvas.getContext("2d");
    const activityFill = activityContext.createLinearGradient(0, 0, 0, 190);
    activityFill.addColorStop(0, "rgba(143, 122, 255, 0.28)");
    activityFill.addColorStop(1, "rgba(78, 119, 227, 0.005)");

    const lineOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 450 },
        interaction: { intersect: false, mode: "index" },
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: "#171f34",
                borderColor: "rgba(157, 139, 255, .3)",
                borderWidth: 1,
                titleColor: "#e6e8f8",
                bodyColor: "#b3bdd1",
                displayColors: false,
                callbacks: { label: (context) => `Fraud probability: ${context.parsed.y.toFixed(2)}%` }
            }
        },
        scales: {
            x: { grid: { display: false }, border: { display: false }, ticks: { color: "#77849f", maxTicksLimit: 7, maxRotation: 0 } },
            y: { min: 0, max: 100, grid: { color: "rgba(136, 153, 192, .09)" }, border: { display: false }, ticks: { stepSize: 25, padding: 8, callback: (value) => `${value}%` } }
        }
    };

    activityChart = new Chart(activityCanvas, {
        type: "line",
        data: { labels: [], datasets: [{ data: [], borderColor: "#a18bff", backgroundColor: activityFill, fill: true, borderWidth: 2, pointRadius: 3, pointHoverRadius: 5, pointBackgroundColor: "#b4a4ff", pointBorderColor: "#111a2d", pointBorderWidth: 2, tension: 0.34 }] },
        options: lineOptions
    });

    analyticsChart = new Chart(document.getElementById("analytics-chart"), {
        type: "line",
        data: { labels: [], datasets: [{ label: "Fraud probability", data: [], borderColor: "#64cfc7", backgroundColor: "rgba(91, 208, 195, .12)", fill: true, borderWidth: 2, pointRadius: 3, pointHoverRadius: 5, pointBackgroundColor: "#75e1d3", pointBorderColor: "#111a2d", pointBorderWidth: 2, tension: 0.34 }] },
        options: lineOptions
    });

    distributionChart = new Chart(document.getElementById("distribution-chart"), {
        type: "doughnut",
        data: { labels: ["Fraud", "Legitimate"], datasets: [{ data: [], backgroundColor: ["#a389ff", "#55d6c3"], hoverBackgroundColor: ["#b49fff", "#76e3d2"], borderColor: "#111a2d", borderWidth: 4, hoverOffset: 5 }] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "77%",
            plugins: {
                legend: { display: false },
                tooltip: { backgroundColor: "#171f34", borderColor: "rgba(157, 139, 255, .3)", borderWidth: 1, callbacks: { label: (context) => ` ${context.label}: ${context.parsed}` } }
            }
        }
    });
}

function createCell(text, className) {
    const cell = document.createElement("td");
    cell.textContent = text;
    if (className) cell.className = className;
    return cell;
}

function createDecisionBadge(prediction) {
    const badge = document.createElement("span");
    const fraud = prediction.fraud;
    badge.className = `decision-badge${fraud ? " fraud" : ""}`;
    badge.textContent = prediction.result;
    return badge;
}

function renderTable(body, predictions, overview) {
    body.replaceChildren();
    const visible = overview ? predictions.slice(-5).reverse() : [...predictions].reverse();

    if (visible.length === 0) {
        const row = document.createElement("tr");
        row.className = "empty-row";
        const cell = createCell("No predictions in this session yet.");
        cell.colSpan = overview ? 5 : 6;
        row.append(cell);
        body.append(row);
        return;
    }

    for (const prediction of visible) {
        const row = document.createElement("tr");
        if (overview) {
            row.append(createCell(prediction.reference, "reference-cell"));
            row.append(createCell(prediction.type));
            row.append(createCell(`$${prediction.amount.toLocaleString(undefined, { maximumFractionDigits: 2 })}`));
            row.append(createCell(`${(prediction.probability * 100).toFixed(2)}%`, "risk-cell"));
            const decisionCell = document.createElement("td");
            decisionCell.append(createDecisionBadge(prediction));
            row.append(decisionCell);
        } else {
            row.append(createCell(prediction.reference, "reference-cell"));
            row.append(createCell(prediction.timestamp));
            row.append(createCell(prediction.type));
            row.append(createCell(`$${prediction.amount.toLocaleString(undefined, { maximumFractionDigits: 2 })}`));
            row.append(createCell(`${(prediction.probability * 100).toFixed(2)}%`, "risk-cell"));
            const decisionCell = document.createElement("td");
            decisionCell.append(createDecisionBadge(prediction));
            row.append(decisionCell);
        }
        body.append(row);
    }
}

function renderSession() {
    const total = sessionPredictions.length;
    const fraud = sessionPredictions.filter((item) => item.fraud).length;
    const legitimate = total - fraud;
    const values = {
        "total-count": total,
        "fraud-count": fraud,
        "legitimate-count": legitimate,
        "fraud-rate": `${((fraud / total) * 100).toFixed(1)}%`,
        "donut-total": total,
        "legend-fraud": fraud,
        "legend-legitimate": legitimate,
        "session-count": `${total} ${total === 1 ? "prediction" : "predictions"}`
    };

    for (const [id, value] of Object.entries(values)) {
        document.getElementById(id).textContent = total ? value : "—";
    }

    renderTable(document.getElementById("overview-table"), sessionPredictions, true);
    renderTable(document.getElementById("transactions-table"), sessionPredictions, false);

    if (total && activityChart && distributionChart && analyticsChart) {
        const recent = sessionPredictions.slice(-24);
        const labels = recent.map((item) => item.reference.slice(2));
        const probabilities = recent.map((item) => item.probability * 100);
        activityChart.data.labels = labels;
        activityChart.data.datasets[0].data = probabilities;
        activityChart.update();
        analyticsChart.data.labels = labels;
        analyticsChart.data.datasets[0].data = probabilities;
        analyticsChart.update();
        distributionChart.data.datasets[0].data = [fraud, legitimate];
        distributionChart.update();
        document.getElementById("activity-empty").hidden = true;
        document.getElementById("analytics-empty").hidden = true;
    }
}

async function refreshApiStatus() {
    try {
        const health = await checkApiHealth();
        setApiStatus(health.status === "healthy");
    } catch {
        setApiStatus(false);
    }
}

function updateResult(result, transaction) {
    const probability = Math.max(0, Math.min(1, Number(result.fraud_probability)));
    const fraud = Number(result.fraud_prediction) === 1 || String(result.result).toLowerCase() === "fraud";
    const resultLabel = fraud ? "Fraud detected" : "Legitimate";
    const percentage = (probability * 100).toFixed(2);
    const risk = fraud ? "high" : probability >= decisionThreshold * 0.5 ? "elevated" : "low";
    const riskCaption = risk === "high" ? "ABOVE THRESHOLD" : risk === "elevated" ? "ELEVATED" : "LOW RISK";
    const threshold = Number(result.threshold ?? decisionThreshold);

    setThreshold(threshold);
    document.getElementById("empty-result").hidden = true;
    document.getElementById("result-content").hidden = false;
    const banner = document.getElementById("result-banner");
    banner.dataset.risk = risk;
    document.getElementById("result-label").textContent = resultLabel;
    document.getElementById("risk-caption").textContent = riskCaption;
    document.getElementById("probability-value").textContent = `${percentage}%`;
    document.getElementById("probability-bar").style.width = `${percentage}%`;
    document.getElementById("decision-value").textContent = resultLabel;
    document.getElementById("result-type").textContent = transaction.type.replaceAll("_", " ");

    const now = new Date();
    sessionPredictions.push({
        reference: `T-${String(sessionPredictions.length + 1).padStart(4, "0")}`,
        timestamp: now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        type: transaction.type.replaceAll("_", " "),
        amount: transaction.amount,
        probability,
        result: fraud ? "Fraud" : "Legitimate",
        fraud
    });
    renderSession();
}

setThreshold(decisionThreshold);
createCharts();
renderSession();
refreshApiStatus();

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorMessage.textContent = "";
    analyzeButton.disabled = true;
    analyzeButton.querySelector("span:first-child").textContent = "Analyzing with production model…";

    const transaction = {
        step: Number(document.getElementById("step").value),
        type: document.getElementById("type").value,
        amount: Number(document.getElementById("amount").value),
        oldbalanceOrg: Number(document.getElementById("oldbalanceOrg").value),
        newbalanceOrig: Number(document.getElementById("newbalanceOrig").value),
        oldbalanceDest: Number(document.getElementById("oldbalanceDest").value),
        newbalanceDest: Number(document.getElementById("newbalanceDest").value)
    };

    try {
        const result = await predictFraud(transaction);
        if (!Number.isFinite(Number(result.fraud_probability)) || result.fraud_prediction === undefined) {
            throw new Error("The API response is missing prediction or probability data.");
        }
        setApiStatus(true);
        updateResult(result, transaction);
        document.getElementById("result-content").scrollIntoView({ behavior: "smooth", block: "nearest" });
    } catch (error) {
        setApiStatus(false);
        errorMessage.textContent = `Could not analyze this transaction. ${error.message} Confirm the FastAPI server is running on port 8000.`;
    } finally {
        analyzeButton.disabled = false;
        analyzeButton.querySelector("span:first-child").textContent = "Run fraud analysis";
    }
});

const sidebar = document.getElementById("sidebar");
const scrim = document.getElementById("mobile-scrim");
const menuButton = document.getElementById("menu-button");

function setMenuOpen(open) {
    sidebar.classList.toggle("open", open);
    scrim.classList.toggle("visible", open);
    menuButton.setAttribute("aria-expanded", String(open));
}

menuButton.addEventListener("click", () => setMenuOpen(!sidebar.classList.contains("open")));
scrim.addEventListener("click", () => setMenuOpen(false));
document.querySelectorAll(".nav-link, .brand, .primary-link, .text-link").forEach((link) => {
    link.addEventListener("click", () => setMenuOpen(false));
});
document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setMenuOpen(false);
});

if ("IntersectionObserver" in window) {
    const sections = document.querySelectorAll(".page-section");
    const observer = new IntersectionObserver((entries) => {
        for (const entry of entries) {
            if (!entry.isIntersecting) continue;
            const id = entry.target.id;
            const title = entry.target.dataset.title;
            document.getElementById("current-view").textContent = title;
            document.querySelectorAll(".nav-link").forEach((link) => {
                const active = link.getAttribute("href") === `#${id}`;
                link.classList.toggle("active", active);
                if (active) link.setAttribute("aria-current", "page");
                else link.removeAttribute("aria-current");
            });
        }
    }, { rootMargin: "-18% 0px -68% 0px", threshold: 0 });
    sections.forEach((section) => observer.observe(section));
}

