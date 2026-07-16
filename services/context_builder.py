class ContextBuilder:

    def build(self, alert, risk):

        return {

            "rule_id": alert.rule_id,
            "level": alert.level,
            "description": alert.description,

            "agent": {
                "id": alert.agent_id,
                "name": alert.agent_name,
                "ip": alert.agent_ip
            },

            "network": {
                "source_ip": alert.source_ip,
                "destination_ip": alert.destination_ip,
                "source_port": alert.source_port,
                "destination_port": alert.destination_port,
                "protocol": alert.protocol
            },

            "user": alert.username,

            "mitre": alert.mitre,

            "groups": alert.groups,

            "risk": risk,

            "timestamp": alert.timestamp
        }