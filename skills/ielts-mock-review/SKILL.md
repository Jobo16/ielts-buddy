---
name: ielts-mock-review
description: 说明如何读取 IELTS Buddy 模考与已提交练习的事实数据；不定义模考解读、诊断或训练优先级。
---

# IELTS Buddy 模考数据接口

本 Skill 只说明模考和练习结果的数据读取。需要账号数据时，先按[Agent API 配置](references/setup.md)绑定并检查能力。

## 接口

| 能力 | 数据 | 调用约束 |
| --- | --- | --- |
| `ielts_mock_list_papers` | 当前账号可见的模考试卷目录 | 按 capability 描述传筛选参数。 |
| `ielts_mock_recent_activity` | 已产生的模考活动事实 | 不将缺失数据补成成绩或趋势。 |
| `ielts_practice_read_review` | 已提交客观题 session 的结果和可选材料 | 仅用于精确的已提交 session。 |

```sh
python3 scripts/ielts_buddy_api.py capabilities
python3 scripts/ielts_buddy_api.py call ielts_mock_recent_activity --json '{}'
```

## 边界

- 返回的数据不是 IELTS 官方成绩。
- 本 Skill 不生成能力判断、修复任务或后续计划。
- `workflows/` 是独立的可选推荐层，不属于本 Skill 的接口契约。
