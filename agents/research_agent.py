from pathlib import Path

import anthropic

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def research_topic(topic: str) -> str:
    client = anthropic.Anthropic()

    system_prompt = (PROMPTS_DIR / "research_system.md").read_text(encoding="utf-8")

    tools = [
        {
            "type": "web_search_20250305",
            "name": "web_search",
        }
    ]

    messages = [
        {
            "role": "user",
            "content": f"Research this topic for a tech-for-dummies blog post:\n\n**{topic}**\n\nFollow your instructions exactly. Use web search to find accurate, specific information. Return the structured research notes.",
        }
    ]

    while True:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4000,
            thinking={"type": "adaptive"},
            system=system_prompt,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            text = next(
                (block.text for block in response.content if block.type == "text"),
                "",
            )
            return text

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": block.input.get("query", ""),
                        }
                    )
            messages.append({"role": "user", "content": tool_results})
            continue

        break

    return ""


def extract_outline(research_notes: str) -> dict:
    lines = research_notes.split("\n")
    sections = []
    diagram_hints = []

    in_beats = False
    for line in lines:
        stripped = line.strip()
        if "## Narrative Beats" in stripped:
            in_beats = True
            continue
        if in_beats and stripped.startswith("##"):
            in_beats = False
        if in_beats and stripped.startswith("Beat"):
            beat_name = stripped.split("—")[0].strip() if "—" in stripped else stripped.split(":")[0].strip()
            sections.append(beat_name)

    if not sections:
        sections = ["Opening", "How It Works", "The Reveal", "Closing"]

    return {
        "sections": sections,
        "diagram_hints": diagram_hints,
    }
