const API_BASE = "";
const JSON_HEADERS = { Accept: "application/json" };

let riskChart = null;
let agentChart = null;

function debounce(fn, delay = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

function formatTimestamp(value) {
    if (!value) return "—";
    try {
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return value;
        return date.toLocaleString("pt-BR", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
        });
    } catch {
        return value;
    }
}

function truncate(text, max = 60) {
    if (!text) return "—";
    return text.length > max ? `${text.slice(0, max)}…` : text;
}

function riskBadgeClass(risk) {
    return `badge badge-${(risk || "low").toLowerCase()}`;
}

function escapeHtml(text) {
    if (text == null) return "";
    const div = document.createElement("div");
    div.textContent = String(text);
    return div.innerHTML;
}

function updateMetaHeader(data) {
    const lastUpdate = document.getElementById("last-update");
    const alertCount = document.getElementById("alert-count");
    const aiStatus = document.getElementById("ai-status");
    const aiStatusText = document.getElementById("ai-status-text");

    if (lastUpdate) {
        lastUpdate.textContent = data.last_update
            ? formatTimestamp(data.last_update)
            : new Date().toLocaleString("pt-BR");
    }

    if (alertCount) {
        alertCount.textContent = String(data.total ?? 0);
    }

    if (aiStatus && aiStatusText) {
        const online = data.ollama_online;
        aiStatus.classList.toggle("online", online);
        aiStatus.classList.toggle("offline", !online);
        aiStatusText.textContent = online ? "Online" : "Offline";
    }
}

function updateStatCards(byRisk, total) {
    const mapping = {
        "stat-total": total,
        "stat-critical": byRisk?.CRITICAL ?? 0,
        "stat-high": byRisk?.HIGH ?? 0,
        "stat-medium": byRisk?.MEDIUM ?? 0,
        "stat-low": byRisk?.LOW ?? 0,
    };

    Object.entries(mapping).forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = String(value);
    });
}

function getSelectedRisks(selector) {
    return [...document.querySelectorAll(selector)]
        .filter((input) => input.checked)
        .map((input) => input.value)
        .join(",");
}

function buildQueryParams(extra = {}) {
    const params = new URLSearchParams();

    const searchInput = document.getElementById("search-input");
    if (searchInput?.value.trim()) {
        params.set("q", searchInput.value.trim());
    }

    const risk = getSelectedRisks(".filter-risk");
    if (risk) params.set("risk", risk);

    const agent = document.getElementById("filter-agent")?.value;
    if (agent) params.set("agent", agent);

    const mitre = document.getElementById("filter-mitre")?.value;
    if (mitre) params.set("mitre", mitre);

    Object.entries(extra).forEach(([key, value]) => {
        if (value != null && value !== "") params.set(key, value);
    });

    return params;
}

async function fetchAlerts(params = new URLSearchParams()) {
    const response = await fetch(`${API_BASE}/alerts?${params.toString()}`, {
        headers: JSON_HEADERS,
    });
    if (!response.ok) throw new Error("Falha ao carregar alertas");
    return response.json();
}

async function fetchStatistics() {
    const response = await fetch(`${API_BASE}/statistics`, { headers: JSON_HEADERS });
    if (!response.ok) throw new Error("Falha ao carregar estatísticas");
    return response.json();
}

async function fetchFilters() {
    const response = await fetch(`${API_BASE}/filters`, { headers: JSON_HEADERS });
    if (!response.ok) return { agents: [], mitre: [] };
    return response.json();
}

