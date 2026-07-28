from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete_json

SYSTEM_PROMPT = (
    "You are a GxP validation engineer assessing a single requirement from a "
    "validation document (URS/FS/DS). Given the requirement's title, "
    "description, and category, assess its risk to product quality/patient "
    "safety/data integrity, identify the most relevant regulatory reference "
    "(e.g. 'EU GMP Annex 15', 'EU GMP Annex 11', 'FDA Part 11', 'ICH Q9(R1)'), "
    "write clear acceptance criteria, suggest a concrete test approach, and "
    "recommend which validation phase (IQ, OQ, or PQ) verifies it."
)

SCHEMA = {
    "type": "object",
    "properties": {
        "risk": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
        "gmp_reference": {"type": "string", "description": "e.g. 'EU GMP Annex 15'"},
        "acceptance_criteria": {"type": "string"},
        "suggested_test": {"type": "string"},
        "protocol_section": {"type": "string", "description": "e.g. 'IQ', 'OQ', 'PQ'"},
        "verification_type": {"type": "string", "description": "e.g. 'IQ', 'OQ', 'PQ'"},
    },
    "required": [
        "risk", "gmp_reference", "acceptance_criteria", "suggested_test",
        "protocol_section", "verification_type",
    ],
}


class RequirementAssessment(AICapability):
    def run(self, *, title: str, description: str, category: str = "") -> dict:
        prompt = f"Title: {title}\nCategory: {category}\nDescription: {description}"
        return complete_json(
            SYSTEM_PROMPT, prompt, schema=SCHEMA,
            tool_name="record_assessment", max_tokens=1024,
        )
