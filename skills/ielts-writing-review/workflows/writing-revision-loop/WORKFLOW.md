# Writing Revision Loop

## Core Rule

The first review is not the finish line. The value is whether the learner can revise and avoid repeating the same errors.

## Inputs

Use one of:

1. Original reviewed DOCX from `ielts-task1-review` or `ielts-task2-review` plus a revised answer.
2. Original prompt, original essay, review notes, and revised essay.
3. Read-only IELTS Buddy writing record data plus a revised answer, if the record was already created elsewhere.

Do not rescore the revised essay before checking whether the original priority comments were fixed.
Do not call a server-side “fresh review” or “submit revision for feedback” tool. The revision check is local Agent work.

## Workflow

1. Read the original review's major comments, score blockers, and model answer.
2. Compare the revised answer against the original answer.
3. Mark each original issue:
   - fixed;
   - improved but still weak;
   - unchanged;
   - worsened;
   - no longer relevant.
4. Identify new problems introduced by the revision.
5. Give a new band estimate only after the fix-check.
6. Create one next rewrite target, not a full new essay plan unless asked.
7. Record recurring writing errors into the learning loop.

Use the same canonical Writing codes as the first review. Record a new rubric observation only when the revision provides direct evidence; task completion alone is not evidence of improvement.

## Default Deliverable

Deliver a validated revision-report `.docx` by default. The DOCX is the primary local Agent output.

1. Build a revision plan from the original review and revised answer.
2. Generate the report with `scripts/create_revision_report_docx.py`.
3. Validate it with `scripts/validate_revision_report_docx.py`.
4. Return the absolute path to the final DOCX.
5. If validation fails, fix the plan and rerun generation plus validation.

For quick chat-only use, summarize with this shape:

```text
Fixed: <issues>
Still weak: <issues>
New issue: <issue>
Band movement: <old estimate -> new estimate>
Rewrite target: <one concrete instruction>
```

## Relation To Existing Workflows

Use the existing Task 1 and Task 2 review workflows for first-pass correction. This workflow starts only after the learner submits a revision.

## IELTS Buddy Data Hand-off

After the revision report is generated and validated, persist only caller-provided results when a data-only Agent API tool exists: revised answer, fixed/unchanged issue summary, local score movement, next rewrite target, and artifact metadata.

If the available Agent API revision tool says it will generate a fresh review, skip the write-back and return the local DOCX. Never overwrite the original reviewed DOCX.

## Bundled Resources

- `scripts/create_revision_report_docx.py`: create a revision-report DOCX from a JSON plan. It includes a fix-check table, score movement, new issues, revised answer, next rewrite target, and micro-drills.
- `scripts/validate_revision_report_docx.py`: verify required sections, tables, page breaks, Times New Roman, and plan content.

## JSON Revision Plan For DOCX Creation

Create a JSON file with this shape:

```json
{
  "task_type": "Task 2",
  "prompt": "Task prompt",
  "original_band": "6.5",
  "revised_band": "7.0",
  "overall_judgement": "The revision fixes the main task-response issue but still needs tighter paragraph progression.",
  "fix_checks": [
    {
      "issue": "The original introduction did not state a clear position.",
      "status": "fixed",
      "evidence": "The revised introduction now says ...",
      "comment": "Clearer and more examiner-friendly."
    },
    {
      "issue": "Body paragraph 2 used vague support.",
      "status": "improved",
      "evidence": "The example is more specific, but the explanation stops early.",
      "comment": "Extend the consequence by one sentence."
    }
  ],
  "criterion_scores": {
    "Task Response": {"before": "6.5", "after": "7", "note": "Position and support are clearer."},
    "Coherence & Cohesion": {"before": "6.5", "after": "6.5", "note": "Progression still needs work."},
    "Lexical Resource": {"before": "7", "after": "7", "note": "Mostly stable."},
    "Grammatical Range & Accuracy": {"before": "6.5", "after": "6.5", "note": "Some article and clause errors remain."},
    "Overall": {"before": "6.5", "after": "7", "note": "Borderline improvement."}
  },
  "new_issues": [
    {"issue": "New repetition", "evidence": "important ... important", "fix": "Replace the second use with a precise synonym."}
  ],
  "revised_essay": ["Paragraph 1", "Paragraph 2", "Paragraph 3", "Paragraph 4"],
  "next_rewrite_target": "Rewrite body paragraph 2 with one concrete example and one consequence sentence.",
  "micro_drills": ["Write three consequence sentences using therefore / this means / as a result."]
}
```

Then run:

```bash
python scripts/create_revision_report_docx.py revision_plan.json --source-docx "MyEssay(reviewed).docx"
python scripts/validate_revision_report_docx.py "MyEssay(revision-report).docx" --plan-json revision_plan.json
```

For pasted text only, omit `--source-docx`; the script writes to the Desktop by default.

## Quality Bar

- Check old comments before giving a new score.
- Do not praise a revision for adding length if it fails to fix the original issue.
- Separate fixed, improved, unchanged, worsened, and new issues.
- The DOCX must contain a compact fix-check table and a single concrete next rewrite target.
- Do not overwrite the original reviewed DOCX.
