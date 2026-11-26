# 练习 API 数据契约

个人数据接口先按 [数据接入](api-access.md) 确认已授权能力；公开预测接口无需 Token。

## 输入与输出

| 能力 | 输入 | 输出 | 约束 |
| --- | --- | --- | --- |
| `ielts_prediction_search_hits` | 可选 `kind`、`source`、`reportIds`、日期与科目筛选、`limit/offset` 和 `candidateLimit/candidateOffset` | 已发布考场记录或滚动榜单、分页候选及可选练习入口 | 不传 Token；空筛选返回最新记录，精确日期优先于月份。 |
| `ielts_practice_list_taxonomy` | 可选 `view`、`groupCode`、`limit/offset` 和筛选条件 | 默认返回分组目录；`view=tags` 返回精确标签和可用数量 | 用户提出题库、材料、Test、题型等分类词时先解析 tag id。 |
| `ielts_practice_search_parts` | 可选 `subject`、`tagIds`、`tagQueries`、难度、排序和 `cursor` | 最多六个 Part 候选、权威 `origin`、`contentRef` 与下一游标 | 不批量输出完整题目；翻页只用返回的 `nextCursor`。 |
| `ielts_dictation_search_materials` | 可选 `difficulty`、`search`、`tagQueries`、`partNumber`、`limit`、`offset` | 材料标题、原听力题标签、精听句数、`contentRef`、“开始精听”入口及 `nextOffset` | 关键词匹配标题、原稿及译文；搜索不创建精听运行，用户点击入口后进入对应 Part。 |
| `ielts_practice_read_part` | `partId` | 单个 Part 的元数据和非答案内容 | 只读取已确定的 Part。 |
| `ielts_practice_recent_activity` | `subject`、`status`、日期筛选、`limit`、`offset` | 本页普通练习摘要、`reviewTarget` 和下一页位置 | 仅返回当前账号数据；未提交记录用 `sessionId` 查会话详情。 |
| `ielts_practice_read_session` | `sessionId` | session 状态与 `launchUrl` | 仅访问当前账号拥有的 session。 |
| `ielts_review_read_snapshot` | 列表返回的 `target`，可选 `view`、`scope`、`includeMaterial`、`limit`、`offset`、`detailSection` 和 `contentOffset` | 指定普通练习或模考科目的作答、答案、批改和材料快照 | 仅当前用户已提交的普通练习或已完成模考科目。 |

复盘列表使用 `ielts_review_recent_activity`，普通练习取 `reviewTarget`，模考取 `reviewTargets` 中的一个科目引用；第二次调用 `ielts_review_read_snapshot({target: ...})` 先读摘要，再按返回的 `items[].detail.input` 读所需字段。页内续读使用 `nextContent.input`。

## 预测命中结构

`ielts_prediction_search_hits` 的 `kind=exam_report` 返回考场记录，`kind=rolling_ranking` 返回滚动榜单：

- `id` 与 `contentRef` 标识记录；`source` 明确数据来自哪个平台。
- `examDate`、`examMode`、`venue`、`recallKind`、`title` 和 `recallContent` 是考场回忆或题目信息。
- `candidates` 是可能对应的题目列表。每项包含 `title`、`details`、`matchScore`，以及可为空的 `practiceUrl` 和 `practiceRoute`。
- `matchScore` 是服务端给出的匹配值，不是来源平台的确认结论。文本匹配低于 50 的候选不会进入列表；保留服务端顺序和来源，当前候选页只代表该记录的一部分。
- 只有已绑定到已发布题库 Part 的候选才有 `practiceUrl`。链接为空时仍可展示候选信息，不能自行拼接做题地址。

响应同时返回 `totalCount`、`dateFacets`、`hasMore` 和 `nextOffset`。记录翻页使用 `nextOffset`。同一条记录要取更多候选时，直接使用该记录的 `moreCandidates.input`；它包含准确的记录类型、ID 和候选偏移。

三个月以前的考场记录会继续保留并可检索，但不再执行题库匹配，因此 `candidates` 可能为空。这不表示考场记录缺失或接口失败。

## 个人练习

- 使用 `ielts_practice_create_part`。提交完整题面，答案缺失时可省略；按事实选择 answerSource。阅读用题文或已拥有的素材引用，听力用自己的录音或合成稿，写作与口语按相应 schema。读听最多 40 道题，整个请求最多 12,000 字符。
- 写入前保存一次请求用的键。使用 CLI 的 `--idempotency-key` 或 HTTP 的 `Idempotency-Key`，遇到网络结果不明时，原样重试同一内容；为新题换新键。
- `ready` 表示可打开。听力合成可能返回 `queued` 或 `running`；等待后用 `ielts_practice_read_personal_part` 查询同一 `personalPartId`，失败或取消时停止轮询。有 `retryable` 时从网页任务入口重试。
- 题面按 `summary`、`passage` 和 `questions` 读取；单题传 `questionNo`，续读直接用 `nextInput`。题目答案、解析和听力稿在提交后的授权复盘中读取。

## 凭证与链接

- `IELTS_BUDDY_TOKEN` 仅用于 Agent API；浏览器网页登录态仅用于浏览器练习页，二者不可互换。
- `launchUrl` 只能使用 `read_session` 或近期活动的返回值，不能由 `partId` 或 `sessionId` 拼接。
- `practiceUrl` 是预测候选题的可选公开入口，`launchUrl` 是已有练习 session 的入口；两者都必须原样使用，不能自行拼接。

## 数据边界

- `read_snapshot` 返回已记录的事实与证据。错因判断、证据解读和学习建议由调用方完成。
- 题库来源只认 `search_parts` 的 `origin.questionBank`、`origin.sourceBook`、`origin.sourceTest` 和 `origin.sourceUnit`，不从标题或普通标签推断。
- 不批量导出题库、答案、解析、听力文本或音频地址。
- 服务端已记录的浏览器练习事件不得再次写入。
- 创建 session、填写答案和交卷都属于浏览器交互，不是 Agent API 能力。
