import json
from pathlib import Path

import anthropic

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
STATE_DIR = Path(__file__).parent.parent / "state"


def suggest_topics(published_topics: list[dict]) -> list[str]:
    client = anthropic.Anthropic()

    system_prompt = (PROMPTS_DIR / "topic_system.md").read_text(encoding="utf-8")

    published_list = "\n".join(
        f"- {t['topic']}" for t in published_topics
    ) if published_topics else "None yet."

    user_message = f"""Suggest 5 topic candidates for the next tech-for-dummies post.

Already published (do not repeat):
{published_list}

Return exactly 5 candidates in the format specified in your instructions."""

    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=2000,
        thinking={"type": "adaptive"},
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        response = stream.get_final_message()

    text = next(
        block.text for block in response.content if block.type == "text"
    )
    return _parse_topics(text)


def _parse_topics(raw: str) -> list[str]:
    lines = raw.strip().split("\n")
    topics = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit() and ". " in line:
            topic = line.split(". ", 1)[1].strip()
            topic = topic.split("\n")[0].strip()
            topics.append(topic)
    return topics[:5] if len(topics) >= 5 else topics


def slugify(topic: str) -> str:
    import re
    slug = topic.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:60]
