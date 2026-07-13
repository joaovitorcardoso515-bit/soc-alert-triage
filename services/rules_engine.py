class RulesEngine:


    def analyze(self, alert):

        score = 0
        reasons = []


        # Regra 1 - nível alto do Wazuh
        if alert.level >= 10:
            score += 40
            reasons.append(
                "Wazuh alert level crítico"
            )


        # Regra 2 - instalação de pacote
        if "dpkg" in alert.description.lower():

            score += 15

            reasons.append(
                "Instalação de pacote detectada"
            )


        # Regra 3 - PAM
        if "login" in alert.description.lower():

            score += 10

            reasons.append(
                "Evento de autenticação"
            )


        return {
            "score": score,
            "reasons": reasons
        }