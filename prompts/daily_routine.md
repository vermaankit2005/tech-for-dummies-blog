Daily tech-for-dummies post — autonomous.

1. Read prompts/story_system.md, prompts/topic_system.md, prompts/research_system.md.
2. Read state/published_topics.json. Never repeat any published topic.
3. TOPIC: Generate 5 candidates per topic_system.md. Pick strongest (dual-audience payoff, fresh angle, real numbers exist). Choose autonomously. Log reasoning in commit body.
4. RESEARCH: Web-search real facts — exact latencies, protocol names, dates, specs, named people. Minimum 6 verified facts with sources. Format per research_system.md.
5. STORY: Full draft per story_system.md. Second person, present tense, reader-as-protagonist, inline jargon, layered precision, no interest labels, no "In this post" opener, no closing summary. 1,500–2,500 words. Diagrams only if earned (max 2-3).
6. Render HTML using the same cream-paper template as output/what-happens-when-you-type-google.html. Save to output/<kebab-case-slug>.html.
7. Append entry to state/published_topics.json with title, file path, today's date (absolute, not relative), status "draft — autonomous, awaiting review".
8. Commit + push: subject "Daily post: <title>". Body includes topic-selection reasoning and the 5 candidates considered.

HUMAN-IN-LOOP — send mobile push notification and HALT if any of these trigger:
- All 5 topic candidates fail the topic_system filter
- Research yields fewer than 6 verified facts with sources
- Draft contains [NEEDS RESEARCH: ...] or [VERIFY: ...] markers more than twice
- Topic touches current politics, named living individuals in unflattering light, or active security exploits
- Commit or push fails

Push notification format: "tech-for-dummies blocked: <reason>. Topic: <title>. Decision needed."

No blockers → ship silently. The commit + push is the signal.
