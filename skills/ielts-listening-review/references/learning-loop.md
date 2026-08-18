# Cloud-Backed Learning Loop

The local Agent and the IELTS Buddy web Agent follow the same loop. Authenticated cloud events are the durable learner record. A local Agent keeps a SQLite mirror for fast reads and offline work; the learning policy remains in the Agent.

Use only subjects, subskill codes, and evidence types defined in [skill-taxonomy.json](skill-taxonomy.json). Missing evidence is `unknown`, never a low score.

## Storage Adapter

When a local filesystem and Python 3 are available, use the bundled zero-dependency mirror:

```sh
python3 <skill-dir>/scripts/learning_store.py init
python3 <skill-dir>/scripts/learning_store.py snapshot
python3 <skill-dir>/scripts/learning_store.py next
```

The default database is `~/.ielts-buddy/learning.db`. Set `IELTS_BUDDY_HOME` to move it. Do not edit the SQLite database directly. Pull cloud events before reading a snapshot whenever the Agent API connection is available.

When no local filesystem is available, use cloud events directly:

- `ielts_learning_pull_events`: read events after a cursor.
- `ielts_learning_push_events`: append events idempotently.

The cloud is the authoritative event log, not the learning controller.

## Session Loop

1. Read the current snapshot before proposing work.
2. Handle a due review first.
3. Otherwise target the skill with the lowest supported mastery.
4. With no evidence, use practice Agent API data to suggest a diagnostic listening or reading practice, then include the IELTS Buddy browser route for doing it.
5. Ask one task at a time and use hints before answers.
6. Record the outcome immediately after objective grading or local Agent review.
7. End with one concrete next action; do not produce a dashboard unless asked.

For local objective attempts:

```sh
python3 <skill-dir>/scripts/learning_store.py record-attempt \
  --subject reading \
  --object-type question \
  --object-id <question-id> \
  --skill reading.paraphrase \
  --correct false
```

For locally judged Writing or Speaking evidence, normalize the observed criterion performance to `0..1`, retain the learner-facing band estimate in details, and state confidence:

```sh
python3 <skill-dir>/scripts/learning_store.py record-evidence \
  --subject writing \
  --object-type essay \
  --object-id <essay-id> \
  --skill writing.idea-development \
  --evidence-type rubric \
  --performance 0.72 \
  --confidence medium \
  --details-json '{"criterionScore": 6.5}'
```

Use stable IELTS Buddy question, session, or resource IDs as object IDs. Practice data can be read through Agent API, but timed answering, listening playback, and full question interaction remain browser-first; record outcomes after objective grading or local Agent review rather than recreating the question UI locally. Persistent plans are managed through the dedicated study-plan tools and must not be copied into the learning-event store.

## Evidence Contract

- `objective`: require boolean `correct`; use for answer-key-graded Reading and Listening attempts.
- `rubric`: require normalized `performance` from `0` to `1` and `confidence=low|medium|high`; use for locally judged Writing and Speaking criteria. Rubric evidence is not automatically scheduled as an object review.
- `retrieval`: require `rating=again|hard|good`; use when an item is actively recalled and should enter spaced review.

Do not convert self-reports, task completion, time spent, or model-generated advice into mastery evidence. Store learner-facing scores, error details, and criterion notes in the event payload without using them as separate skill codes.

## Learning Policy

The performance estimate uses the five most recent normalized evidence values with increasing recency weights. Confidence is reported separately from performance and reaches `1.0` after five observations. Fewer than two observations trigger diagnostic practice instead of a mastery claim.

Review intervals are `1, 3, 7, 14, 30, 60, 90` days after consecutive successful retrievals. An incorrect result is due immediately. The Agent may explain these decisions but must not invent extra precision.

Selection order:

1. Overdue or failed review.
2. Diagnostic practice for a low-confidence skill.
3. Lowest-performance skill with sufficient evidence.
4. Diagnostic practice when no evidence exists.

This V1 intentionally uses an explainable model. Do not run BKT, IRT, FSRS parameter optimization, or a separate server-side recommender without sufficient real learner history.

## Default Write Flow

For an authenticated local Agent:

1. Before deriving state, read the local `cloudCursor`, call `ielts_learning_pull_events` until `hasMore=false`, and import each response.
2. Record a new event in the local mirror so an interrupted request cannot lose it.
3. At the end of the current objective grading or local review operation, run `outbox --limit 200` and send the returned `events` unchanged to `ielts_learning_push_events`.
4. After a successful response, run `ack` with every event ID in `acknowledgedEventIds` returned by the server.
5. Pull again before the next state-dependent decision so the local mirror receives the server cursor and events from other devices.

If authentication or connectivity is unavailable, keep events in the outbox and continue locally. Upload them at the next successful connection. Never merge by timestamps or overwrite events: `eventId` makes writes idempotent, and the server cursor defines the shared event order.

## Model Basis

The V1 design adapts three proven open-source patterns:

- DeepTutor: recent evidence with confidence caps and a swappable mastery policy.
- OATutor: prioritize relevant work with the lowest current mastery.
- Learn FASTER and claude-tutor: local learner state, active recall, and spaced review.

The implementation is original and deliberately smaller than those systems.
