---
name: ielts-reading-review
description: 说明如何读取 IELTS Buddy 已提交阅读练习的结果与按需材料；不定义证据分析、错因判断或教学方案。
---

# IELTS Buddy 阅读结果接口

本 Skill 只说明已提交练习数据的读取方式。需要账号数据时，先按[Agent API 配置](references/setup.md)绑定并检查能力。

## 接口

| 能力 | 数据 | 调用约束 |
| --- | --- | --- |
| `ielts_review_read_snapshot` | 已提交 session 的题目编号、题型、题干、用户作答、答案 key 与可选材料快照 | 只读取当前账号已提交的 session；仅需要原始材料时传 `includeMaterial:true`。 |
| `ielts_review_recent_activity` | 已提交普通练习和已完成模考科目的摘要及复盘引用 | 先查列表，再将返回的 `reviewTarget` 作为详情工具的 `target`。 |
| `ielts_practice_read_session` | session 状态和浏览器入口 | 仅需核实未提交普通练习时使用。 |

```sh
python3 scripts/ielts_buddy_api.py capabilities
python3 scripts/ielts_buddy_api.py call ielts_review_read_snapshot --json '{"target":{"kind":"practice","sessionId":123},"scope":"incorrect","includeMaterial":true}'
```

## 边界

- 服务端返回事实数据，不定位原文证据、不判断错因、不生成词汇或训练建议。
- 正式作答和提交在浏览器练习页完成。
- `workflows/` 是独立的可选推荐层，不属于本 Skill 的接口契约。

## 列表与详情

查询学习记录分两步：先读取列表摘要，再按需用返回的 `reviewTarget` 调用 `ielts_review_read_snapshot` 查看某次练习或某个已完成模考科目的详情；精听使用 `attemptId` 调用 `ielts_dictation_read_attempt`，未提交普通练习使用 `sessionId` 调用 `ielts_practice_read_session`。不要为了列出记录逐条展开详情。使用前以当前账号的 capabilities 为准。

列表中的 `sessionId` 是练习次数，`partId` 是不同篇目；区分零作答、已作答未提交和已提交，不从部分题目的正确率推算 IELTS 分数。需要完整记录时按 `nextOffset`、`nextCursor` 或 `nextPage` 翻页，直到 `hasMore=false`；空页有后续游标时仍需继续。`observationTruncated=true` 或 `coverage.sourceTruncated=true` 表示数据仍不完整，不得声称查全。计划列表只含摘要，用 `planId` 调用 `ielts_study_plans_get` 获取任务页。
