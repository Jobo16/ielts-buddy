# Mock Test Review

> 这是可选推荐用法，不是 Skill 接口契约或强制执行要求。只有用户要求采用该用法时才读取和使用。

Use this workflow after a completed IELTS mock test. The browser owns timing, media playback, answer entry, and submission; the local Agent owns evidence review and remediation.

## Inputs

Use owned session data or learner-provided results:

- test type and date;
- section scores and timing;
- question-level answers for objective sections;
- Writing answers and Speaking transcript or audio evidence;
- interruptions or invalid sections that affect interpretation.

## Workflow

1. Verify which sections are complete and comparable.
2. Calculate or read section and overall band data without inventing missing components.
3. For Reading and Listening, group misses by canonical skill code and question type.
4. For Writing and Speaking, use local rubric evidence and state confidence; assess pronunciation only from audio evidence.
5. Separate knowledge gaps, strategy errors, and time-management errors.
6. Choose one high-impact repair task per affected subject, capped at three tasks total.
7. Record evidence, then hand off to `$ielts-study-plan` for weekly review or the next daily study action.

## Output

```text
模考结论：<one sentence>
有效分数：<section scores with missing/invalid labels>
主要失分模式：<canonical skills with evidence>
下一轮修复：<up to three tasks>
建议复测：<date or completion condition>
```

Do not treat one mock as a stable level. Compare trends only after comparable attempts exist.
