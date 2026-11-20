"""
SENSE Agent — "GhostSupplier"
Infers hidden Tier-2/3 supplier concentration risk for a given component,
and cross-references live disruption signals against those hidden suppliers.

This is intentionally rule-based + explainable rather than a black-box model:
judges (and your own team, debugging at 2am) can see exactly why a score
came out the way it did. Swap in a real ML/graph model later if you have time.
"""
from typing import Optional
from .llm import explain


def _risk_band(score: int) -> str:
    if score >= 70:
        return "HIGH"
    if score >= 35:
        return "MEDIUM"
    return "LOW"


def assess_component_risk(component: dict, disruption_signals: list[dict]) -> dict:
    """
    Walks the Tier-1 -> Tier-2 supplier chain for a component, and scores
    concentration risk: a component that leans heavily on one hidden Tier-2
    supplier is riskier than one that is diversified, and that risk is
    compounded if that hidden supplier currently has an active disruption
    signal against it.
    """
    findings = []
    max_score = 0

    for t1 in component.get("tier1_suppliers", []):
        for t2 in t1.get("tier2_suppliers", []):
            concentration_score = t2["share_pct"]  # 0-100, higher = more concentrated risk

            active_signal = next(
                (s for s in disruption_signals if s["supplier_id"] == t2["supplier_id"]),
                None,
            )

            score = concentration_score
            reasons = [f"{t2['share_pct']}% of supply for this component traces to a single hidden Tier-2 vendor ({t2['name']}, {t2['region']})."]

            if active_signal:
                severity_bump = {"low": 10, "medium": 25, "high": 40}.get(active_signal["severity"], 15)
                score = min(100, score + severity_bump)
                reasons.append(
                    f"Active disruption signal detected at this hidden vendor: "
                    f"{active_signal['signal'].replace('_', ' ')} "
                    f"({active_signal['severity']} severity, flagged {active_signal['detected_days_ago']}d ago)."
                )

            findings.append({
                "tier1_supplier": t1["name"],
                "tier2_supplier": t2["name"],
                "tier2_region": t2["region"],
                "concentration_pct": t2["share_pct"],
                "active_disruption": active_signal,
                "risk_score": score,
                "risk_band": _risk_band(score),
                "reasons": reasons,
            })
            max_score = max(max_score, score)

    return {
        "component_id": component["component_id"],
        "component_name": component["name"],
        "overall_risk_score": max_score,
        "overall_risk_band": _risk_band(max_score),
        "hidden_tier_findings": findings,
    }


def run(component: dict, disruption_signals: list[dict], use_llm: bool = False) -> dict:
    result = assess_component_risk(component, disruption_signals)
    summary_prompt = (
        f"In two plain sentences, explain to a non-technical supply officer why "
        f"component '{result['component_name']}' has a {result['overall_risk_band']} "
        f"hidden-supplier risk score of {result['overall_risk_score']}/100. "
        f"Findings: {result['hidden_tier_findings']}"
    )
    result["agent_explanation"] = explain(summary_prompt, use_llm=use_llm) or (
        f"This component's supply is concentrated in a small number of hidden Tier-2 vendors, "
        f"and {result['overall_risk_band'].lower()}-severity disruption signals are currently active "
        f"against at least one of them. Recommend reviewing diversification before this reaches Tier-1."
        if result["overall_risk_band"] != "LOW"
        else "No significant hidden-tier concentration or disruption risk detected for this component right now."
    )
    return result
