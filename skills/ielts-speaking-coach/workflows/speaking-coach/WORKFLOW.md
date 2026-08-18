# Speaking Coach

Default learner-facing coaching language is Simplified Chinese. Keep the learner's answer, corrected English sentences, natural versions, reusable chunks, and IELTS criterion names in English where needed.

## Core Rule

Speaking feedback should protect fluency. Correct the problems that affect IELTS performance, not every minor slip.

## Inputs

Use:

- user-typed answers;
- pasted transcript;
- IELTS Buddy speaking topic/material data;
- the user's target band and part number.

If audio or ASR is unavailable, run typed speaking practice. Do not pretend to assess pronunciation from text.
If the user asks to create or weave topic material before answering, use `../speaking-topic-builder/WORKFLOW.md` first. Do not ask IELTS Buddy to auto-match questions.

## Practice Flow

1. Pick IELTS Speaking Part 1, 2, or 3.
2. Ask one question at a time.
3. Let the user answer fully before correcting.
4. Evaluate in this order:
   - task relevance and idea development;
   - fluency and coherence;
   - lexical resource;
   - grammar range and accuracy;
   - pronunciation only when audio evidence exists.
5. Give a natural alternative answer or sentence upgrade.
6. Add 2-4 reusable chunks.
7. Ask one follow-up question.

Record locally judged criterion evidence as `rubric` using canonical Speaking codes from `../../references/skill-taxonomy.json`. Store the learner-facing band estimate and concrete evidence in event details. Never record `speaking.pronunciation` without audio evidence.

## Feedback Format

Use a short structure:

```text
分数参考: <band or range>
优点: <one concrete point>
先改: <one or two issues>
自然表达版本: <rewritten answer or sentence>
可复用表达: <chunks>
下一题: <question>
```

Keep corrections to the top 3. Track recurring patterns across the session.

## Default Deliverable

Deliver a validated Speaking Report `.docx` by default for a full Part 2 answer, Part 3 answer set, transcript, or mock interview. For one quick Part 1 response, chat feedback is acceptable.

1. Build a speaking report plan from typed answers or transcript data.
2. Generate the DOCX with `scripts/create_speaking_report_docx.py`.
3. Validate it with `scripts/validate_speaking_report_docx.py`.
4. Return the absolute path to the final DOCX.
5. If validation fails, fix the plan and rerun generation plus validation.

## IELTS Buddy Data Hand-off

The local Agent owns speaking scoring, feedback, natural rewrites, chunks, and next questions. Use Agent API only to read topic/material data or save caller-provided summaries and progress. Do not call a tool that asks the server to generate speaking feedback or match questions. 当用户要把本次输出变成后续任务时，交给 `$ielts-study-plan` 的“证据到下一步”；只传递有回答文本或转写支撑的事实。

当学习者明确要求保存本次表达时，读取 [口语表达进入词汇本](../../references/vocabulary-handoff.md)。先给出 2–4 个有原回答证据的候选并等待确认，再调用 `ielts_vocabulary_personal_add`；保存本身不产生复习结果。

## Bundled Resources

- `scripts/create_speaking_report_docx.py`: create a Speaking Report DOCX with criterion scores, answer review, natural rewrites, reusable chunks, recurring patterns, and next questions.
- `scripts/validate_speaking_report_docx.py`: verify required sections, Times New Roman, and plan content.

## JSON Speaking Report Plan

```json
{
  "session_title": "Part 2: Describe a useful website",
  "part": "Part 2",
  "band_estimate": "6.5",
  "overall_feedback": "回答很清楚，但例子需要展开到结果或影响。",
  "criterion_scores": {
    "流利度与连贯性 Fluency and Coherence": {"score": "6.5", "note": "整体清楚，但有少量重复。"},
    "词汇资源 Lexical Resource": {"score": "7", "note": "话题词汇比较到位。"}
  },
  "answers": [
    {
      "question": "Describe a useful website.",
      "answer": "I often use a website for learning English...",
      "feedback": "内容切题，但第二个例子没有展开到具体结果。",
      "natural_version": "I use this website almost every day because it gives me short, practical exercises.",
      "reusable_chunks": ["almost every day", "short, practical exercises"],
      "focus": "把一个例子补到结果或影响。"
    }
  ],
  "recurring_patterns": ["例子经常停在过程，没有说结果。"],
  "next_questions": ["How has this website changed your study habits?"]
}
```

```bash
python scripts/create_speaking_report_docx.py speaking_report_plan.json
python scripts/validate_speaking_report_docx.py ~/Desktop/IELTS_Speaking_Report_YYYYMMDD_HHMM.docx --plan-json speaking_report_plan.json
```

## Borrowed Pattern

This workflow adapts MIT-licensed English Coach and lang-tutor patterns: answer the real request first, keep corrections concise, detect recurring patterns, and separate conversation from language feedback.
