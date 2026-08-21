# 练习 API 数据契约

个人数据接口先使用 `scripts/ielts_buddy_api.py capabilities` 确认已授权能力；公开预测接口无需 Token。

## 输入与输出

| 能力 | 输入 | 输出 | 约束 |
| --- | --- | --- | --- |
| `ielts_prep_search` | `resourceType:"prediction_hit"`、可选 `subject`、`limit` | 已发布预测记录和 `practiceUrl` | 不传 Token；`practiceUrl` 原样使用。 |
| `ielts_practice_list_taxonomy` | 可选筛选 | 科目、题型、标签、难度与数量 | 用返回的 tag id 作为后续查询条件。 |
| `ielts_practice_search_parts` | `subject`、tag id、难度、排序、分页 | Part 目录和紧凑元数据 | 不批量输出完整题目。 |
| `ielts_practice_read_part` | `partId` | 单个 Part 的元数据和非答案内容 | 只读取已确定的 Part。 |
| `ielts_practice_recent_activity` | 可选分页 | 当前账号近期 session 元数据 | 仅返回当前账号数据。 |
| `ielts_practice_start_session` | `partId` | 新 session 与 `launchUrl` | 用户明确要求开始后才写入。 |
| `ielts_practice_read_session` | `sessionId` | session 状态与 `launchUrl` | 仅访问当前账号拥有的 session。 |
| `ielts_practice_submit_session` | 用户明确提供的阅读/听力客观题答案 | 提交后的客观题结果 | 不用于写作、口语或服务端教学反馈。 |
| `ielts_practice_read_review` | 已提交 `sessionId`、可选 `scope`、`includeMaterial` | 作答、答案 key 和受长度限制的材料快照 | 仅针对已提交阅读/听力 session。 |

## 凭证与链接

- `IELTS_BUDDY_TOKEN` 仅用于 Agent API；浏览器网页登录态仅用于浏览器练习页，二者不可互换。
- `launchUrl` 只能使用 `start_session`、`read_session` 或近期活动的返回值，不能由 `partId` 或 `sessionId` 拼接。
- `practiceUrl` 与 `launchUrl` 都是浏览器入口；数据接口不替代音频播放、计时和答题 UI。

## 数据边界

- `read_review` 返回事实数据，不包含错因、证据定位、教学结论或学习建议。
- 不批量导出题库、答案、解析、听力文本或音频地址。
- 服务端已记录的浏览器练习事件不得再次写入。
