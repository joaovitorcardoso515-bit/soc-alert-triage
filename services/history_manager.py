import json
from pathlib import Path
from datetime import datetime


class HistoryManager:

    def __init__(self):

        self.base_path = Path("history")
        self.base_path.mkdir(exist_ok=True)

    def save(self, alert):

        now = datetime.now()

        day_folder = self.base_path / now.strftime("%Y-%m-%d")
        day_folder.mkdir(exist_ok=True)

        filename = now.strftime("%H-%M-%S-%f") + ".json"

        filepath = day_folder / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                alert.to_dict(),
                f,
                indent=4,
                ensure_ascii=False
            )

    def load_all(self):

        alerts = []

        for file in self.base_path.rglob("*.json"):

            with open(file, encoding="utf-8") as f:
                alerts.append(json.load(f))

        return alerts

    def search_by_ip(self, ip):

        result = []

        for alert in self.load_all():

            network = alert.get("network", {})

            if network.get("source_ip") == ip:
                result.append(alert)

        return result

    def search_by_user(self, username):

        result = []

        for alert in self.load_all():

            if alert.get("username") == username:
                result.append(alert)

        return result

    def search_by_rule(self, rule_id):

        result = []

        for alert in self.load_all():

            if alert.get("rule_id") == rule_id:
                result.append(alert)

        return result

    def statistics(self):

        alerts = self.load_all()

        stats = {
            "total_alerts": len(alerts),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

        for alert in alerts:

            level = alert.get("level", 0)

            if level >= 15:
                stats["critical"] += 1

            elif level >= 10:
                stats["high"] += 1

            elif level >= 5:
                stats["medium"] += 1

            else:
                stats["low"] += 1

        return stats