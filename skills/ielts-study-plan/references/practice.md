# Practice

IELTS question answering is browser-first, not browser-only. Use MCP for question-bank data, session metadata, and recent activity when available; always include a browser link so the learner can do the interactive work in IELTS Buddy.

Default route:

```text
https://ieltsbuddy.igocn.cn/practice
```

## Data And Link Flow

1. If the user asks to 刷题, 做练习, 开始阅读/听力/口语/写作练习, or continue a practice session, first decide whether data would help them choose or resume work.
2. When MCP is configured, use `ielts_practice_list_taxonomy`, `ielts_practice_search_parts`, `ielts_practice_read_part`, or `ielts_practice_recent_activity` to return a compact data summary: subject, part title, difficulty, tags, available count, recent status, or next launch input.
3. Include the stable practice URL or the launch URL/session route returned by `ielts_practice_start_session`.
4. Do not force the browser if a data answer is enough, such as “what should I practice next?” or “show me available reading parts.” Do not force local execution for timed answering, audio playback, or a full answer sheet.
5. If MCP is unavailable, say the data interface requires the IELTS Buddy MCP connection and still provide the browser route.
6. If the current client can open browser links and the user asked to open it, open the URL. Otherwise return the link.

## Local Review Boundary

Use `local-agent-runtime.md` for any practice result that requires teaching judgment.

- Reading/listening objective questions: use answer keys or returned graded results as data, then explain errors with the installed `$ielts-reading-review` or `$ielts-listening-review` Skill.
- Writing/speaking open-ended answers: do not submit through MCP for server-side feedback. Use `$ielts-writing-review` or `$ielts-speaking-coach`.
- If the learner gives answers in chat, the Agent may review them locally. Only write back caller-provided results, scores, summaries, and events.

## MCP Interfaces

Use these as the data interface before or alongside the browser link:

- `ielts_practice_list_taxonomy`: list subjects, question types, filters, tags, difficulty values, and availability counts.
- `ielts_practice_search_parts`: search available parts before suggesting what to open.
- `ielts_practice_read_part`: read one part's metadata and non-answer content, then return the browser route or start-session input.
- `ielts_practice_start_session`: create a cloud practice session and return its browser launch route when available.
- `ielts_practice_recent_activity`: read recent activity for reflection or planning.
- `ielts_practice_read_session`: inspect an owned session's compact status and browser route, not to replace the web practice UI.
- `ielts_practice_read_review`: read stored objective results, answers, answer keys, and an opt-in bounded material snapshot for a submitted Reading or Listening session; the local Agent performs diagnosis and teaching.
- `ielts_practice_submit_session`: use only for objective reading/listening answer-key grading when the user explicitly supplied answers and asked the Agent to submit through MCP. Do not use it to trigger writing or speaking feedback.

Use recent activity and learner events to identify patterns, but do not claim a weakness from one isolated answer. After an objective graded result or local open-ended review, record each meaningful outcome and complete the default cloud write flow in [learning-loop.md](learning-loop.md). The Agent owns remediation and review timing; IELTS Buddy does not create a separate adaptive session.
