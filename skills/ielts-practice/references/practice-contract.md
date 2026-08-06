# 刷题数据契约

本地 Agent 是刷题链路的大脑。IELTS Buddy MCP 只提供经过权限控制的数据、状态和链接，不做选题、学习诊断或教学处理。

## 公开预测命中与做题入口

- `ielts-buddy-public` 的 `ielts_prep_search` 可匿名读取已发布的预测命中。查询最新记录时传 `{ resourceType: "prediction_hit", subject: <可选>, limit: <1–8> }`，不要传 `query`、`testDate` 或 `testMonth`。
- 每条返回记录的 `practiceUrl` 是对应题目的公开入口。必须原样输出；它不是 session URL，也不读取、创建或暴露用户练习记录。
- 用户打开 `practiceUrl` 后，已登录则直接进入该题目的开始流程；未登录则先显示登录弹窗，认证成功后自动跳转回来并创建属于该浏览器账号的练习 session。
- 个人题库搜索、未完成 session、结果和学习记录仍使用 OAuth 的 `ielts-buddy` MCP。

## 读取顺序

1. `ielts_practice_recent_activity`：读取近期 session，确认是否有未完成练习。
2. `ielts_learner_read_profile` 或 `ielts_learning_pull_events`：只在需要了解已有学习证据时读取。
3. `ielts_practice_list_taxonomy`：用户提出资料、题型、话题、Part、技能等结构化条件时，先将词语解析成精确 tag id。
4. `ielts_practice_search_parts`：返回最多六个紧凑候选。默认按中性目录顺序返回；本地 Agent 明确决定需要“优先未练”或“最新”时，才传对应参数。结果只给出题目标题、题数、科目、难度、标签、是否练过和更新时间。
5. `ielts_practice_read_part`：只在需要确认某一题组的非答案内容时读取；默认不用于在聊天中展示整套试题。

## 开始与恢复

- 新题：本地 Agent 从候选中自行决定精确 `partId`。用户明确要求开始后，调用 `ielts_practice_start_session({ partId })`，把后端返回的 `launchUrl` 交给用户。
- 未完成题：使用 `ielts_practice_read_session({ sessionId })` 返回的 `launchUrl` 恢复，不要重新创建 session。
- 不知道是否要开始：先给出至多三个候选和选择理由，不创建 session。

## 浏览器入口与登录

- `launchUrl` 只能来自 `ielts_practice_start_session`、`ielts_practice_read_session` 或近期 session 的返回值。本地 Agent 不能用 `partId` 或 `sessionId` 自行构造 URL。
- 本地 Agent 将它作为可点击的“开始练习”或“继续练习”链接输出。链接会进入该 session 的浏览器练习页，而不是题库列表。
- 浏览器已有网站登录态时会直接进入练习；没有登录态时，网站会带着原练习地址跳转登录，登录成功后自动返回。
- MCP OAuth 用于让本地 Agent 调用数据接口；浏览器网页登录态用于访问练习页。两者不是同一份凭证。浏览器必须登录 session 所属的同一账号，服务端才会返回该 session 数据。

## 完成后的事实读取

用户在浏览器提交后，先调用 `ielts_practice_read_session({ sessionId })` 确认状态，再调用 `ielts_practice_read_review({ sessionId, scope: "incorrect" })` 读取错题事实。需要阅读精读或听力精听的原始材料时，才第二次调用并传 `includeMaterial: true`；材料受 `maxMaterialChars` 限制。

`ielts_practice_read_review` 是已提交阅读/听力 session 的数据接口，只返回题目编号、题型、题干、用户作答、答案 key 与可选材料快照。它不定位原文证据、不分类错因、不生成词汇或训练建议。服务端已经写入学习事件；不要再次调用学习事件写入接口记录同一次浏览器练习。

`ielts_practice_submit_session` 仅用于用户直接在对话中提供阅读或听力答案，并明确要求提交客观题答案的少数场景。它不能用于写作或口语反馈。

## 输出要求

每次使用远程数据时，清楚区分事实与本地 Agent 判断：

```text
题库事实：<题组、题数、难度、是否练过>
我的判断：<为什么现在练这一组>
下一步：显示“开始或继续练习”的可点击链接，地址为 <launchUrl>
```

不要把题库、答案、解析、听力文本或音频地址批量导出到聊天或本地文件。
