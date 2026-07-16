def _format_mitre(mitre) -> str:
    if isinstance(mitre, dict):
        ids = mitre.get("id", [])
        if ids:
            return ", ".join(ids)
        techniques = mitre.get("technique", [])
        if techniques:
            return ", ".join(techniques)
        tactics = mitre.get("tactic", [])
        if tactics:
            return ", ".join(tactics)
        return ""
    return str(mitre) if mitre else ""


def _serialize_ai(ai_result) -> dict | None:
    if not ai_result:
        return None

    if isinstance(ai_result, dict):
        return {
            "summary": ai_result.get("summary"),
            "threat_assessment": ai_result.get("threat_assessment"),
            "reason": ai_result.get("reason"),
            "recommended_actions": ai_result.get("recommended_actions", []),
            "confidence": ai_result.get("confidence"),
        }

    return None


def serialize_alert(entry: dict) -> dict:
    alert = entry["alert"]
    risk = entry["risk"]
    raw = entry.get("raw", {})
    source = raw.get("_source", {})
    data = source.get("data", {})
    rule = source.get("rule", {})
    mitre = alert.mitre

    return {
        "id": entry["id"],
        "timestamp": alert.timestamp,
        "risk": risk["risk"],
        "score": risk["score"],
        "reasons": risk.get("reasons", []),
        "rule_id": alert.rule_id,
        "level": alert.level,
        "description": alert.description,
        "agent": alert.agent_name,
        "agent_id": alert.agent_id,
        "agent_ip": alert.agent_ip,
        "username": alert.username,
        "source_ip": alert.source_ip,
        "destination_ip": data.get("dstip"),
        "src_port": data.get("srcport"),
        "dst_port": data.get("dstport"),
        "mitre": _format_mitre(mitre),
        "mitre_detail": mitre if isinstance(mitre, dict) else {},
        "groups": rule.get("groups", []),
        "decoder": source.get("decoder", {}).get("name"),
        "ai": _serialize_ai(entry.get("ai")),
    }
