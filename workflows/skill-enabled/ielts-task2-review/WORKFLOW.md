# IELTS Task 2 Review

> 这是可选推荐用法，不是 Skill 接口契约或强制执行要求。只有用户要求采用该用法时才读取和使用。

## Core Rule

Imitate the teacher's marking style before giving generic IELTS advice. Use the teacher-style guide and the scoring guide as the two authorities:

1. Read `references/teacher_style.md` before reviewing.
2. Read `references/scoring_guide.md` before scoring.
3. Use `references/review_format.md` for the output structure.

## Default Deliverable

Deliver a validated reviewed `.docx` by default. The DOCX is the primary local Agent output, not an optional extra.

1. Extract the prompt and scored essay.
2. Build the teacher-style review plan from the bundled references, the prompt, and the student's essay.
3. Generate the reviewed DOCX with `../../../scripts/workflows/ielts-task2-review/create_review_docx.py`.
4. Validate it with `../../../scripts/workflows/ielts-task2-review/validate_review_docx.py`.
5. Return the absolute path to the final reviewed DOCX. Do not stop after presenting review text or JSON.
6. If validation fails, fix the review plan or document and rerun validation before delivery.

## IELTS Buddy Data Hand-off

When IELTS Buddy Agent API tools are available and the user wants the result saved, first finish the local review and validated DOCX. Then inspect the available capability description.

Only call a data-only writing save/import tool if it persists caller-provided data without running server-side review. The payload should contain the prompt, essay, target band, local score summary, local feedback summary, and reviewed DOCX metadata or link when available.

Do not call `ielts_writing_import_submission` if the manifest says it will run a teacher-style review. Do not call `ielts_writing_submit_revision` if the manifest says it will generate a fresh review. For rewrites, use `../../common/writing-revision-loop/WORKFLOW.md` locally and persist only caller-provided revision results.

When the learner asks to keep useful corrections or expressions, follow [批改表达进入词汇本](../references/writing-vocabulary-handoff.md). Select only evidence-backed reusable chunks, show the candidates first, and call `ielts_vocabulary_personal_add` only after explicit confirmation.

## Workflow

1. Identify the Task 2 prompt and the student's essay.
   - Normal DOCX input should be an unreviewed student file containing the prompt, optional outline, and the student's essay.
   - For a `.docx`, first run `../../../scripts/workflows/ielts-task2-review/extract_task2_input.py` to separate the prompt, optional outline, and student essay.
   - Preserve `student_essay_paragraph_indices` from the extraction result and include it in the review plan.
   - Treat short outline bullets after the prompt as planning notes, not as the scored essay.
   - Existing comments, italic rewrites, feedback, or model essays are not expected in normal use. If they are detected, treat them as accidental leftover material only; do not score, rewrite, or copy them as part of the student's essay.
   - For pasted text, separate prompt and essay from headings, blank lines, or explicit labels.
2. Check task fit before polishing language.
   - If the essay content, position, or logic is significantly off-topic, mark this first in comments.
   - Later italic rewrites and the final model essay must redirect the mistaken idea back to the task.
3. Calibrate comment style before writing comments.
   - Use `references/teacher_style.md` for short anchored comments and realistic Band 7.5 rewrites.
   - Use the prompt wording to identify the task type before judging task response.
4. Split the essay into review units.
   - Use sentence-level units when problems are local.
   - Use paragraph-level units when logic, task response, or coherence needs bigger repair.
5. Add teacher-style comments.
   - Comments must be short, Simplified Chinese, practical, and anchored to specific English words or phrases.
   - A non-empty comment target must match text inside the selected student essay paragraph; do not fall back to prompt, outline, or the whole wrong paragraph.
   - Prefer concrete notes: `偏口语`, `重复`, `不自然`, `可以更简洁`, `注意冠词`, `偏题`, `这里太笼统`.
6. Add italic rewrites after the relevant original unit.
   - Rewrites should be concise, formal, natural, and at a stable Band 7.5 standard.
   - Keep rewrites close to the student's intended meaning; avoid making local fixes sound like an over-polished Band 9 sample.
7. Score the student's original essay strictly using `references/scoring_guide.md`.
   - Score with bilingual learner-facing labels: 任务回应 Task Response, 连贯与衔接 Coherence & Cohesion, 词汇资源 Lexical Resource, 语法多样性与准确性 Grammatical Range & Accuracy, and 总分参考 Overall.
   - For this teacher-style educational review, criterion scores and the estimated overall score may use whole or half bands, such as `6`, `6.5`, or `7`. Use `.5` when the original essay sits between adjacent scoring anchors; do not force criterion scores to integers.
   - Do this before giving improvement advice.
8. Give concise Band 7.5 / 8.0-oriented feedback.
   - Separate issues blocking stable Band 7.5 from improvements needed to move toward 8.0.
   - Keep this section short and focused.
9. Write a 250-300 word model essay at a stable Band 8.0 standard.
   - Use exactly four paragraphs:
     1. Introduction: paraphrase the prompt and state the essay's position.
     2. Body paragraph 1.
     3. Body paragraph 2.
     4. Conclusion: begin with `In conclusion`.
   - Leave one blank line between model essay paragraphs in the output DOCX.
   - Align it with the scoring guide.
   - Preserve the student's main position when it is on-topic and defensible.
   - Correct any flawed or off-topic logic from the original draft.
   - It must be strong enough for Band 8.0: a clear and well-developed position, relevant and well-extended support, well-managed cohesion, flexible topic vocabulary, and mostly error-free grammar.
   - Keep it realistic and teacher-like, not an over-polished Band 9 essay.
