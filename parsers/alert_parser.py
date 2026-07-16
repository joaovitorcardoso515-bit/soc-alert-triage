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

        source = raw_alert.get("_source", {})

        rule = source.get("rule", {})
        agent = source.get("agent", {})
        data = source.get("data", {})

        return Alert(

            # Rule
            rule_id=rule.get("id"),
            level=rule.get("level"),
            description=rule.get("description"),

            # Agent
            agent_id=agent.get("id"),
            agent_name=agent.get("name"),
            agent_ip=agent.get("ip"),

            # Network
            source_ip=data.get("srcip"),
            destination_ip=data.get("dstip"),
            source_port=data.get("srcport"),
            destination_port=data.get("dstport"),
            protocol=data.get("protocol"),

            # User
            username=(
                data.get("srcuser")
                or data.get("dstuser")
                or data.get("user")
            ),

            # MITRE
            mitre=self.parse_mitre(rule),

            # Extra
            groups=rule.get("groups", []),
            decoder=source.get("decoder", {}).get("name"),
            full_log=source.get("full_log"),

            # Timestamp
            timestamp=source.get("timestamp")
        )