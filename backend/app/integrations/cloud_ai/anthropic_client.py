from functools import lru_cache

from anthropic import Anthropic

from app.config import get_settings


@lru_cache
def get_anthropic_client() -> Anthropic:
    settings = get_settings()
    return Anthropic(api_key=settings.anthropic_api_key)


def complete(system: str, user: str, *, max_tokens: int = 1024) -> str:
    """One-shot completion helper shared by every app/ai/* capability."""
    settings = get_settings()
    client = get_anthropic_client()
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def complete_json(system: str, user: str, *, schema: dict, tool_name: str = "record_data",
                   max_tokens: int = 8192) -> dict:
    """Structured-extraction variant of complete(): forces the response through a
    tool call matching `schema` instead of asking the model to "return JSON only"
    in free text. Free-text JSON requests are unreliable -- models often wrap the
    output in a ```json fence even when told not to, which breaks naive
    json.loads(). Tool use guarantees a schema-conforming response with no
    prose/markdown to strip.
    """
    settings = get_settings()
    client = get_anthropic_client()
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
        tools=[{"name": tool_name, "description": "Record the extracted data.", "input_schema": schema}],
        tool_choice={"type": "tool", "name": tool_name},
    )
    if response.stop_reason == "max_tokens":
        # The tool call's JSON was cut off mid-generation. The SDK gives back an
        # empty/partial .input for a truncated tool_use block with no other
        # signal -- silently returning that would look like "zero results"
        # instead of "truncated", so raise instead of letting it through.
        raise ValueError(
            f"complete_json response truncated at max_tokens={max_tokens}; "
            "raise max_tokens or send a smaller input chunk"
        )
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    raise ValueError("Model response did not include the expected tool_use block")
