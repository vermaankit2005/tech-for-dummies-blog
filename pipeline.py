#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt

load_dotenv()

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / "state" / "pipeline_state.json"
PUBLISHED_FILE = BASE_DIR / "state" / "published_topics.json"
OUTPUT_DIR = BASE_DIR / "output"

console = Console()

VALID_STATES = [
    "IDLE",
    "TOPIC_PENDING",
    "TOPIC_APPROVED",
    "RESEARCH_DONE",
    "OUTLINE_APPROVED",
    "DRAFT_DONE",
]


def _header(command: str, state: str) -> None:
    console.print(f"[bold][tech-for-dummies pipeline][/bold] {command} — state: [cyan]{state}[/cyan]")


def _ok(msg: str) -> None:
    console.print(f"[green]✓[/green] {msg}")


def _err(msg: str) -> None:
    console.print(f"[red]✗[/red] {msg}")


def _load_state() -> dict:
    if not STATE_FILE.exists():
        return {
            "state": "IDLE", "topic": None, "topic_slug": None,
            "research_notes": None, "outline": None, "draft_path": None,
            "created_at": None, "updated_at": None,
        }
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def _save_state(state: dict) -> None:
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_published() -> dict:
    if not PUBLISHED_FILE.exists():
        return {"published": []}
    return json.loads(PUBLISHED_FILE.read_text(encoding="utf-8"))


def _require_state(current: str, required: str) -> bool:
    if current != required:
        _err(f"Expected state: {required}, current state: {current}")
        return False
    return True


def cmd_status() -> None:
    state = _load_state()
    _header("status", state["state"])
    console.print(f"  Topic:        {state['topic'] or '—'}")
    console.print(f"  Draft:        {state['draft_path'] or '—'}")
    console.print(f"  Last updated: {state['updated_at'] or '—'}")


def cmd_suggest() -> None:
    state = _load_state()
    _header("suggest", state["state"])

    if state["state"] not in ("IDLE", "TOPIC_PENDING"):
        _err(f"Cannot suggest topics in state {state['state']}. Run 'reset' first.")
        return

    published = _load_published()

    with console.status("[bold]Generating topic candidates…[/bold]"):
        from agents.topic_agent import suggest_topics
        topics = suggest_topics(published["published"])

    if not topics:
        _err("No topics returned. Try again.")
        return

    console.print("\n[bold]Topic candidates:[/bold]")
    for i, topic in enumerate(topics, 1):
        console.print(f"  {i}. {topic}")

    console.print()
    choice = Prompt.ask("Pick a topic [1-5] or 'r' to regenerate", default="r")

    if choice.lower() == "r":
        state["state"] = "TOPIC_PENDING"
        _save_state(state)
        console.print("Run [bold]suggest[/bold] again to get new candidates.")
        return

    try:
        idx = int(choice) - 1
        if not (0 <= idx < len(topics)):
            raise ValueError
    except ValueError:
        _err(f"Invalid choice: {choice}")
        return

    from agents.topic_agent import slugify
    topic = topics[idx]
    slug = slugify(topic)

    state["state"] = "TOPIC_APPROVED"
    state["topic"] = topic
    state["topic_slug"] = slug
    state["created_at"] = datetime.now(timezone.utc).isoformat()
    _save_state(state)

    _ok(f"Topic approved: {topic}")
    console.print(f"  Slug: {slug}")
    console.print("\nRun [bold]python pipeline.py research[/bold] to continue.")


def cmd_research() -> None:
    state = _load_state()
    _header("research", state["state"])

    if not _require_state(state["state"], "TOPIC_APPROVED"):
        return

    topic = state["topic"]
    console.print(f"  Topic: {topic}")

    with console.status("[bold]Researching (this may take a minute)…[/bold]"):
        from agents.research_agent import research_topic, extract_outline
        research_notes = research_topic(topic)
        outline = extract_outline(research_notes)

    state["state"] = "RESEARCH_DONE"
    state["research_notes"] = research_notes
    state["outline"] = outline
    _save_state(state)

    console.print("\n[bold]Research notes:[/bold]")
    console.print(research_notes[:2000] + ("…" if len(research_notes) > 2000 else ""))
    console.print("\n[bold]Proposed outline sections:[/bold]")
    for s in outline["sections"]:
        console.print(f"  - {s}")

    _ok("Research complete.")
    console.print(f"\nEdit outline in [bold]state/pipeline_state.json[/bold] if needed.")
    console.print("Then run [bold]python pipeline.py approve-outline[/bold].")


