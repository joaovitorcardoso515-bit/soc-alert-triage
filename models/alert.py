from dataclasses import dataclass, field


@dataclass
class Alert:
    # Informações da regra
    rule_id: int
    level: int
    description: str

    # Informações do agente
    agent_id: str | None = None
    agent_name: str | None = None
    agent_ip: str | None = None

    # Informações de rede
    source_ip: str | None = None
    destination_ip: str | None = None
    source_port: str | None = None
    destination_port: str | None = None
    protocol: str | None = None

    # Usuário
    username: str | None = None

    # MITRE ATT&CK
    mitre: dict = field(default_factory=dict)

    # Informações adicionais
    groups: list = field(default_factory=list)
    decoder: str | None = None
    full_log: str | None = None

    # Timestamp
    timestamp: str | None = None

    def is_high_level(self):
        return self.level >= 10

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "level": self.level,
            "description": self.description,

            "agent": {
                "id": self.agent_id,
                "name": self.agent_name,
                "ip": self.agent_ip
            },

            "network": {
                "source_ip": self.source_ip,
                "destination_ip": self.destination_ip,
                "source_port": self.source_port,
                "destination_port": self.destination_port,
                "protocol": self.protocol
            },

            "username": self.username,

            "mitre": self.mitre,

            "groups": self.groups,

            "decoder": self.decoder,

            "full_log": self.full_log,

            "timestamp": self.timestamp
        }

    def has_source_ip(self):
        return self.source_ip is not None

    def has_mitre(self):
        return len(self.mitre.get("id", [])) > 0

    def __str__(self):

        mitre_ids = ", ".join(self.mitre.get("id", [])) or "None"
        mitre_tactics = ", ".join(self.mitre.get("tactic", [])) or "None"
        mitre_techniques = ", ".join(self.mitre.get("technique", [])) or "None"

        groups = ", ".join(self.groups) if self.groups else "None"

        return f"""
================ ALERT ================

Rule
-----
ID: {self.rule_id}
Level: {self.level}
Description: {self.description}

Agent
-----
ID: {self.agent_id}
Name: {self.agent_name}
IP: {self.agent_ip}

Network
-------
Source IP: {self.source_ip}
Destination IP: {self.destination_ip}

Source Port: {self.source_port}
Destination Port: {self.destination_port}

Protocol: {self.protocol}

User
----
{self.username}

Groups
------
{groups}

Decoder
-------
{self.decoder}

MITRE ATT&CK
------------
IDs: {mitre_ids}

Tactics:
{mitre_tactics}

Techniques:
{mitre_techniques}

Timestamp
---------
{self.timestamp}

=======================================
"""