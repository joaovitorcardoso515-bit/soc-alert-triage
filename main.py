from clients.indexer_client import IndexerClient

from parsers.alert_parser import AlertParser

from services.rules_engine import RulesEngine
from services.risk_engine import RiskEngine
from services.history_manager import HistoryManager
from services.ai_triage import AITriage

from logs.logger import AlertLogger


def main():

    # Clientes
    indexer = IndexerClient()

    # Serviços
    parser = AlertParser()
    rules_engine = RulesEngine()
    risk_engine = RiskEngine()
    history = HistoryManager()
    ai = AITriage()
    logger = AlertLogger()

    # Buscar os últimos alertas
    alerts = indexer.search_alerts(limit=5)

    if not alerts:
        print("Nenhum alerta encontrado.")
        return

    for raw_alert in alerts:

        # Converter JSON -> Alert
        alert = parser.parse(raw_alert)

        # Salvar histórico
        history.save(alert)

        # Aplicar regras customizadas
        rule_result = rules_engine.analyze(alert)

        # Calcular risco
        risk_result = risk_engine.calculate(
            alert,
            rule_result
        )

        # IA
        ai_result = ai.analyze(
            alert,
            risk_result
        )

        # Salvar log estruturado
        logger.save(
            alert,
            risk_result
        )

        # Exibir alerta
        print(alert)

        print(
            f"Risk: {risk_result['risk']} | Score: {risk_result['score']}"
        )

        print()

        print("Reasons")

        if risk_result["reasons"]:
            for reason in risk_result["reasons"]:
                print(f"- {reason}")
        else:
            print("- None")

        print()

        print("========== AI TRIAGE ==========")
        print(ai_result)
        print("===============================")

        print()

    print("===== ESTATÍSTICAS =====")
    print(history.statistics())


if __name__ == "__main__":
    main()