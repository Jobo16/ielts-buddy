---
name: ielts-practice
description: 说明如何发现和调用 IELTS Buddy 预测、题库目录、练习记录与结果接口；不定义选题、复盘或教学策略。
---

# IELTS Buddy 练习接口

本 Skill 只说明浏览器练习相关的目录和只读记录接口。个人数据调用前，先按[Agent API 配置](references/setup.md)绑定并检查能力。

## 接口

| 能力 | 数据或动作 | 调用约束 |
| --- | --- | --- |
| `ielts_prediction_search_hits` | 公开预测命中 | 可无需 Token；仅使用已发布的返回记录和可信练习目标。 |
| `ielts_practice_list_taxonomy`、`ielts_practice_search_parts`、`ielts_practice_read_part` | 题库分类、目录和非答案内容 | 不在聊天中复刻完整试题。 |
| `ielts_dictation_search_materials` | 可逐句精听的听力素材目录与 `contentRef` | 只返回素材事实，不创建精听运行或浏览器入口。 |
| `ielts_practice_recent_activity`、`ielts_practice_read_session` | 当前账号 session 状态 | 只读取当前账号数据。 |
| `ielts_practice_read_review` | 已提交 session 的作答、答案 key 和可选材料 | 服务端不提供错因、证据或教学结论。 |

```sh
python3 scripts/ielts_buddy_api.py capabilities
python3 scripts/ielts_buddy_api.py call ielts_practice_search_parts --json '{"subject":"reading","limit":1}'
```

## 边界

- Token 只用于数据接口；浏览器网页登录态只用于练习页面，两者不可互换。
- Agent 不创建、填写或提交正式练习；用户在浏览器刷题中心手动开始、作答和交卷，Agent 在完成后读取权威记录。
- 题库来源只使用 `search_parts` 返回的 `origin.questionBank`、`origin.sourceBook`、`origin.sourceTest` 和 `origin.sourceUnit`；不要从标题或普通标签推断来源。
- 本 Skill 不定义选题、诊断、复盘或学习计划。
- `workflows/` 是独立的可选推荐层，不属于本 Skill 的接口契约。
