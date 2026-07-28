import json

from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete

SYSTEM_PROMPT = (
    "You perform GxP risk analysis on a single requirement. Return JSON: "
    '{"severity": "low"|"medium"|"high"|"critical", "likelihood": "low"|"medium"|"high"|"critical", '
    '"rationale": str, "mitigation": str}. Respond with JSON only.'
)


class RiskAnalysis(AICapability):
    def run(self, requirement_text: str, context: str = "") -> dict:
        prompt = f"Requirement: {requirement_text}\n\nProject context: {context}"
        raw = complete(SYSTEM_PROMPT, prompt)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"severity": "medium", "likelihood": "medium", "rationale": raw, "mitigation": ""}
