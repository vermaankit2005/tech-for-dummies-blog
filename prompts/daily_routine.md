Daily tech-for-dummies post — approval-gated, two phases.

Runs every morning at 8:00 AM. The run pauses for human approval between
Phase 1 and Phase 2. Do not skip the approval gate. Do not pre-write the
story before a topic is approved.

================================================================
PHASE 1 — TOPICS (automatic, on wake)
================================================================

1. Read prompts/story_system.md, prompts/topic_system.md,
   prompts/research_system.md.
2. Read state/published_topics.json. Never repeat any published topic
   (same mechanism, moment, or protagonist action — even if reworded).
3. Generate exactly 5 topic candidates per topic_system.md. Each must pass
   all three filter tests and have real numbers/specs available. Do NOT
   research them in depth yet — just enough to confirm the reveal is real.
4. Present the 5 candidates to the user for approval using the
   AskUserQuestion tool, so they surface in the Claude app on the user's
   phone (same logged-in account). For each candidate include: the topic
   line, WHY IT PASSES, THE REVEAL, and the NARRATIVE HOOK, formatted per
   topic_system.md.
5. HALT and wait for the user's selection. Do not proceed to Phase 2 until
   the user picks one of the 5 (or supplies their own via the "Other"
   option). The picked topic is the approved topic.

================================================================
PHASE 2 — RESEARCH + STORY (after the user approves a topic)
================================================================

6. RESEARCH the approved topic. Web-search for real facts — exact latencies,
   protocol names, dates, specs, named people. Minimum 6 verified facts with
   sources. Format per research_system.md.
7. STORY: full draft per story_system.md. Second person, present tense,
   reader-as-protagonist, inline jargon, layered precision, no interest
   labels, no "In this post" opener, no closing summary. 1,500–2,500 words.
   Diagrams only if earned (max 2-3).
8. Render HTML using the same cream-paper template as
   output/what-happens-when-you-type-google.html. Save to
   output/<kebab-case-slug>.html.
9. Append an entry to state/published_topics.json with title, file path,
   today's date (absolute, not relative), and status
   "draft — autonomous, awaiting review".
10. Commit on the master branch and push to origin/master. No feature
    branch. No pull request.
    - Commit subject: "Daily post: <title>".
    - Commit body: the approved topic, the topic-selection reasoning, and
      the 5 candidates that were presented.

================================================================
HUMAN-IN-LOOP — escalate and HALT if any of these trigger
================================================================

- All 5 topic candidates fail the topic_system filter.
- Research yields fewer than 6 verified facts with sources.
- Draft contains [NEEDS RESEARCH: ...] or [VERIFY: ...] markers more than
  twice.
- Topic touches current politics, named living individuals in an
  unflattering light, or active security exploits.
- Commit or push fails.

When a blocker triggers, tell the user via the Claude app (AskUserQuestion or
a plain message that surfaces on their phone) in this format:
"tech-for-dummies blocked: <reason>. Topic: <title>. Decision needed."
Then stop — do not ship.

Phase 1 always pauses for approval. Once a topic is approved and no blocker
triggers, Phase 2 ships silently — the commit + push to master is the signal.
