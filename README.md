# tech-for-dummies

A Feynman-style tech blog. One post, two audiences — non-technical readers get the story, engineers get the precision underneath. Same words, different layers.

## Posts

| Title | Status |
|-------|--------|
| [What Happens When You Type google.com](output/what-happens-when-you-type-google.html) | Draft |
| [Why a Torn QR Code Still Scans](output/why-a-torn-qr-code-still-scans.html) | Draft |

## How it works

Each post is written in three stages:

1. **Topic** — filtered against published topics, chosen for dual-audience potential
2. **Research** — real numbers, real protocol names, exact specs (no vague analogies without data)
3. **Story** — written per `prompts/story_system.md`: second person, present tense, reader as protagonist

## Running the pipeline

Requires `ANTHROPIC_API_KEY` in `.env`:

```bash
cp .env.example .env
# add your API key to .env

pip install -r requirements.txt
python pipeline.py
```

Without an API key, the agents can be run manually — see `agents/` for `topic_agent.py`, `research_agent.py`, `story_agent.py`.

## Structure

```
agents/          # topic, research, story agents
output/          # published HTML posts
prompts/         # voice spec (story_system.md), topic rules, research format
state/           # published topics tracker, pipeline state
pipeline.py      # end-to-end CLI
```
