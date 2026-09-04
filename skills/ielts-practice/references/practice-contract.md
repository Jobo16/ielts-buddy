# 练习 API 数据契约

个人数据接口先使用 `scripts/ielts_buddy_api.py capabilities` 确认已授权能力；公开预测接口无需 Token。

## 输入与输出

| 能力 | 输入 | 输出 | 约束 |
| --- | --- | --- | --- |
| `ielts_prediction_search_hits` | 可选 `reportIds`、`subject`、`query`、`testDate`、`testMonth`、`limit`、`offset` | 已发布考场记录、可能对应的题目和可选练习入口 | 不传 Token；空筛选返回最新记录，精确日期优先于月份。 |
| `ielts_practice_list_taxonomy` | 可选 `subject`、`difficulty`、`search`、`tagQueries`、`tagIds` | 精确标签与当前筛选下的可用数量 | 用户提出题库、材料、Test、题型等分类词时先解析 tag id。 |
| `ielts_practice_search_parts` | 可选 `subject`、`tagIds`、`tagQueries`、难度、排序和 `cursor` | 最多六个 Part 候选、权威 `origin`、`contentRef` 与下一游标 | 不批量输出完整题目；翻页只用返回的 `nextCursor`。 |
| `ielts_dictation_search_materials` | 可选 `difficulty`、`search`、`tagQueries`、`limit` | 可逐句精听素材、分组标签、句段数和 `contentRef` | 不创建精听运行或浏览器入口。 |
| `ielts_practice_read_part` | `partId` | 单个 Part 的元数据和非答案内容 | 只读取已确定的 Part。 |
| `ielts_practice_recent_activity` | 可选分页 | 当前账号近期 session 元数据 | 仅返回当前账号数据。 |
| `ielts_practice_read_session` | `sessionId` | session 状态与 `launchUrl` | 仅访问当前账号拥有的 session。 |
| `ielts_practice_read_review` | 已提交 `sessionId`、可选 `scope`、`includeMaterial` | 作答、答案 key 和受长度限制的材料快照 | 仅针对已提交阅读/听力 session。 |

## 预测命中结构

`ielts_prediction_search_hits` 每个 `items` 元素是一条考场记录：

- `id` 与 `contentRef` 标识记录；`source` 明确数据来自哪个平台。
- `examDate`、`examMode`、`venue`、`recallKind`、`title` 和 `recallContent` 是考场回忆或题目信息。
- `candidates` 是可能对应的题目列表。每项包含 `title`、`details`、`matchScore`，以及可为空的 `practiceUrl` 和 `practiceRoute`。
- `matchScore` 是服务端给出的匹配值，不是来源平台的确认结论。文本匹配低于 50 的候选不会进入列表；调用方保留服务端顺序和全部候选，不只返回最高分候选，也不自行重新计算分值。
- 只有已绑定到已发布题库 Part 的候选才有 `practiceUrl`。链接为空时仍可展示候选信息，不能自行拼接做题地址。

响应同时返回 `totalCount`、`dateFacets`、`hasMore` 和 `nextOffset`。继续翻页时只使用服务端返回的 `nextOffset`；需要读取指定记录时传先前返回的 `reportIds`。

三个月以前的考场记录会继续保留并可检索，但不再执行题库匹配，因此 `candidates` 可能为空。这不表示考场记录缺失或接口失败。

## 凭证与链接

- `IELTS_BUDDY_TOKEN` 仅用于 Agent API；浏览器网页登录态仅用于浏览器练习页，二者不可互换。
- `launchUrl` 只能使用 `read_session` 或近期活动的返回值，不能由 `partId` 或 `sessionId` 拼接。
- `practiceUrl` 是预测候选题的可选公开入口，`launchUrl` 是已有练习 session 的入口；两者都必须原样使用，不能自行拼接。

## 数据边界

- `read_review` 返回事实数据，不包含错因、证据定位、教学结论或学习建议。
- 题库来源只认 `search_parts` 的 `origin.questionBank`、`origin.sourceBook`、`origin.sourceTest` 和 `origin.sourceUnit`，不从标题或普通标签推断。
- 不批量导出题库、答案、解析、听力文本或音频地址。
- 服务端已记录的浏览器练习事件不得再次写入。
- 创建 session、填写答案和交卷都属于浏览器交互，不是 Agent API 能力。
