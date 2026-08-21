# Reading Review

> 这是可选推荐用法，不是 Skill 接口契约或强制执行要求。只有用户要求采用该用法时才读取和使用。

## Core Rule

Reading review is not answer dumping. First locate evidence and paraphrase. Then explain why the wrong option was attractive.

## Inputs

Use the best available input:

1. `ielts_practice_read_part` plus the user's answers and result.
2. A completed browser session result if IELTS Buddy exposes it.
3. A passage DOCX plus user answers.
4. Pasted passage, questions, answer key, and user answers.

If the passage or answer key is missing, ask for it or provide the browser route. Do not invent official answers.

## Workflow

For each wrong or uncertain item:

1. Identify the exact question type.
2. Locate the evidence sentence or paragraph.
3. Write the paraphrase bridge between question and passage.
4. Explain the trap:
   - synonym mismatch;
   - too broad or too narrow;
   - opposite meaning;
   - true but irrelevant;
   - not given vs false;
   - distractor from nearby text;
   - grammar or reference-chain confusion.
5. Create one micro-drill using the same skill.
6. Record the outcome in the learning loop with a stable question or session ID when available.

Map evidence to canonical codes from `../../../scripts/skill-taxonomy.json`. Use `reading.evidence-location` for locating proof, `reading.paraphrase` for meaning bridges, the specific TFNG or reference-chain code when applicable, and `reading.distractor` only when option elimination caused the miss.

## Default Deliverable

Deliver a validated Reading Evidence Map `.docx` by default when there are 2+ wrong/uncertain items or the user wants a saved artifact. For one quick correction, concise chat is acceptable.

1. Build an evidence-map plan from the passage/practice data and user answers.
2. Generate the DOCX with `../../../scripts/workflows/reading-review/create_reading_evidence_map_docx.py`.
3. Validate it with `../../../scripts/workflows/reading-review/validate_reading_evidence_map_docx.py`.
4. Return the absolute path to the final DOCX.
5. If validation fails, fix the plan and rerun generation plus validation.

Quick chat table:

| Q | Your answer | Correct | Evidence | Paraphrase | Error type |
| --- | --- | --- | --- | --- | --- |

## Bundled Resources

- `../../../scripts/workflows/reading-review/create_reading_evidence_map_docx.py`: create a standalone Evidence Map DOCX from a JSON plan.
- `../../../scripts/workflows/reading-review/validate_reading_evidence_map_docx.py`: verify required sections, table, page break, Times New Roman, and plan content.

## JSON Evidence Map Plan For DOCX Creation

Create a JSON file with this shape:

```json
{
  "source_title": "IELTS Reading Practice",
  "passage_title": "The History of Glass",
  "summary": "Review of wrong and uncertain Reading answers.",
  "items": [
    {
      "question_number": "14",
      "question": "What caused glass production to expand?",
      "question_type": "Short answer",
      "user_answer": "new tools",
      "correct_answer": "technological advances",
      "evidence": "Production expanded as technological advances made glass cheaper and easier to shape.",
      "paraphrase_bridge": "caused production to expand = made glass cheaper and easier to shape",
      "trap": "new tools is too narrow; the sentence refers to broader technological advances.",
      "why_correct": "The answer fits both the meaning and the required noun phrase.",
      "error_type": "too narrow",
      "micro_drill": "Find two phrases in the passage where a broad noun replaces a specific example."
    }
  ],
  "review_prompts": [
    "Before checking options, underline the exact words in the question that need paraphrase."
  ],
  "vocabulary": [
    {
      "phrase": "technological advances",
      "meaning": "技术进步",
      "source_sentence": "Production expanded as technological advances made glass cheaper and easier to shape."
    }
  ]
}
```

Then run:

```bash
python ../../../scripts/workflows/reading-review/create_reading_evidence_map_docx.py evidence_map_plan.json --source-docx Passage.docx
python ../../../scripts/workflows/reading-review/validate_reading_evidence_map_docx.py "Passage(evidence-map).docx" --plan-json evidence_map_plan.json
```

For practice data or pasted text only, omit `--source-docx`; the script writes to the Desktop by default.

## Quality Bar

- Evidence must come from the passage.
- Explanation must show the paraphrase bridge.
- The DOCX must include a compact answer map and item-level analysis.
- Do not reveal answers before a retry if the user is still practicing.
- Do not recreate a timed browser practice locally.
