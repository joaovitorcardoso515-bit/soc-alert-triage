import requests


class AITriage:

    def __init__(self):
        self.url = "http://localhost:11434/api/generate"
        self.model = "gemma3:1b"

    def build_prompt(self, alert, risk):

        return f"""
You are an expert SOC analyst.

You MUST analyze the alert below.

Do NOT ask questions.
Do NOT request more information.
Do NOT invent facts.
Use ONLY the data provided.

ALERT

Rule ID: {alert.rule_id}
Description: {alert.description}
Level: {alert.level}
Agent: {alert.agent_name}
User: {alert.username}
Source IP: {alert.source_ip}
MITRE IDs: {", ".join(alert.mitre.get("id", [])) or "None"}

Risk: {risk["risk"]}
Score: {risk["score"]}

OUTPUT

Summary:
Threat:
Reason:
Recommended Actions:
1.
2.
3.
"""

    def analyze(self, alert, risk):

        prompt = self.build_prompt(alert, risk)

        try:

            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )

            response.raise_for_status()

            data = response.json()

            return data["response"]

        except Exception as e:

            return str(e)