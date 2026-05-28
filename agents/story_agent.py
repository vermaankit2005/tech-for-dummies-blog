import json
from pathlib import Path

import anthropic

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def write_draft(topic: str, research_notes: str, outline: dict) -> str:
    client = anthropic.Anthropic()

    system_prompt = (PROMPTS_DIR / "story_system.md").read_text(encoding="utf-8")

    sections_text = "\n".join(f"- {s}" for s in outline.get("sections", []))
    hints_text = "\n".join(f"- {h}" for h in outline.get("diagram_hints", [])) or "None specified."

    user_message = f"""Write the tech-for-dummies blog post draft.

TOPIC: {topic}

RESEARCH_NOTES:
{research_notes}

OUTLINE:
Sections (in order):
{sections_text}

Diagram hints:
{hints_text}

Follow your system prompt exactly. Write the full draft now."""

    full_text = []

    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=6000,
        thinking={"type": "adaptive"},
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for event in stream:
            if hasattr(event, "type") and event.type == "content_block_delta":
                delta = event.delta
                if hasattr(delta, "type") and delta.type == "text_delta":
                    full_text.append(delta.text)

    return "".join(full_text)
