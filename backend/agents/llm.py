"""
Pluggable "agentic reasoning" layer.

Every agent computes its decision with plain, explainable rule-based logic
(see sense.py / adapt.py / recover.py) — that part never depends on an LLM,
so the prototype always works offline and judges can audit the exact reason
for every score.

This module *optionally* asks an LLM to turn that structured result into a
natural-language explanation, which is the "agentic" layer the hackathon
brief asks for. If no API key is configured, every agent already has a
sensible templated fallback string, so nothing breaks in a live demo with
no internet.

To satisfy the "SAP Learning Hub, student edition integration" requirement,
swap the call_anthropic() body below for a call to SAP Generative AI Hub's
prompt endpoint (covered in the "Solve your business problems using prompts
and LLMs in SAP Generative AI Hub" Learning Hub course) — the explain()
function signature stays the same, so nothing else in the codebase changes.
"""
import os

_ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")


def call_anthropic(prompt: str) -> str | None:
    if not _ANTHROPIC_API_KEY:
        return None
    try:
        import anthropic  # pip install anthropic
        client = anthropic.Anthropic(api_key=_ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in msg.content if block.type == "text").strip()
    except Exception as e:  # network issue, bad key, etc. — never crash the demo over this
        print(f"[llm] call failed, falling back to template: {e}")
        return None


def explain(prompt: str, use_llm: bool = False) -> str | None:
    if not use_llm:
        return None
    return call_anthropic(prompt)