function renderAlertsTable(alerts) {
    const tbody = document.querySelector("#alerts-table tbody");
    const emptyState = document.getElementById("empty-state");
    if (!tbody) return;

    if (!alerts.length) {
        tbody.innerHTML = "";
        emptyState?.classList.remove("hidden");
        return;
    }

    emptyState?.classList.add("hidden");

    tbody.innerHTML = alerts.map((alert) => `
        <tr data-id="${escapeHtml(alert.id)}">
            <td>${escapeHtml(formatTimestamp(alert.timestamp))}</td>
            <td><span class="${riskBadgeClass(alert.risk)}">${escapeHtml(alert.risk)}</span></td>
            <td>${escapeHtml(alert.rule_id ?? "—")}</td>
            <td>${escapeHtml(alert.agent ?? "—")}</td>
            <td class="desc-cell" title="${escapeHtml(alert.description)}">${escapeHtml(truncate(alert.description, 55))}</td>
            <td>${escapeHtml(alert.mitre || "—")}</td>
            <td>${escapeHtml(alert.source_ip || "—")}</td>
            <td><span class="ai-indicator ${alert.ai ? "" : "empty"}">${alert.ai ? "●" : "—"}</span></td>
            <td><button class="btn-view" data-id="${escapeHtml(alert.id)}">View</button></td>
        </tr>
    `).join("");

    tbody.querySelectorAll(".btn-view").forEach((btn) => {
        btn.addEventListener("click", (event) => {
            event.stopPropagation();
            openDetailPanel(btn.dataset.id);
        });
    });

    tbody.querySelectorAll("tr").forEach((row) => {
        row.addEventListener("click", () => openDetailPanel(row.dataset.id));
    });
}

function populateFilterDropdowns(filters) {
    const agentSelect = document.getElementById("filter-agent");
    const mitreSelect = document.getElementById("filter-mitre");

    if (agentSelect) {
        const current = agentSelect.value;
        agentSelect.innerHTML = '<option value="">Todos</option>' +
            (filters.agents || []).map((agent) =>
                `<option value="${escapeHtml(agent)}" ${agent === current ? "selected" : ""}>${escapeHtml(agent)}</option>`
            ).join("");
    }

    if (mitreSelect) {
        const current = mitreSelect.value;
        mitreSelect.innerHTML = '<option value="">Todos</option>' +
            (filters.mitre || []).map((item) =>
                `<option value="${escapeHtml(item)}" ${item === current ? "selected" : ""}>${escapeHtml(item)}</option>`
            ).join("");
    }
}

async function loadDashboard() {
    const tbody = document.querySelector("#alerts-table tbody");
    if (tbody) {
        tbody.innerHTML = `<tr class="loading-row"><td colspan="9">Carregando alertas...</td></tr>`;
    }

    try {
        const [alertsData, statsData, filtersData] = await Promise.all([
            fetchAlerts(buildQueryParams()),
            fetchStatistics(),
            fetchFilters(),
        ]);

        renderAlertsTable(alertsData.alerts);
        updateMetaHeader(alertsData);
        updateStatCards(statsData.by_risk, statsData.total);

        if (typeof renderCharts === "function") {
            renderCharts(statsData);
        }

        populateFilterDropdowns(filtersData);
    } catch (error) {
        console.error(error);
        if (tbody) {
            tbody.innerHTML = `<tr class="loading-row"><td colspan="9">Erro ao carregar alertas. Verifique a conexão com o Indexer.</td></tr>`;
        }
    }
}

async function openDetailPanel(alertId) {
    if (!alertId) return;

    try {
        const response = await fetch(`${API_BASE}/alerts/${encodeURIComponent(alertId)}`, {
            headers: JSON_HEADERS,
        });
        if (!response.ok) throw new Error("Alerta não encontrado");
        const alert = await response.json();

        const panel = document.getElementById("detail-panel");
        const overlay = document.getElementById("overlay");
        const content = document.getElementById("detail-panel-content");

        if (!panel || !content) return;

        content.innerHTML = buildDetailPanelHTML(alert);
        panel.classList.add("open");
        panel.setAttribute("aria-hidden", "false");
        overlay?.classList.add("visible");

        content.querySelector(".panel-close")?.addEventListener("click", closeDetailPanel);
    } catch (error) {
        console.error(error);
    }
}

function closeDetailPanel() {
    const panel = document.getElementById("detail-panel");
    const overlay = document.getElementById("overlay");

    panel?.classList.remove("open");
    panel?.setAttribute("aria-hidden", "true");
    overlay?.classList.remove("visible");
}

