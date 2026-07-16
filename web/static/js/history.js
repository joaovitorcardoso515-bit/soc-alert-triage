function getHistorySelectedRisks() {
    return [...document.querySelectorAll(".history-filter-risk")]
        .filter((input) => input.checked)
        .map((input) => input.value)
        .join(",");
}

function buildHistoryParams() {
    const params = new URLSearchParams();

    const search = document.getElementById("history-search")?.value.trim();
    if (search) params.set("q", search);

    const sort = document.getElementById("history-sort")?.value;
    if (sort) params.set("sort", sort);

    const order = document.getElementById("history-order")?.value;
    if (order) params.set("order", order);

    const risk = getHistorySelectedRisks();
    if (risk) params.set("risk", risk);

    return params;
}

async function loadHistory() {
    const tbody = document.querySelector("#history-table tbody");
    const emptyState = document.getElementById("history-empty");
    if (!tbody) return;

    tbody.innerHTML = `<tr class="loading-row"><td colspan="10">Carregando histórico...</td></tr>`;

    try {
        const response = await fetch(`/history?${buildHistoryParams().toString()}`, {
            headers: { Accept: "application/json" },
        });
        if (!response.ok) throw new Error("Falha ao carregar histórico");
        const data = await response.json();

        if (typeof updateMetaHeader === "function") {
            updateMetaHeader({
                total: data.total,
                last_update: data.last_update,
                ollama_online: false,
            });
        }

        fetch("/health/ollama", { headers: { Accept: "application/json" } })
            .then((r) => r.json())
            .then((health) => {
                if (typeof updateMetaHeader === "function") {
                    updateMetaHeader({
                        total: data.total,
                        last_update: data.last_update,
                        ollama_online: health.status === "online",
                    });
                }
            })
            .catch(() => {});

        if (!data.history.length) {
            tbody.innerHTML = "";
            emptyState?.classList.remove("hidden");
            return;
        }

        emptyState?.classList.add("hidden");

        tbody.innerHTML = data.history.map((alert) => `
            <tr data-id="${escapeHtml(alert.id)}">
                <td>${escapeHtml(formatTimestamp(alert.timestamp))}</td>
                <td><span class="${riskBadgeClass(alert.risk)}">${escapeHtml(alert.risk)}</span></td>
                <td>${escapeHtml(alert.score ?? "—")}</td>
                <td>${escapeHtml(alert.rule_id ?? "—")}</td>
                <td>${escapeHtml(alert.agent ?? "—")}</td>
                <td class="desc-cell" title="${escapeHtml(alert.description)}">${escapeHtml(truncate(alert.description, 50))}</td>
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
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr class="loading-row"><td colspan="10">Erro ao carregar histórico.</td></tr>`;
    }
}

function initHistoryEvents() {
    document.getElementById("history-search")?.addEventListener(
        "input",
        debounce(() => loadHistory())
    );

    document.getElementById("history-sort")?.addEventListener("change", () => loadHistory());
    document.getElementById("history-order")?.addEventListener("change", () => loadHistory());
    document.getElementById("refresh-history")?.addEventListener("click", () => loadHistory());

    document.querySelectorAll(".history-filter-risk").forEach((input) => {
        input.addEventListener("change", () => loadHistory());
    });
}

document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("history-table")) {
        initHistoryEvents();
        loadHistory();
    }
});
