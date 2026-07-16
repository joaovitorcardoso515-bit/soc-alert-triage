from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from web.serializers.alert_serializer import serialize_alert
from web.services.triage_service import TriageService

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="AI SOC Triage",
    description="Plataforma profissional de análise de alertas",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

_triage: TriageService | None = None


def get_triage() -> TriageService:
    global _triage
    if _triage is None:
        _triage = TriageService()
    return _triage


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "page": "dashboard"},
    )


@app.get("/history")
async def history(
    request: Request,
    sort: str = Query("timestamp"),
    order: str = Query("desc"),
    q: str | None = Query(None),
    risk: str | None = Query(None),
    agent: str | None = Query(None),
    mitre: str | None = Query(None),
    limit: int = Query(200, ge=1, le=500),
):
    accept = request.headers.get("accept", "")
    wants_json = "application/json" in accept and "text/html" not in accept

    if wants_json:
        entries = get_triage().process_alerts(limit)
        items = TriageService.filter_entries(entries, q=q, risk=risk, agent=agent, mitre=mitre)
        items = TriageService.sort_items(items, sort=sort, order=order)

        return {
            "history": items,
            "total": len(items),
            "last_update": get_triage().get_last_update(),
        }

    return templates.TemplateResponse(
        "history.html",
        {"request": request, "page": "history"},
    )


@app.get("/alert/{alert_id}", response_class=HTMLResponse)
async def alert_page(request: Request, alert_id: str):
    entry = get_triage().get_alert(alert_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")

    return templates.TemplateResponse(
        "alert.html",
        {
            "request": request,
            "page": "alerts",
            "alert": serialize_alert(entry),
        },
    )


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse(
        "settings.html",
        {"request": request, "page": "settings"},
    )


@app.get("/alerts")
async def get_alerts(
    q: str | None = Query(None, description="Busca por IP, usuário, rule ID ou descrição"),
    risk: str | None = Query(None, description="Filtro de risco separado por vírgula"),
    agent: str | None = Query(None, description="Filtro por agente"),
    mitre: str | None = Query(None, description="Filtro por MITRE"),
    limit: int = Query(100, ge=1, le=500),
):
    entries = get_triage().process_alerts(limit)
    items = TriageService.filter_entries(entries, q=q, risk=risk, agent=agent, mitre=mitre)

    return {
        "alerts": items,
        "total": len(items),
        "last_update": get_triage().get_last_update(),
        "ollama_online": get_triage().is_ollama_online(),
    }


@app.get("/alerts/{alert_id}")
async def get_alert(alert_id: str):
    entry = get_triage().get_alert(alert_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return serialize_alert(entry)


@app.get("/statistics")
async def get_statistics(limit: int = Query(100, ge=1, le=500)):
    get_triage().process_alerts(limit)
    stats = get_triage().get_statistics()
    stats["ollama_online"] = get_triage().is_ollama_online()
    return stats


@app.get("/filters")
async def get_filters(limit: int = Query(100, ge=1, le=500)):
    get_triage().process_alerts(limit)
    return get_triage().get_filter_options()


@app.get("/health/ollama")
async def ollama_health():
    return {
        "status": "online" if get_triage().is_ollama_online() else "offline",
    }
