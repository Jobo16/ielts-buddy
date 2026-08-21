# Diagnostic Baseline

> 这是可选推荐用法，不是 Skill 接口契约或强制执行要求。只有用户要求采用该用法时才读取和使用。

Use this workflow when the learner has no reliable recent evidence or explicitly asks for a level diagnosis. Produce a starting hypothesis, not an official score.

## Required Context

Collect only missing fields:

- IELTS Academic or General Training;
- target band and exam date;
- available study time;
- recent official or mock scores, if any;
- one strongest and one weakest self-reported area.

Self-reports and old scores are context, not mastery evidence.

## Evidence Flow

1. Reuse recent owned practice or mock results before asking for new work.
2. When evidence is missing, choose a small baseline:
   - one objective Listening or Reading part;
   - one Writing paragraph or full answer appropriate to the learner's goal;
   - one Speaking Part 2 answer plus one Part 3 follow-up.
3. Do not run all four sections in one chat unless the learner asks for a full diagnostic.
4. Map every observed issue to `../../../scripts/skill-taxonomy.json`.
5. Record objective evidence as `objective` and locally judged Writing or Speaking evidence as `rubric` with explicit confidence.
6. Mark missing subjects as `unknown`; never convert missing data into a low score.

## Output

```text
当前基线：<subject-level evidence summary>
证据强度：<high/medium/low by subject>
最先补的能力：<canonical skill code + learner-facing label>
今天先做：<one concrete task>
复测时间：<date or condition>
```

End with one action. Hand off to `../../skill-enabled/daily-study-loop/WORKFLOW.md` when the learner wants to start immediately.
