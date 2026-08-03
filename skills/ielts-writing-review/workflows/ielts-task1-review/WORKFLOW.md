# IELTS Task 1 Review

This workflow covers IELTS Academic Writing Task 1 only. Do not apply chart, map, table, or process criteria to General Training letters.

## Core Rule

Analyze the visual prompt before correcting the student's writing. For Task 1, accurate chart/table/map/process understanding is part of Task Achievement, so do not polish language before identifying the main features.

## Default Deliverable

Deliver a validated reviewed `.docx` by default. The DOCX is the primary local Agent output, not an optional extra.

1. Inspect the visual and student answer.
2. Build the teacher-style review plan from the bundled references, the visual facts, and the student's answer.
3. Generate the reviewed DOCX with `scripts/create_and_validate_task1_review.py` for DOCX input, or `scripts/create_task1_review_docx.py` followed by the validator for pasted text.
4. Return the absolute path to the final reviewed DOCX. Do not stop after presenting review text or JSON.
5. If validation fails, fix the review plan or document and rerun validation before delivery.

## IELTS Buddy Data Hand-off

When IELTS Buddy MCP tools are available and the user wants the result saved, first finish the local review and validated DOCX. Then inspect the available capability description.

Only call a data-only writing save/import tool if it persists caller-provided data without running server-side review. The payload should contain the prompt, essay, target band, `visualContext`, local score summary, local feedback summary, and reviewed DOCX metadata or link when available.

Do not call `ielts_writing_import_submission` if the manifest says it will run a teacher-style review. Do not call `ielts_writing_submit_revision` if the manifest says it will generate a fresh review. For rewrites, use `../writing-revision-loop/WORKFLOW.md` locally and persist only caller-provided revision results.

When the learner asks to keep useful corrections or expressions, follow [批改表达进入词汇本](../../references/vocabulary-handoff.md). Select only evidence-backed reusable chunks, show the candidates first, and call `ielts_vocabulary_personal_add` only after explicit confirmation.

Use these references in order:

1. Read `references/visual_analysis_protocol.md` to inspect the visual.
2. Read `references/teacher_style.md` for Task 1 teacher-style marking.
3. Read `references/scoring_guide.md` before scoring.
4. Use `references/review_format.md` for DOCX layout and cleanup rules.

## Workflow

1. Identify the prompt, embedded image, and student answer.
   - For `.docx`, extract embedded images with `scripts/extract_docx_images.py`.
   - Inspect the extracted image directly before reviewing. This is mandatory: never score or rewrite a Task 1 answer from the text alone.
   - For `.docx`, also run `scripts/extract_task1_input.py` so the review plan can distinguish prompt text from student answer paragraphs.
   - For pasted text, require an image attachment or image path.
2. Build an internal visual facts note.
   - Identify visual type, units, categories, time periods, axes, legends, stages, and key values.
   - Identify overview-level features before local details.
   - Keep this note internal unless the user explicitly asks to see it.
3. Check the student's Task Achievement.
   - Mark inaccurate chart type, wrong units, missing overview, wrong key feature selection, inaccurate values, or irrelevant details in comments.
4. Calibrate comment style before writing comments.
   - Use `references/teacher_style.md` for short anchored comments and realistic Band 7.5 rewrites.
   - Classify the new task as bar chart, line graph, table, pie chart, map, process, or mixed visual so the comments target the right Task Achievement issues.
5. Split the answer into review units.
   - Use sentence-level units for grammar, articles, plural forms, data phrasing, collocation, and formal wording.
   - Use paragraph-level units for overview errors, poor grouping, data misreading, map/process sequencing, or missing comparisons.
6. Add teacher-style comments.
   - Use short Simplified Chinese comments anchored to specific English words or phrases.
   - Use comments like `图表类型要写具体：bar chart`, `要说明是比例`, `有点重复`, `更正式`, `这里加逗号`, `这句已经在总览里说过`.
7. Add italic rewrites after relevant units.
   - Rewrites must be concise, formal, data-accurate, and at a stable Band 7.5 standard.
   - Keep rewrites learnable and close to the student's intended meaning; do not turn local fixes into over-complex Band 9 wording.
8. Score the student's original answer strictly using `references/scoring_guide.md`.
   - Score with bilingual learner-facing labels: 任务完成度 Task Achievement, 连贯与衔接 Coherence & Cohesion, 词汇资源 Lexical Resource, 语法多样性与准确性 Grammatical Range & Accuracy, and 总分参考 Overall.
   - For this teacher-style educational review, criterion scores and the estimated overall score may use whole or half bands, such as `6`, `6.5`, or `7`. Use `.5` when the original answer sits between adjacent scoring anchors; do not force criterion scores to integers.
9. Give concise Band 7.5 / 8.0-oriented feedback.
   - Mention blockers preventing stable Band 7.5 first.
   - Then mention the most useful move toward 8.0.
10. Write a 150-200 word model answer at a stable Band 8.0 standard.
   - Use exactly four paragraphs:
     1. Introduction: paraphrase the task prompt.
     2. Overview: begin with `Overall` and summarize the main features.
     3. Body paragraph 1: report the first logical group of details.
     4. Body paragraph 2: report the second logical group of details.
   - Leave one blank line between model answer paragraphs in the output DOCX.
   - Align it with the visual and the scoring guide.
   - Correct any inaccurate visual interpretation.
   - It must be strong enough for Band 8.0: skilful key feature selection, clear overview, logical grouping, precise data language, natural comparisons, well-managed cohesion, and mostly error-free grammar.
   - Keep it realistic and teacher-like, not an over-complex Band 9 answer.
