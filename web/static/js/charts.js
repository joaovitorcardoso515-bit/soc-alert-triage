const CHART_COLORS = {
    LOW: "#22C55E",
    MEDIUM: "#EAB308",
    HIGH: "#F97316",
    CRITICAL: "#EF4444",
};

const chartDefaults = {
    color: "#9CA3AF",
    borderColor: "rgba(255,255,255,0.06)",
};

function renderCharts(stats) {
    renderRiskPieChart(stats.by_risk);
    renderAgentBarChart(stats.by_agent);
}

function renderRiskPieChart(byRisk) {
    const canvas = document.getElementById("risk-pie");
    if (!canvas || typeof Chart === "undefined") return;

    const data = [
        byRisk?.LOW ?? 0,
        byRisk?.MEDIUM ?? 0,
        byRisk?.HIGH ?? 0,
        byRisk?.CRITICAL ?? 0,
    ];

    if (window.riskChart) {
        window.riskChart.destroy();
    }

    window.riskChart = new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            datasets: [{
                data,
                backgroundColor: [
                    CHART_COLORS.LOW,
                    CHART_COLORS.MEDIUM,
                    CHART_COLORS.HIGH,
                    CHART_COLORS.CRITICAL,
                ],
                borderColor: "#151F2E",
                borderWidth: 3,
                hoverOffset: 6,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "65%",
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        color: "#F3F4F6",
                        padding: 16,
                        usePointStyle: true,
                        pointStyle: "circle",
                        font: { size: 12 },
                    },
                },
                tooltip: {
                    backgroundColor: "#151F2E",
                    titleColor: "#F3F4F6",
                    bodyColor: "#9CA3AF",
                    borderColor: "rgba(255,255,255,0.1)",
                    borderWidth: 1,
                    padding: 12,
                },
            },
        },
    });
}

function renderAgentBarChart(byAgent) {
    const canvas = document.getElementById("agent-bar");
    if (!canvas || typeof Chart === "undefined") return;

    const labels = Object.keys(byAgent || {});
    const values = Object.values(byAgent || {});

    if (window.agentChart) {
        window.agentChart.destroy();
    }

    window.agentChart = new Chart(canvas, {
        type: "bar",
        data: {
            labels: labels.length ? labels : ["Sem dados"],
            datasets: [{
                label: "Alertas",
                data: values.length ? values : [0],
                backgroundColor: "rgba(59, 130, 246, 0.7)",
                borderColor: "#3B82F6",
                borderWidth: 1,
                borderRadius: 6,
                borderSkipped: false,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "#151F2E",
                    titleColor: "#F3F4F6",
                    bodyColor: "#9CA3AF",
                    borderColor: "rgba(255,255,255,0.1)",
                    borderWidth: 1,
                },
            },
            scales: {
                x: {
                    ticks: { color: chartDefaults.color, maxRotation: 45 },
                    grid: { color: chartDefaults.borderColor },
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: chartDefaults.color,
                        stepSize: 1,
                        precision: 0,
                    },
                    grid: { color: chartDefaults.borderColor },
                },
            },
        },
    });
}
