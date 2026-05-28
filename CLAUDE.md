# tech-for-dummies blog

Feynman-style tech blog. Dual audience: non-technical readers + engineers. Same post, same words, two layers.

## Every session

1. Read `prompts/story_system.md` first — always. It's the living voice spec.
2. Suggest 5 topics → user picks one
3. Web-search for real numbers (latency, protocol names, exact specs)
4. Write full draft following story_system.md rules exactly — **output HTML only** (no .md file)
5. Run `python scripts/add_diagram_export.py output/<slug>.html` after writing the HTML
6. After review: ask "what was off?" → edit story_system.md → save memory if recurring pattern

## Key files

- `prompts/story_system.md` — THE VOICE. Read before writing anything. Update after each post.
- `prompts/topic_system.md` — topic filter rules
- `prompts/research_system.md` — research output format
- `state/published_topics.json` — topics already published, never repeat
- `output/` — finished HTML posts (the publishing artifact — no .md files)
- `scripts/add_diagram_export.py` — inject "save diagrams as images" button into HTML post
- `scripts/diagram_export_snippet.html` — the snippet itself (reusable)
- `agents/` — topic_agent.py, research_agent.py, story_agent.py (need ANTHROPIC_API_KEY to run)
- `pipeline.py` — full CLI pipeline (dormant until API key added to .env)

## Pipeline status

Agents built but dormant — no API key. Claude runs all 3 agent roles manually each session:
- topic_agent → suggest 5 topics
- research_agent → web search for real facts/numbers
- story_agent → write draft per story_system.md

## story_system.md rules (summary)

- Second person ("you"), present tense
- Reader is protagonist. Their devices are extensions of them ("your browser" not "the browser")
- Inline explanation for every technical term when first introduced
- Layered precision: exact numbers for engineers, story for everyone else
- No interest labels: "interesting", "fascinating", "surprising" — show the thing, cut the label
- No "In this post..." openers. Drop reader mid-scene.
- No summary at end. Story ends when story ends.
- Diagrams only after prose earns them. Max 2-3 per post.
- One failure state mention per post max.

## After each post

Ask user: "What was off?" → edit story_system.md with the fix → update `state/published_topics.json` with new topic.
