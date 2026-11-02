---
name: ielts-mock-review
description: 依据一次模考的科目完成状态、可信成绩与作答证据进行复盘，识别高影响问题并提出下一步；需要时按明确结构检索或组成模考试卷。
---

# 雅思模考复盘

先核对用户给出的成绩、考试条件和科目是否完整。方法见 [模考复盘](references/mock-test-review/WORKFLOW.md)。网站数据按 [数据接入](references/api-access.md) 和 [复盘记录](references/review-records.md) 获取。

整场仍进行中时，已经 completed 的科目可以单独复盘；未完成科目不能估分。`ielts_review_recent_activity` 返回真实 reviewTarget，再用 `ielts_review_read_snapshot` 取该科目证据。口语、写作用 scope=all；音频无原话时仅解释存量判分事实。不同来源、不完整或条件不同的成绩不能直接画进步趋势。

需要找卷时使用 `ielts_mock_search_papers`。用户要求组卷时，先检索真实 Part，再用 `ielts_mock_create_paper` 提交不重复的 partIds：听力 1–4、阅读 1–3 且 40 题、写作 Task 1–2、口语 Part 1 与 Part 2&3。结构由服务端再验证，不能用标题猜测。组卷不等于开始考试；网页正式作答和交卷由用户完成。

复盘区分已确认问题、待验证原因和下一训练动作。用户要求保存安排时才创建共享待办；不把建议本身写成已完成学习事实。
