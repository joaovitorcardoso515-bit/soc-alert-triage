from models.alert import Alert


class AlertParser:

    def parse_mitre(self, rule):

        mitre = rule.get("mitre", {})

        return {
            "id": mitre.get("id", []),
            "tactic": mitre.get("tactic", []),
            "technique": mitre.get("technique", [])
        }


    def parse(self, raw_alert):

        source = raw_alert["_source"]

        rule = source.get("rule", {})
        agent = source.get("agent", {})

        data = source.get("data", {})


        return Alert(

            rule_id=rule.get("id"),

            level=rule.get("level"),

            description=rule.get("description"),


            agent_id=agent.get("id"),

            agent_name=agent.get("name"),

            agent_ip=agent.get("ip"),


            source_ip=data.get("srcip"),

            username=data.get("srcuser"),


            mitre=self.parse_mitre(rule),


            timestamp=source.get("timestamp")
        )