class Alert:

    def __init__(
        self,
        rule_id,
        level,
        description,
        agent_id,
        agent_name,
        agent_ip,
        source_ip,
        username,
        mitre,
        timestamp
    ):

        self.rule_id = rule_id
        self.level = level
        self.description = description

        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_ip = agent_ip

        self.source_ip = source_ip
        self.username = username

        self.mitre = mitre

        self.timestamp = timestamp


    def __str__(self):

        return f"""
Alert
------
Rule: {self.rule_id}
Level: {self.level}
Description: {self.description}

Agent:
- ID: {self.agent_id}
- Name: {self.agent_name}
- IP: {self.agent_ip}

Source IP:
{self.source_ip}

User:
{self.username}

MITRE:
{self.mitre}

Time:
{self.timestamp}
"""