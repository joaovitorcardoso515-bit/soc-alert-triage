from datetime import datetime, timezone

from clients.indexer_client import IndexerClient
from parsers.alert_parser import AlertParser
from services.risk_engine import RiskEngine
from services.rules_engine import RulesEngine

try:
    from clients.ollama_client import OllamaClient
except ImportError:
    OllamaClient = None


class TriageService:

    def __init__(self):
        self.indexer = IndexerClient()
        self.parser = AlertParser()
        self.rules_engine = RulesEngine()
        self.risk_engine = RiskEngine()
        self.ollama = OllamaClient() if OllamaClient else None
        self._cache: dict[str, dict] = {}
        self._last_update: datetime | None = None

    def _build_alert_id(self, raw_alert, alert) -> str:
        return raw_alert.get("_id") or f"{alert.rule_id}-{alert.timestamp}"

    def _run_ai_analysis(self, alert, risk_result):
        if not self.ollama:
            return None

        try:
            return self.ollama.analyze(alert, risk_result)
        except Exception:
            return None

    def process_alerts(self, limit: int = 50) -> list[dict]:
        raw_alerts = self.indexer.search_alerts(limit)
        results = []

        for raw_alert in raw_alerts:
            alert = self.parser.parse(raw_alert)
            rule_result = self.rules_engine.analyze(alert)
            risk_result = self.risk_engine.calculate(alert, rule_result)
            ai_result = self._run_ai_analysis(alert, risk_result)

            alert_id = self._build_alert_id(raw_alert, alert)
            entry = {
                "id": alert_id,
                "alert": alert,
                "risk": risk_result,
                "raw": raw_alert,
                "ai": ai_result,
            }
            self._cache[alert_id] = entry
            results.append(entry)

        self._last_update = datetime.now(timezone.utc)
        return results

    def get_all_entries(self) -> list[dict]:
        if not self._cache:
            self.process_alerts(100)
        return list(self._cache.values())

    def get_alert(self, alert_id: str) -> dict | None:
        if alert_id not in self._cache:
            self.process_alerts(100)
        return self._cache.get(alert_id)

    def get_last_update(self) -> str | None:
        if not self._last_update:
            return None
        return self._last_update.isoformat()

    def get_statistics(self) -> dict:
        entries = self.get_all_entries()
        by_risk = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        by_agent: dict[str, int] = {}

        for entry in entries:
            risk = entry["risk"]["risk"]
            by_risk[risk] = by_risk.get(risk, 0) + 1
            agent = entry["alert"].agent_name or "Unknown"
            by_agent[agent] = by_agent.get(agent, 0) + 1

        return {
            "by_risk": by_risk,
            "by_agent": by_agent,
            "total": len(entries),
            "last_update": self.get_last_update(),
        }

    def get_filter_options(self) -> dict:
        entries = self.get_all_entries()
        agents = sorted({
            entry["alert"].agent_name
            for entry in entries
            if entry["alert"].agent_name
        })
        mitre_values = set()

        for entry in entries:
            mitre = entry["alert"].mitre
            if isinstance(mitre, dict):
                mitre_values.update(mitre.get("id", []))
                mitre_values.update(mitre.get("technique", []))
            elif mitre:
                mitre_values.add(str(mitre))

        return {
            "agents": agents,
            "mitre": sorted(mitre_values),
        }

    def is_ollama_online(self) -> bool:
        if self.ollama and hasattr(self.ollama, "ping"):
            try:
                return bool(self.ollama.ping())
            except Exception:
                return False

        if self.ollama and hasattr(self.ollama, "is_available"):
            try:
                return bool(self.ollama.is_available())
            except Exception:
                return False

        return self.ollama is not None

    @staticmethod
    def filter_entries(
        entries: list[dict],
        q: str | None = None,
        risk: str | None = None,
        agent: str | None = None,
        mitre: str | None = None,
    ) -> list[dict]:
        from web.serializers.alert_serializer import serialize_alert

        items = [serialize_alert(entry) for entry in entries]

        if q:
            query = q.lower().strip()
            items = [
                item for item in items
                if query in (item.get("source_ip") or "").lower()
                or query in (item.get("username") or "").lower()
                or query in str(item.get("rule_id") or "").lower()
                or query in (item.get("description") or "").lower()
            ]

        if risk:
            selected_risks = {
                value.strip().upper()
                for value in risk.split(",")
                if value.strip()
            }
            items = [item for item in items if item["risk"] in selected_risks]

        if agent:
            items = [item for item in items if item.get("agent") == agent]

        if mitre:
            mitre_query = mitre.lower().strip()
            items = [
                item for item in items
                if mitre_query in (item.get("mitre") or "").lower()
            ]

        return items

    @staticmethod
    def sort_items(items: list[dict], sort: str = "timestamp", order: str = "desc") -> list[dict]:
        reverse = order.lower() != "asc"
        sort_key = sort if sort in {"timestamp", "risk", "rule_id", "agent", "score"} else "timestamp"

        risk_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}

        def resolve_value(item: dict):
            value = item.get(sort_key)
            if sort_key == "risk":
                return risk_order.get(value, 0)
            return value or ""

        return sorted(items, key=resolve_value, reverse=reverse)
