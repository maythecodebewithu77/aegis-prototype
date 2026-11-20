"""
RECOVER Agent — "ScrapLoop"
Given a shortage signal for a component, scans the reverse-logistics /
recovery inventory for certified recoverable substitutes and ranks them
by proximity and condition.
"""
from .llm import explain

_CONDITION_RANK = {"grade a": 2, "grade b": 1}


def _condition_score(condition: str) -> int:
    lc = condition.lower()
    for key, score in _CONDITION_RANK.items():
        if key in lc:
            return score
    return 0


def find_recovery_matches(component_id: str, inventory: list[dict]) -> list[dict]:
    matches = [item for item in inventory if item["component_id"] == component_id]
    matches.sort(key=lambda m: (-_condition_score(m["condition"]), m["distance_km"]))
    return matches


def run(component_id: str, component_name: str, inventory: list[dict], use_llm: bool = False) -> dict:
    matches = find_recovery_matches(component_id, inventory)
    best = matches[0] if matches else None

    result = {
        "component_id": component_id,
        "component_name": component_name,
        "matches_found": len(matches),
        "matches": matches,
        "recommended_match": best,
        "requires_human_approval": best is not None,
    }

    if best:
        prompt = (
            f"In two plain sentences, explain to a procurement officer why AEGIS "
            f"recommends sourcing recovered '{component_name}' units from "
            f"{best['source']}, {best['distance_km']}km away, condition: {best['condition']}."
        )
        result["agent_explanation"] = explain(prompt, use_llm=use_llm) or (
            f"Found {best['quantity']} certified recovered units of {component_name} at "
            f"{best['source']} ({best['distance_km']}km away, {best['condition']}). "
            f"Recommend approving this as an emergency substitute source while primary supply is disrupted."
        )
    else:
        result["agent_explanation"] = f"No certified recoverable substitutes found for {component_name} right now."

    return result
