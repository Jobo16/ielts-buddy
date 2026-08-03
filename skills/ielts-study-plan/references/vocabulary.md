# My Vocabulary Book

IELTS Buddy provides one cloud-backed personal vocabulary book shared by the web Agent, local Agents, and learning modules.

## Personal Vocabulary Tools

- `ielts_vocabulary_personal_list`: search or list saved words and their sources.
- `ielts_vocabulary_personal_progress`: read personal learning-state counts and review progress.
- `ielts_vocabulary_personal_prepare_cards`: prepare data-only flashcards from My Vocabulary Book.
- `ielts_vocabulary_personal_add`: add or enrich words and record where they came from.
- `ielts_vocabulary_personal_import`: import JSON or CSV vocabulary content without review progress.
- `ielts_vocabulary_personal_export`: export JSON or CSV vocabulary content without review progress.
- `ielts_vocabulary_personal_update`: correct one entry or its learning state.
- `ielts_vocabulary_personal_record_review`: record an answered personal card.
- `ielts_vocabulary_personal_delete`: remove one entry after confirmation.

## Built-in Wordbook Tools

- `ielts_vocabulary_builtin_progress`: read progress for a built-in wordbook.
- `ielts_vocabulary_builtin_prepare_cards`: prepare built-in cards.
- `ielts_vocabulary_builtin_record_review`: record an answered built-in card.

When the user asks to remember or collect a word or phrase, save it with `ielts_vocabulary_personal_add`. Use `sourceType=agent` for direct conversation additions; use a more specific source such as `practice`, `course`, `reading_lexicon`, `writing_review`, or `speaking_feedback` when known. Include `sourceId`, `sourceTitle`, and the source sentence when available.

Words are deduplicated case-insensitively. Adding an existing phrase enriches its metadata and records another source instead of creating a duplicate.

For local flashcard practice, choose one source and call `ielts_vocabulary_personal_prepare_cards` or `ielts_vocabulary_builtin_prepare_cards`. Return the card data in the conversation. Do not provide a browser link unless the user explicitly asks to open the web app.

For an interactive local session, use the installed `$ielts-vocabulary-coach` Skill: one card at a time, active recall before reveal, concise feedback, and the matching personal or built-in review tool after each answered card.

Common local-card inputs:

- “给我 10 个核心词，不要和上次重复”：`source=builtin`, `setId=core`, `limit=10`, `mode=mixed`, `excludeRecentlyReviewedDays=7`.
- “听力词书新词”：`source=builtin`, `setId=listening`, `mode=new`.
- “阅读词书复习到期词”：`source=builtin`, `setId=reading`, `mode=due`.
- “复习我的错词/弱词”：use `mode=weak`; choose `source=builtin` for built-in wordbooks or `source=personal` for My Vocabulary Book.

After each answered card, keep the source unchanged: call `ielts_vocabulary_builtin_record_review` with `setId` and `entryId`, or `ielts_vocabulary_personal_record_review` with `id`. Do not pick a fresh random batch from `ielts_vocabulary_personal_list` alone, because that ignores review history and can repeat the same words.

Import and export are content-transfer operations only. Never import, export, invent, or infer FSRS state, mastery, due dates, or review history. Run them only when the user explicitly requests the transfer.

The built-in core, listening, and reading word books are read-only study content. “My Vocabulary Book” is the user's writable collection and is the destination for words produced by all other modules and Agents.
