# Listening Error Review

> 这是可选推荐用法，不是 Skill 接口契约或强制执行要求。只有用户要求采用该用法时才读取和使用。

## Core Rule

Listening playback and dictation input are browser-owned. Local Agent value starts after the attempt: classify errors, build replay targets, and schedule drills.

## Inputs

Use any available combination:

- browser result summary;
- transcript or dictation text;
- user answer and correct answer;
- audio timestamp or section number;
- question type and answer key;
- user-pasted notes from the web session.

If the user only asks to do dictation, provide the listening-dictation route from `../references/browser-routes.md`.

## Error Taxonomy

Classify each miss into the main cause:

- sound discrimination;
- weak form or connected speech;
- spelling;
- singular/plural;
- number, date, or unit;
- word boundary;
- distractor;
- paraphrase;
- grammar fit;
- attention/location loss.

Avoid generic “listen more” feedback.

## Workflow

1. List missed items only.
2. For each item, show correct answer, user answer, error type, and one replay target.
3. Create a 1-2 minute micro-drill:
   - shadow the phrase;
   - spell the answer;
   - distinguish singular/plural;
   - predict answer grammar before replay;
   - identify distractor phrase.
4. Save high-value phrases to vocabulary only when the user asks or when the phrase is clearly reusable.
5. Record learning events after grading.

Map the primary cause to one canonical code from `../../../scripts/skill-taxonomy.json`. Record an objective result for the question and add no more than two supported skill codes; do not turn every surface typo into a separate weakness.

## Default Deliverable

Deliver a validated Listening Error Notebook `.docx` by default when there are 2+ missed items, a full dictation review, or a section review. For one quick miss, concise chat is acceptable.

1. Build an error-notebook plan from transcript/result data.
2. Generate the DOCX with `../../../scripts/workflows/listening-error-review/create_listening_error_notebook_docx.py`.
3. Validate it with `../../../scripts/workflows/listening-error-review/validate_listening_error_notebook_docx.py`.
4. Return the absolute path to the final DOCX.
5. If validation fails, fix the plan and rerun generation plus validation.

## Bundled Resources

- `../../../scripts/workflows/listening-error-review/create_listening_error_notebook_docx.py`: create a Listening Error Notebook DOCX with error map, item analysis, replay plan, micro-drills, and vocabulary.
- `../../../scripts/workflows/listening-error-review/validate_listening_error_notebook_docx.py`: verify required sections, table, Times New Roman, and plan content.

## JSON Error Notebook Plan

```json
{
  "source_title": "IELTS Listening Section 2",
  "section_title": "Community centre booking",
  "summary": "The main issue was plural endings and distractors after correction phrases.",
  "items": [
    {
      "question_number": "12",
      "user_answer": "ticket",
      "correct_answer": "tickets",
      "error_type": "singular/plural",
      "transcript": "You will need to bring your tickets to the entrance.",
      "cause": "The final /s/ was weak but grammatically required by bring your ...",
      "replay_target": "bring your tickets",
      "micro_drill": "Replay the phrase twice and mark whether the answer must be singular or plural before listening again."
    }
  ],
  "review_plan": ["Replay only the target phrases, not the whole audio."],
  "vocabulary": [
    {"phrase": "entrance", "meaning": "入口", "source_sentence": "bring your tickets to the entrance"}
  ]
}
```

```bash
python ../../../scripts/workflows/listening-error-review/create_listening_error_notebook_docx.py listening_error_plan.json
python ../../../scripts/workflows/listening-error-review/validate_listening_error_notebook_docx.py ~/Desktop/IELTS_Listening_Error_Notebook_YYYYMMDD_HHMM.docx --plan-json listening_error_plan.json
```
