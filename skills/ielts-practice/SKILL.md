---
name: ielts-practice
description: 读取 IELTS Buddy 公开预测命中并提供对应做题入口；在已授权时也可使用个人题库与练习记录，交接到浏览器完成作答并在完成后复盘。适用于查询最新预测命中、“我要刷题”、继续练习、开始阅读或听力练习，以及完成后的客观题结果复盘。
---

# 雅思刷题练习

默认用简体中文沟通。IELTS Buddy 提供题库事实、练习状态和浏览器链接；本地 Agent 负责决定练什么、解释为什么练，以及完成后的教学复盘。

## 选择工作流

| 需求 | 读取 |
| --- | --- |
| 开始一组题、继续未完成练习、按条件选题 | [浏览器刷题](workflows/browser-practice/WORKFLOW.md) |
| 阅读或听力客观题完成后读取结果、交接精读或精听 | [客观题结果复盘](workflows/objective-result-review/WORKFLOW.md) |

## 执行边界

- 需要 IELTS Buddy 题库、历史或浏览器练习时，先读 [Agent API 配置](references/setup.md) 与 [刷题数据契约](references/practice-contract.md)。
- 查询最新预测命中时，使用包内脚本调用无需 Token 的 `ielts_prep_search`，传入 `{ resourceType: "prediction_hit", subject: <可选科目> }`；不查询或猜测未发布的预测数据。
- 预测命中返回的 `practiceUrl` 是公开做题入口。原样输出为可点击链接，不能创建个人 session 或自行拼接其他 URL。未登录时，网页会先显示登录弹窗；登录完成后自动继续至该题目的开始页。
- 本地 Agent 只能基于返回的事实选择精确 `partId`；不得请求或暗示服务端推荐、匹配题目、诊断薄弱项或生成教学反馈。
- 正式作答、计时、听力播放、草稿保存和答案提交始终在浏览器练习页完成。不要在聊天中复刻整套试题或播放器。
- 只有用户明确要求开始或继续练习时，才调用会创建 session 的 `ielts_practice_start_session`。`launchUrl` 由 IELTS Buddy 后端根据该用户的 session 返回；本地 Agent 不得自行拼接或猜测链接，并应将它输出为可点击的“开始练习”入口。
- 浏览器提交后服务端会写入权威 `practice.attempted` 学习事件。本地 Agent 只读取，不重复推送同一练习事件。
- 已提交的阅读或听力复盘先调用 `ielts_practice_read_review`；它只返回题目结果、作答、答案 key 与按需受限的材料快照。本地 Agent 必须自己定位证据、判断错因和设计训练。
- 阅读、听力的错因讲解由本地 Agent 完成；写作和口语开放题分别交给 `$ielts-writing-review`、`$ielts-speaking-coach`，不能要求服务端代做批改。