def cmd_approve_outline() -> None:
    state = _load_state()
    _header("approve-outline", state["state"])

    if not _require_state(state["state"], "RESEARCH_DONE"):
        return

    outline = state["outline"]
    console.print("\n[bold]Current outline sections:[/bold]")
    for s in outline.get("sections", []):
        console.print(f"  - {s}")
    hints = outline.get("diagram_hints", [])
    if hints:
        console.print("\n[bold]Diagram hints:[/bold]")
        for h in hints:
            console.print(f"  - {h}")

    console.print()
    choice = Prompt.ask("Approve outline?", choices=["y", "n", "e"], default="y")

    if choice == "n":
        console.print("Outline not approved. Edit state/pipeline_state.json and run approve-outline again.")
        return

    if choice == "e":
        editor = os.environ.get("EDITOR", "notepad")
        os.system(f'{editor} "{STATE_FILE}"')
        state = _load_state()
        outline = state["outline"]
        console.print("\n[bold]Updated outline:[/bold]")
        for s in outline.get("sections", []):
            console.print(f"  - {s}")
        sub = Prompt.ask("Approve?", choices=["y", "n"], default="y")
        if sub == "n":
            console.print("Run approve-outline again when ready.")
            return

    state["state"] = "OUTLINE_APPROVED"
    _save_state(state)

    _ok("Outline approved.")
    console.print("\nRun [bold]python pipeline.py draft[/bold] to write the post.")


def cmd_draft() -> None:
    state = _load_state()
    _header("draft", state["state"])

    if not _require_state(state["state"], "OUTLINE_APPROVED"):
        return

    topic = state["topic"]
    slug = state["topic_slug"]
    research_notes = state["research_notes"]
    outline = state["outline"]

    console.print(f"  Topic: {topic}")

    with console.status("[bold]Writing draft (this takes a few minutes)…[/bold]"):
        from agents.story_agent import write_draft
        draft = write_draft(topic, research_notes, outline)

    draft_path = OUTPUT_DIR / f"{slug}-draft.md"
    OUTPUT_DIR.mkdir(exist_ok=True)
    draft_path.write_text(draft, encoding="utf-8")

    state["state"] = "DRAFT_DONE"
    state["draft_path"] = str(draft_path)
    _save_state(state)

    _ok(f"Draft ready: {draft_path}")
    console.print("\nEdit the draft, then run [bold]python pipeline.py mark-published[/bold].")


def cmd_mark_published() -> None:
    state = _load_state()
    _header("mark-published", state["state"])

    if not _require_state(state["state"], "DRAFT_DONE"):
        return

    published = _load_published()
    published["published"].append({
        "topic": state["topic"],
        "slug": state["topic_slug"],
        "date": datetime.now(timezone.utc).date().isoformat(),
    })
    PUBLISHED_FILE.write_text(json.dumps(published, indent=2, ensure_ascii=False), encoding="utf-8")

    draft_path = state["draft_path"]

    state["state"] = "IDLE"
    state["topic"] = None
    state["topic_slug"] = None
    state["research_notes"] = None
    state["outline"] = None
    state["draft_path"] = None
    state["created_at"] = None
    _save_state(state)

    _ok(f"Marked published: {published['published'][-1]['topic']}")
    console.print(f"  Draft kept at: {draft_path}")
    console.print("\nPipeline is IDLE. Run [bold]python pipeline.py suggest[/bold] for the next post.")


def cmd_reset() -> None:
    state = _load_state()
    _header("reset", state["state"])

    if state["state"] == "IDLE":
        console.print("Already IDLE. Nothing to reset.")
        return

    console.print(f"  Current topic: {state['topic'] or '—'}")
    confirm = Prompt.ask("Reset will discard current post. Confirm?", choices=["y", "n"], default="n")
    if confirm != "y":
        console.print("Reset cancelled.")
        return

    state["state"] = "IDLE"
    state["topic"] = None
    state["topic_slug"] = None
    state["research_notes"] = None
    state["outline"] = None
    state["draft_path"] = None
    state["created_at"] = None
    _save_state(state)

    _ok("Pipeline reset to IDLE.")


COMMANDS = {
    "suggest": cmd_suggest,
    "research": cmd_research,
    "approve-outline": cmd_approve_outline,
    "draft": cmd_draft,
    "mark-published": cmd_mark_published,
    "status": cmd_status,
    "reset": cmd_reset,
}


def main() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[red]✗[/red] ANTHROPIC_API_KEY not set. Create a .env file or set the env var.")
        sys.exit(1)

    if len(sys.argv) < 2:
        console.print("[bold]Usage:[/bold] python pipeline.py <command>")
        console.print(f"Commands: {', '.join(COMMANDS)}")
        sys.exit(1)

    command = sys.argv[1]
    if command not in COMMANDS:
        _err(f"Unknown command: {command}")
        console.print(f"Commands: {', '.join(COMMANDS)}")
        sys.exit(1)

    COMMANDS[command]()


if __name__ == "__main__":
    main()
