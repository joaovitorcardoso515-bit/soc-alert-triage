from clients.indexer_client import IndexerClient

from parsers.alert_parser import AlertParser

from services.risk_engine import RiskEngine
from services.rules_engine import RulesEngine
from logs.logger import AlertLogger


# Clientes
indexer = IndexerClient()

# Processadores
parser = AlertParser()
rules_engine = RulesEngine()
risk_engine = RiskEngine()

# Logger
logger = AlertLogger()


# Buscar alertas do Wazuh Indexer
alerts = indexer.search_alerts(5)


for raw_alert in alerts:

    # Converter JSON Wazuh -> objeto Alert
    alert = parser.parse(raw_alert)


    # Aplicar regras customizadas
    rule_result = rules_engine.analyze(alert)


    # Calcular risco final
    risk_result = risk_engine.calculate(
        alert,
        rule_result
    )


    # Salvar log estruturado
    logger.save(
        alert,
        risk_result
    )


    # Exibir resultado no terminal
    print(alert)

    print(
        "Risk:",
        risk_result["risk"],
        "| Score:",
        risk_result["score"]
    )

    print("Motivos:")

    for reason in risk_result["reasons"]:
        print("-", reason)

    print("====================")