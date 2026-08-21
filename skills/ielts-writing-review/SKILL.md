---
name: ielts-writing-review
description: 说明如何读写 IELTS Buddy 当前账号的写作提交与修订记录；不定义审题、评分、批改、改写或教学方案。
---

# IELTS Buddy 写作数据接口

本 Skill 只说明写作数据的读写接口。调用前，先按[Agent API 配置](references/setup.md)绑定并检查能力。

## 接口

| 能力 | 数据或动作 | 调用约束 |
| --- | --- | --- |
| `ielts_writing_read_practice` | 当前账号已保存的写作练习记录 | 仅读取当前账号数据。 |
| `ielts_writing_import_submission` | 保存调用方提供的题目、原文与元数据 | 仅在 capability 描述为数据保存时使用；不调用会触发服务端批改的能力。 |
| `ielts_writing_submit_revision` | 保存调用方提供的修订结果 | 仅在 capability 描述为数据保存时使用；不覆盖原始提交。 |

```sh
python3 scripts/ielts_buddy_api.py capabilities
python3 scripts/ielts_buddy_api.py call ielts_writing_read_practice --json '{}'
```

## 边界

- 仅持久化用户或调用方已提供的事实与内容。
- 本 Skill 不定义审题、评分、批改、改写、表达筛选或后续练习。
- `workflows/` 是独立的可选推荐层，不属于本 Skill 的接口契约。