function buildDetailPanelHTML(alert) {
    const ai = alert.ai || {};
    const actions = Array.isArray(ai.recommended_actions)
        ? ai.recommended_actions.map((a) => `<li>${escapeHtml(a)}</li>`).join("")
        : "";

    const reasons = (alert.reasons || [])
        .map((r) => `<li>${escapeHtml(r)}</li>`)
        .join("");

    return `
        <div class="panel-header">
            <h2>Alert #${escapeHtml(alert.rule_id)} <span class="${riskBadgeClass(alert.risk)}">${escapeHtml(alert.risk)}</span></h2>
            <button class="panel-close" aria-label="Fechar">&times;</button>
        </div>

        <section class="panel-section">
            <h3>Detalhes</h3>
            <dl class="detail-list">
                <div class="detail-row"><dt>Rule</dt><dd>${escapeHtml(alert.rule_id ?? "—")}</dd></div>
                <div class="detail-row"><dt>Description</dt><dd>${escapeHtml(alert.description ?? "—")}</dd></div>
                <div class="detail-row"><dt>Agent</dt><dd>${escapeHtml(alert.agent ?? "—")}</dd></div>
                <div class="detail-row"><dt>Username</dt><dd>${escapeHtml(alert.username ?? "—")}</dd></div>
                <div class="detail-row"><dt>Source IP</dt><dd>${escapeHtml(alert.source_ip ?? "—")}</dd></div>
                <div class="detail-row"><dt>Destination IP</dt><dd>${escapeHtml(alert.destination_ip ?? "—")}</dd></div>
                <div class="detail-row"><dt>Ports</dt><dd>${escapeHtml(alert.src_port ?? "—")} → ${escapeHtml(alert.dst_port ?? "—")}</dd></div>
                <div class="detail-row"><dt>MITRE</dt><dd>${escapeHtml(alert.mitre ?? "—")}</dd></div>
                <div class="detail-row"><dt>Groups</dt><dd>${escapeHtml((alert.groups || []).join(", ") || "—")}</dd></div>
                <div class="detail-row"><dt>Decoder</dt><dd>${escapeHtml(alert.decoder ?? "—")}</dd></div>
                <div class="detail-row"><dt>Timestamp</dt><dd>${escapeHtml(formatTimestamp(alert.timestamp))}</dd></div>
                <div class="detail-row"><dt>Risk Score</dt><dd>${escapeHtml(alert.score ?? "—")}</dd></div>
            </dl>
        </section>

        ${reasons ? `
        <section class="reasons-block">
            <h3>Reasons</h3>
            <ul>${reasons}</ul>
        </section>` : ""}

        <section class="panel-section ai-panel">
            <h3>AI PRE TRIAGE</h3>
            ${alert.ai ? `
            <dl class="detail-list">
                <div class="detail-row"><dt>Summary</dt><dd>${escapeHtml(ai.summary ?? "—")}</dd></div>
                <div class="detail-row"><dt>Threat Assessment</dt><dd>${escapeHtml(ai.threat_assessment ?? "—")}</dd></div>
                <div class="detail-row"><dt>Reason</dt><dd>${escapeHtml(ai.reason ?? "—")}</dd></div>
                <div class="detail-row">
                    <dt>Recommended Actions</dt>
                    <dd>${actions ? `<ul class="actions-list">${actions}</ul>` : "—"}</dd>
                </div>
                <div class="detail-row"><dt>Confidence</dt><dd>${escapeHtml(ai.confidence ?? "—")}</dd></div>
            </dl>
            ` : `<p class="ai-unavailable">Análise de IA não disponível.</p>`}
        </section>
    `;
}

function initSidebar() {
    const toggle = document.getElementById("menu-toggle");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("overlay");

    toggle?.addEventListener("click", () => {
        sidebar?.classList.toggle("open");
    });

    overlay?.addEventListener("click", () => {
        closeDetailPanel();
        sidebar?.classList.remove("open");
    });
}

function initDashboardEvents() {
    const searchInput = document.getElementById("search-input");
    const refreshBtn = document.getElementById("refresh-btn");

    searchInput?.addEventListener("input", debounce(() => loadDashboard()));
    refreshBtn?.addEventListener("click", () => loadDashboard());

    document.querySelectorAll(".filter-risk").forEach((input) => {
        input.addEventListener("change", () => loadDashboard());
    });

    document.getElementById("filter-agent")?.addEventListener("change", () => loadDashboard());
    document.getElementById("filter-mitre")?.addEventListener("change", () => loadDashboard());

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") closeDetailPanel();
    });
}

document.addEventListener("DOMContentLoaded", () => {
    initSidebar();
    initDashboardEvents();

    if (document.getElementById("alerts-table")) {
        loadDashboard();
    }
});