10. Generate and validate a reviewed `.docx` by default.
   - For input `MyEssay.docx`, output `MyEssay(reviewed).docx` in the same folder unless the user specifies another path.
   - For DOCX input, create the reviewed file by copying the original DOCX first.
   - Write comments directly into the copied original essay paragraphs; do not create a second copy of the student's essay for comments.
   - Anchor comments only inside extracted student essay paragraphs, never inside prompt or outline paragraphs.
   - Insert italic rewrites immediately after the matched original essay paragraph.
   - Keep the original prompt and student essay in place; do not repeat the task prompt.
   - For pasted text, output to the current user's Desktop as `IELTS_Task2_Reviewed_YYYYMMDD_HHMM.docx`.
   - Use Times New Roman for all added review text and comments.
   - Use `Cyber Esme` as the Word comment author.
   - Do not add big visible section headings such as `Task`, `Reviewed Essay`, `Score`, or `Model Essay`.
   - Preserve the original `word/document.xml` root namespace declarations and `mc:Ignorable`; do not leave undeclared prefixes such as `w14`, `w15`, `w16*`, or `wp14`.
   - Insert a page break before the score and feedback page; keep the score lines and `冲刺 Band 7.5 / 8.0` together; insert another page break before the model essay.
   - Never overwrite the original essay unless explicitly requested.
11. Clean up temporary byproducts after a successful review.
   - Delete temporary review plan files such as `review_plan_c17t3.json`.
   - Prefer creating review plans in `/private/tmp` or use `--cleanup-plan` when running `../../../scripts/workflows/ielts-task2-review/create_review_docx.py`.
   - Do not delete source essays, final reviewed `.docx` files, or bundled reference files.

## Bundled Resources

- `references/teacher_style.md`: teacher imitation rules for short anchored comments and rewrites.
- `references/scoring_guide.md`: concise, repository-owned Task 2 scoring guide.
- `references/review_format.md`: canonical reviewed document structure.
- `../../../scripts/workflows/ielts-task2-review/extract_task2_input.py`: extract prompt, optional outline, and student essay from a Task 2 DOCX; it also protects against accidental leftover reviewed content.
- `../../../scripts/workflows/ielts-task2-review/create_review_docx.py`: create a reviewed DOCX from a JSON review plan; DOCX input is copied first, comments are anchored into extracted student essay paragraphs, and score/model sections are appended.
- `../../../scripts/workflows/ielts-task2-review/validate_review_docx.py`: verify comments, italic rewrites, student-essay paragraph comment anchoring when `--input-docx` is supplied, root namespace compatibility, score lines, retained `冲刺 Band 7.5 / 8.0` title, removed old headings, and model essay length/four-paragraph structure.

## JSON Review Plan For DOCX Creation

When using `../../../scripts/workflows/ielts-task2-review/create_review_docx.py`, first produce a JSON file with this shape:

```json
{
  "prompt": "Task prompt",
  "student_essay_paragraph_indices": [12, 14, 16, 18],
  "review_units": [
    {
      "original": "Student sentence or paragraph.",
      "comments": [{"target": "specific phrase", "text": "中文短批注"}],
      "rewrite": "Italic teacher-style improvement."
    }
  ],
  "scores": {
    "任务回应 Task Response": "6.5",
    "连贯与衔接 Coherence & Cohesion": "7",
    "词汇资源 Lexical Resource": "6.5",
    "语法多样性与准确性 Grammatical Range & Accuracy": "6.5",
    "总分参考 Overall": "6.5"
  },
  "score_explanation": ["基于原文证据的简短中文评分说明。"],
  "focus_feedback": ["优先修正语法准确性和自然搭配。"],
  "model_essay": [
    "Paragraph 1: introduction with paraphrase and position.",
    "Paragraph 2: body paragraph 1.",
    "Paragraph 3: body paragraph 2.",
    "Paragraph 4: In conclusion, ..."
  ]
}
```

Scores are teacher-style estimates for the review output, so each criterion and `Overall` may be a whole band or a half band.

Then run:

```bash
python ../../../scripts/workflows/ielts-task2-review/create_review_docx.py review_plan.json --input-docx MyEssay.docx --cleanup-plan
python ../../../scripts/workflows/ielts-task2-review/validate_review_docx.py "MyEssay(reviewed).docx" --input-docx MyEssay.docx
```

For pasted text, omit `--input-docx` and the script will default to the Desktop output path.
If the review plan is a permanent example/reference file, omit `--cleanup-plan`.

## Quality Bar

- The reviewed DOCX must contain real Word comments, not plain bracketed notes.
- At least the most important local issues must be anchored to specific text.
- Italic rewrites must appear after the original unit and be written at a stable Band 7.5 standard.
- The score must evaluate the original essay, not the revised essay.
- The model essay must be exactly 4 paragraphs with one blank line between paragraphs, 250-300 words, and should stand securely at Band 8.0 according to the scoring guide.
- The style should follow `references/teacher_style.md`, not a generic IELTS tutor voice.
- Record locally judged criterion evidence as `rubric` with canonical Writing codes from `../../../scripts/skill-taxonomy.json`; keep band estimates and cited text in event details.
- Temporary files from the review process should be removed after successful validation.
