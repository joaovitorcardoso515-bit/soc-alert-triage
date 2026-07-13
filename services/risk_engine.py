class RiskEngine:


    def calculate(self, alert, rule_result):

        score = 0


        # Score baseado no nível do Wazuh
        if alert.level >= 12:
            score += 60

        elif alert.level >= 8:
            score += 40

        elif alert.level >= 5:
            score += 25

        else:
            score += 10


        # Adiciona pontos das regras customizadas
        score += rule_result["score"]


        if score >= 80:
            risk = "CRITICAL"

        elif score >= 60:
            risk = "HIGH"

        elif score >= 30:
            risk = "MEDIUM"

        else:
            risk = "LOW"


        return {
            "risk": risk,
            "score": score,
            "reasons": rule_result["reasons"]
        }