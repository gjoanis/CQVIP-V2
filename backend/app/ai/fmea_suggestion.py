from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete_json

SYSTEM_PROMPT = (
    "You are a quality/reliability engineer performing a Process Failure Mode "
    "and Effects Analysis (PFMEA) for a GxP-regulated manufacturing process. "
    "Given one process step within a named system, identify the single most "
    "significant potential failure mode, its effect on the process, product "
    "quality, or patient safety, its most likely root cause, and the current "
    "detection/prevention controls that would typically already exist. Rate "
    "Severity, Occurrence, and Detection each on the standard AIAG/VDA 1-10 "
    "scale adapted for pharma manufacturing (Severity: 1 = no effect, 10 = "
    "hazardous without warning; Occurrence: 1 = failure unlikely, 10 = failure "
    "almost inevitable; Detection: 1 = controls almost certain to detect the "
    "failure before it causes harm, 10 = no known controls can detect it). "
    "Also recommend one concrete corrective action to reduce the risk."
)

SCHEMA = {
    "type": "object",
    "properties": {
        "potential_failure_mode": {"type": "string"},
        "potential_effect": {"type": "string"},
        "potential_cause": {"type": "string"},
        "current_controls": {"type": "string"},
        "severity": {"type": "integer", "minimum": 1, "maximum": 10},
        "occurrence": {"type": "integer", "minimum": 1, "maximum": 10},
        "detection": {"type": "integer", "minimum": 1, "maximum": 10},
        "recommended_action": {"type": "string"},
    },
    "required": [
        "potential_failure_mode", "potential_effect", "potential_cause", "current_controls",
        "severity", "occurrence", "detection", "recommended_action",
    ],
}


class FmeaSuggestion(AICapability):
    def run(self, *, process_step: str, system_name: str = "") -> dict:
        prompt = f"System/Process: {system_name}\nProcess step: {process_step}"
        return complete_json(
            SYSTEM_PROMPT, prompt, schema=SCHEMA,
            tool_name="record_fmea_suggestion", max_tokens=1024,
        )
