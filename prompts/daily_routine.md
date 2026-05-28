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
3. Generate exactly 4 topic candidates per topic_system.md. Each must pass
   all three filter tests and have real numbers/specs available. Do NOT
   research them in depth yet — just enough to confirm the reveal is real.
   4 candidates (not 5) is intentional — the mobile approval prompt (AskUserQuestion)
   supports exactly 4 buttons. Fit all candidates into those 4 buttons.
4. Present the 4 candidates to the user for approval using the
   AskUserQuestion tool, so they surface in the Claude app on the user's
   phone (same logged-in account). For each candidate include: the topic
   line and the reveal in the option description. Write a short question
   text naming today's date. The "Other" option is automatic — the user can
   type their own topic there.
5. HALT and wait for the user's selection. Do not proceed to Phase 2 until
   the user picks one of the 4 (or supplies their own via the "Other"
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
   Every [DIAGRAM: ...] marker must be paired with a [MERMAID: ...] block.
8. Render TWO HTML files:

   A. output/<kebab-case-slug>.html — the full cream-paper template
      (same as output/what-happens-when-you-type-google.html). Diagrams
      rendered as CSS/HTML layout components as usual.

   B. output/<kebab-case-slug>-medium.html — Medium-safe HTML only.
      Rules:
      - Allowed tags only: h1, h2, h3, p, blockquote, strong, em, hr,
        ul, ol, li, code, pre, img. No div, no span, no CSS, no style.
      - For each diagram, output this HTML comment block immediately
        followed by a fallback text line:
          <!-- DIAGRAM_START
          <paste the raw Mermaid code here, exactly as written>
          DIAGRAM_END -->
          <p><em>[Diagram: <description>]</em></p>
        The publish script will replace both lines with the rendered image.
      - Pull quotes: use <blockquote><p>...</p></blockquote>
      - Section breaks: use <hr />
      - No title tag — the publish script sends the title separately.
      - End with a Sources section as a <p> block.

9. Append an entry to state/published_topics.json with title, file path
   (the cream-paper .html, not the medium one), today's date (absolute,
   not relative), and status "draft — autonomous, awaiting review".
10. Commit on the master branch and push to origin/master. No feature
    branch. No pull request.
    - Commit subject: "Daily post: <title>".
    - Commit body: the approved topic, the topic-selection reasoning, and
      the 4 candidates that were presented.
11. Publish to Medium as a draft:
    Run: python scripts/publish_to_medium.py \
           output/<kebab-case-slug>-medium.html \
           "<title>"
    The script reads MEDIUM_INTEGRATION_TOKEN from .env, converts the
    Mermaid blocks to mermaid.ink image URLs, and POSTs to the Medium API
    as a draft (not public). It prints the draft URL.
    Notify the user: "Medium draft ready: <draft URL>. Open the Medium app,
    go to your Drafts, review and tap Publish."
    If the script fails (token missing, API error), escalate as a blocker
    using the standard format and HALT.

================================================================
HUMAN-IN-LOOP — escalate and HALT if any of these trigger
================================================================

- All 4 topic candidates fail the topic_system filter.
- Research yields fewer than 6 verified facts with sources.
- Draft contains [NEEDS RESEARCH: ...] or [VERIFY: ...] markers more than
  twice.
- Topic touches current politics, named living individuals in an
  unflattering light, or active security exploits.
- Commit or push fails.
- Medium publish script fails (token missing, API error, network failure).

When a blocker triggers, tell the user via the Claude app (AskUserQuestion or
a plain message that surfaces on their phone) in this format:
"tech-for-dummies blocked: <reason>. Topic: <title>. Decision needed."
Then stop — do not ship.

Phase 1 always pauses for approval. Once a topic is approved and no blocker
triggers, Phase 2 ships silently — the commit + push to master is the signal.