11. Generate and validate a reviewed `.docx` by default.
   - For input `MyAnswer.docx`, output `MyAnswer(reviewed).docx` in the same folder unless the user specifies another path.
   - For DOCX input, create the reviewed file by copying the original DOCX first.
   - Write comments directly into the copied original answer paragraphs; do not create a second copy of the student's answer for comments.
   - Insert italic rewrites immediately after the matched original answer paragraph.
   - Keep the original prompt and embedded visual in place; do not repeat the task prompt or image.
   - For pasted text, output to the current user's Desktop as `IELTS_Task1_Reviewed_YYYYMMDD_HHMM.docx`.
   - Use Times New Roman for all added review text and comments.
   - Use `Cyber Esme` as the Word comment author.
   - Do not include a visible `Visual Facts` section unless the user asks for it or `--include-visual-facts` is intentionally used.
   - Do not add big visible section headings such as `Task`, `Reviewed Answer`, `Score`, or `Model Answer`.
   - Preserve the original `word/document.xml` root namespace declarations and `mc:Ignorable`; do not leave undeclared prefixes such as `w14`, `w15`, `w16*`, or `wp14`.
   - Insert a page break before the score and feedback page; keep the score lines and `冲刺 Band 7.5 / 8.0` together; insert another page break before the model answer.
   - Never overwrite the original answer unless explicitly requested.
12. Clean up temporary byproducts after a successful review.
   - Delete temporary files such as `review_plan_*.json`, extracted scratch images, and unpacked DOCX folders.
   - `scripts/extract_docx_images.py` creates a unique `/private/tmp/ielts_task1_images_*` directory by default; delete that scratch directory after validation.
   - Do not delete source answers, final reviewed DOCX files, or bundled reference files.

## Bundled Resources

- `references/visual_analysis_protocol.md`: checklist for charts, tables, maps, processes, and mixed visuals.
- `references/teacher_style.md`: Task 1 teacher-style rules for concise anchored comments and rewrites.
- `references/scoring_guide.md`: concise, repository-owned Task 1 scoring guide.
- `references/review_format.md`: canonical reviewed document structure.
- `scripts/extract_docx_images.py`: extract visual prompts from new input DOCX files to a unique scratch directory by default.
- `scripts/extract_task1_input.py`: extract prompt, student answer, and student answer paragraph indices from a Task 1 DOCX.
- `scripts/create_task1_review_docx.py`: create a reviewed DOCX from a JSON review plan; DOCX input is copied first, comments are anchored into extracted student answer paragraphs, and score/model sections are appended.
- `scripts/create_and_validate_task1_review.py`: create a reviewed DOCX, validate it, and clean extracted scratch images in one command.
- `scripts/validate_task1_review_docx.py`: verify comments, italic rewrites, student-answer paragraph comment anchoring when `--input-docx` is supplied, root namespace compatibility, page breaks, font, author, score lines, retained `冲刺 Band 7.5 / 8.0` title, removed old headings, and model answer length/four-paragraph structure.

## JSON Review Plan For DOCX Creation

When using `scripts/create_task1_review_docx.py`, first produce a JSON file with this shape:

```json
{
  "prompt": "Task prompt or visual prompt summary",
  "student_answer_paragraph_indices": [4, 6, 8, 10],
  "visual_facts": ["Internal visual facts used for accuracy. These are not shown in the DOCX by default."],
  "review_units": [
    {
      "original": "Student sentence or paragraph.",
      "comments": [{"target": "specific phrase", "text": "中文短批注"}],
      "rewrite": "Italic teacher-style improvement."
    }
  ],
  "scores": {
    "任务完成度 Task Achievement": "6.5",
    "连贯与衔接 Coherence & Cohesion": "7",
    "词汇资源 Lexical Resource": "6.5",
    "语法多样性与准确性 Grammatical Range & Accuracy": "6.5",
    "总分参考 Overall": "6.5"
  },
  "score_explanation": ["基于原文证据的简短中文评分说明。"],
  "focus_feedback": ["优先修正总览准确性和自然比较表达。"],
  "model_answer": [
    "Paragraph 1: introduction/paraphrase.",
    "Paragraph 2: Overall ...",
    "Paragraph 3: first detail group.",
    "Paragraph 4: second detail group."
  ]
}
```

Scores are teacher-style estimates for the review output, so each criterion and `Overall` may be a whole band or a half band.

Then run:

```bash
python scripts/create_task1_review_docx.py review_plan.json --input-docx MyAnswer.docx --cleanup-plan
python scripts/validate_task1_review_docx.py "MyAnswer(reviewed).docx" --input-docx MyAnswer.docx
```

For a DOCX workflow with automatic image scratch cleanup, run:

```bash
python scripts/create_and_validate_task1_review.py review_plan.json --input-docx MyAnswer.docx
```

If the review plan is a permanent example/reference file, omit `--cleanup-plan`. Use `--include-visual-facts` only when the user explicitly asks to see the visual facts note in the reviewed DOCX.

## Quality Bar

- The visual must be inspected before scoring or rewriting.
- Comments must stay within the extracted student answer paragraphs; prompt text and image captions are not valid anchor targets.
- The reviewed DOCX must contain real Word comments, not bracketed notes.
- Important Task Achievement issues must be commented first.
- Italic rewrites must be data-accurate and written at a stable Band 7.5 standard.
- The score must evaluate the original answer.
- The model answer must be exactly 4 paragraphs with one blank line between paragraphs, 150-200 words, and should stand securely at Band 8.0 according to the scoring guide.
- The style should follow `references/teacher_style.md`, not a generic IELTS tutor voice.
- Record locally judged criterion evidence as `rubric` with canonical Writing codes from `../../references/skill-taxonomy.json`; keep band estimates and cited text in event details.
