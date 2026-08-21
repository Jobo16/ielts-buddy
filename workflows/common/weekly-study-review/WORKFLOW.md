# Weekly Study Review

> 这是可选推荐用法，不是 Skill 接口契约或强制执行要求。只有用户要求采用该用法时才读取和使用。

Use this workflow when the learner asks for a weekly review, progress report, plan adjustment, or next-week priorities.

## Inputs

Read the smallest useful set:

- learning-event snapshot and due reviews;
- route progress;
- vocabulary progress;
- completed plan tasks;
- recent mock or practice results;
- Writing and Speaking rubric evidence.

## Workflow

1. State the exact review period.
2. Separate completed activity from demonstrated improvement.
3. Summarize each subject as `improving`, `stable`, `needs evidence`, or `priority`.
4. Identify no more than three recurring canonical skill codes from `../../../scripts/skill-taxonomy.json`.
5. Compare the current week with the preceding comparable period only when both periods contain evidence.
6. Carry overdue reviews forward before adding new work.
7. Produce exactly three next actions with a completion signal and time budget.
8. 有跨 Skill 产物时，按 [证据到下一步](../../skill-enabled/evidence-to-next-action/WORKFLOW.md) 区分已证实问题、待验证线索和下一训练动作。
9. Update a persistent plan only after the learner confirms the proposed changes.

## Output

```text
周期：<start> 至 <end>
本周有效进展：<evidence>
需要继续修复：<up to three patterns>
证据不足：<subjects or skills>
下周三个动作：
1. <task + completion signal + minutes>
2. <task + completion signal + minutes>
3. <task + completion signal + minutes>
```

Do not reward activity volume alone. A completed task is not proof of mastery.
