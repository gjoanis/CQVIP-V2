from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete_json

SYSTEM_PROMPT = (
    "You draft validation protocol test steps that verify a single requirement. "
    "Write concrete, executable test steps with clear, objective expected results. "
    "2-4 steps is usually enough; don't pad the list."
)

SCHEMA = {
    "type": "object",
    "properties": {
        "test_steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "expected_result": {"type": "string"},
                },
                "required": ["description", "expected_result"],
            },
        },
    },
    "required": ["test_steps"],
}


class ProtocolGeneration(AICapability):
    """Drafts test steps for a validation protocol covering a single requirement."""

    def run(self, *, requirement_title: str, requirement_description: str, acceptance_criteria: str = "") -> list[dict]:
        prompt = (
            f"Requirement: {requirement_title}\n"
            f"Description: {requirement_description}\n"
            f"Acceptance criteria: {acceptance_criteria}"
        )
        result = complete_json(
            SYSTEM_PROMPT, prompt, schema=SCHEMA, tool_name="record_test_steps", max_tokens=2048,
        )
        return result.get("test_steps", [])
