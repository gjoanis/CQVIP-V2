from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete_json

SYSTEM_PROMPT = (
    "You extract discrete, testable requirements from a section of a validation "
    "document (URS, FS, DS, ...). Extract every requirement you find in this "
    "section -- do not skip, merge, or summarize. This may be a partial excerpt "
    "of a larger document; only report requirements actually present in the text "
    "given to you."
)

SCHEMA = {
    "type": "object",
    "properties": {
        "requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "req_code": {"type": "string", "description": "e.g. URS-001; omit if the source has none"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "category": {"type": "string"},
                },
                "required": ["title", "description"],
            },
        },
    },
    "required": ["requirements"],
}

# A single extraction call has a bounded output budget (max_tokens), which caps
# how many requirements it can return before the model's response gets cut off
# mid-JSON (Anthropic returns an empty tool_use.input in that case -- silent
# data loss if you don't chunk). Splitting the document into bounded chunks and
# extracting per-chunk keeps each call well within budget regardless of how many
# requirements the overall document contains.
CHUNK_CHARS = 6_000
MAX_OUTPUT_TOKENS = 8_000
MAX_TOTAL_CHARS = 300_000


def _chunk_text(text: str, size: int) -> list[str]:
    text = text[:MAX_TOTAL_CHARS]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            newline = text.rfind("\n", start, end)
            if newline > start:
                end = newline
        chunks.append(text[start:end])
        start = end
    return chunks


def _extract_chunk(chunk: str, *, retry_on_truncation: bool = True) -> list[dict]:
    if not chunk.strip():
        return []
    try:
        result = complete_json(
            SYSTEM_PROMPT, chunk, schema=SCHEMA,
            tool_name="record_requirements", max_tokens=MAX_OUTPUT_TOKENS,
        )
        return result.get("requirements", [])
    except ValueError:
        # Even this chunk was too dense to fit the output budget. Split it once
        # and retry each half rather than losing the whole chunk's requirements.
        if not retry_on_truncation or len(chunk) < 500:
            return []
        mid = len(chunk) // 2
        newline = chunk.rfind("\n", 0, mid)
        if newline > 0:
            mid = newline
        return _extract_chunk(chunk[:mid], retry_on_truncation=False) + _extract_chunk(
            chunk[mid:], retry_on_truncation=False,
        )


class RequirementExtraction(AICapability):
    def run(self, document_text: str) -> list[dict]:
        requirements: list[dict] = []
        for chunk in _chunk_text(document_text, CHUNK_CHARS):
            requirements.extend(_extract_chunk(chunk))
        return requirements
