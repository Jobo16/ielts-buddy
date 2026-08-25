---
name: ielts-writing-review
description: 说明如何导入 IELTS Buddy 写作提交、读取不可变版本与教师式批改结果，并提交带新批改的修订版本；不定义本地批改方法。
---

# IELTS Buddy 写作数据接口

本 Skill 只说明写作数据的读写接口。调用前，先按[Agent API 配置](references/setup.md)绑定并检查能力。

## 接口

| 能力 | 数据或动作 | 调用约束 |
| --- | --- | --- |
| `ielts_writing_import_submission` | 导入 Task 1/2 题目与作文，运行教师式批改并返回浏览器结果入口 | 必须传 `taskType`、`prompt`、`essay`；Task 1 应提供必要的 `visualContext`。 |
| `ielts_writing_read_practice` | 指定 `sessionId` 的不可变版本和结构化教师批改结果 | 只读取当前账号数据；使用返回的版本字段陈述事实。 |
| `ielts_writing_submit_revision` | 为指定 session 与 `slotKey` 提交新作文版本并生成新的批改与问题解决证据 | 新增不可变版本，不覆盖原始提交。 |

```sh
python3 scripts/ielts_buddy_api.py capabilities
python3 scripts/ielts_buddy_api.py call ielts_writing_read_practice --json '{"sessionId":123}'
```

## 边界

- `import_submission` 和 `submit_revision` 都会触发服务端教师式批改；若调用方已经完成本地批改且不希望重复批改，不要把它们当成纯保存接口。
- 本 Skill 只定义服务端写作练习接口，不规定本地审题、评分、改写或后续练习流程。
- `workflows/` 是独立的可选推荐层，不属于本 Skill 的接口契约。
