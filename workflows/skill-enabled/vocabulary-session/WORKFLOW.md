# Vocabulary Session

> 这是可选推荐用法，不是 Skill 接口契约或强制执行要求。只有用户要求采用该用法时才读取和使用。

## Core Rule

Vocabulary practice is local-first and data-backed. The service prepares cards and stores progress; the Agent runs recall, hints, feedback, and session pacing.

## Start

1. Read `../../../skills/ielts-vocabulary-coach/references/vocabulary.md`.
2. Choose source:
   - built-in wordbook: `core`, `listening`, or `reading`;
   - personal vocabulary book;
   - weak words from recent practice.
3. Call `ielts_vocabulary_builtin_prepare_cards` for a built-in wordbook, or `ielts_vocabulary_personal_prepare_cards` for My Vocabulary Book. Use a small limit, usually 5-10.
4. Avoid recent repeats with `excludeRecentlyReviewedDays` unless the user asks for due review.
5. Do not provide the web vocabulary-practice link unless the user explicitly asks for the web UI.

## 错题词汇

当用户说“把这次错题里的词收一下”“用刚才阅读/听力的词练我”时：

1. 确认已提交的 `sessionId`，或读取近期练习让用户确认；不要猜测来源。
2. 调用 `ielts_practice_read_review({ sessionId, scope: "incorrect", includeMaterial: true })`。
3. 本地 Agent 从错题题干、答案句与证据桥中选择 3–5 个可迁移词或词块；不要按字面把所有生词收进来。
4. 先按本工作流逐张进行主动回忆。每张卡都说明它与哪道错题有关。
5. 只有用户明确要求保存时，调用 `ielts_vocabulary_personal_add`，并保留来源：

```text
sourceType: practice
sourceId: practice_session:<sessionId>
sourceTitle: <session title>
context: <必要的题目或原文短句>
```

6. 对已保存且本轮回答过的个人词汇，使用 `ielts_vocabulary_personal_record_review` 写入 `again`、`hard` 或 `good`。不要把“已加入词汇本”当作掌握。

## Card Modes

Rotate modes to avoid passive recognition:

1. Recognition: English phrase to Chinese meaning.
2. Production: Chinese meaning or context to English phrase.
3. Cloze: fill the missing word in a sentence.
4. Collocation: choose or produce the natural partner word.
5. IELTS reuse: write one IELTS-style sentence.

Prefer production and cloze for words already seen before. Use recognition for new words.

## Per-Card Flow

1. Show one card only.
2. Ask for an answer before revealing the meaning.
3. If the answer is wrong or weak, give one hint before the full answer.
4. After the answer, give concise feedback:
   - correct form;
   - meaning in the current context;
   - one collocation or reusable chunk;
   - one common confusion if useful.
5. Record review with `ielts_vocabulary_builtin_record_review` for a built-in card or `ielts_vocabulary_personal_record_review` for a personal card:
   - `good`: correct without meaningful help;
   - `hard`: partly correct, slow, or needed a hint;
   - `again`: wrong after hint or unable to recall.

Batching the chat UI is acceptable, but never wait until the end to record outcomes if the client allows reliable writes per card.

## Session Summary

End with:

```text
本轮：<N> 个词
掌握：<words>
需要复习：<words>
下次优先：<wordbook/mode>
```

Do not inflate mastery from one correct answer. Use review history.

## Weekly Vocabulary Sheet

When the user asks for a weekly vocabulary review, printable sheet, or study report, deliver a validated Vocabulary Weekly Sheet `.docx`.

1. Read progress with the matching `ielts_vocabulary_builtin_progress` or `ielts_vocabulary_personal_progress`, and prepare representative words with the matching card tool if needed.
2. Build a weekly sheet plan.
3. Generate the DOCX with `../../../scripts/workflows/vocabulary-session/create_vocabulary_weekly_sheet_docx.py`.
4. Validate it with `../../../scripts/workflows/vocabulary-session/validate_vocabulary_weekly_sheet_docx.py`.
5. Return the absolute path to the final DOCX.

## Bundled Resources

- `../../../scripts/workflows/vocabulary-session/create_vocabulary_weekly_sheet_docx.py`: create a vocabulary sheet with progress snapshot, word table, weak words, due reviews, and practice prompts.
- `../../../scripts/workflows/vocabulary-session/validate_vocabulary_weekly_sheet_docx.py`: verify required sections, tables, Times New Roman, and plan content.

## JSON Weekly Sheet Plan

```json
{
  "week_title": "2026-07-14 Week",
  "wordbook": "IELTS Core",
  "summary": "Most weak words are academic verbs used in Reading passages.",
  "stats": {"reviewed": 24, "mastered": 8, "weak": 5},
  "words": [
    {
      "phrase": "contribute to",
      "meaning": "促成；有助于",
      "learning_state": "review",
      "last_rating": "hard",
      "next_review_at": "2026-07-15",
      "example": "Public transport can contribute to lower emissions."
    }
  ],
  "weak_words": [{"phrase": "whereas", "problem": "Meaning confused with where", "fix": "Use it for contrast."}],
  "due_reviews": [{"phrase": "contribute to", "due_at": "2026-07-15", "mode": "production"}],
  "practice_prompts": ["Use three weak words in one Task 2 body paragraph."]
}
```

```bash
python ../../../scripts/workflows/vocabulary-session/create_vocabulary_weekly_sheet_docx.py vocabulary_weekly_plan.json
python ../../../scripts/workflows/vocabulary-session/validate_vocabulary_weekly_sheet_docx.py ~/Desktop/IELTS_Vocabulary_Weekly_Sheet_YYYYMMDD_HHMM.docx --plan-json vocabulary_weekly_plan.json
```

## Borrowed Pattern

This workflow adapts MIT-licensed Fluent vocabulary-drill ideas: active recall, rotating prompt types, immediate feedback, and spaced-review write-back. IELTS Buddy replaces Fluent's local JSON databases with cloud-backed wordbook progress.
