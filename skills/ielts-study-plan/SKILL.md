---
name: ielts-study-plan
description: 根据考试目标、可用时间与真实学习证据制定或调整雅思学习安排，进行每日接续、周复盘，或将用户要求的下一步保存为 IELTS Buddy 待办。
---

# 雅思学习规划

先理解用户是要建议、完整安排，还是保存待办。复用已有目标与时间约束；只补问会改变安排的信息。没有近期可靠证据时，使用 [最小诊断](references/diagnostic-baseline/WORKFLOW.md)，不要把自述目标当成实测能力。

## 选择方法

- “今天学什么、继续上次”：按 [每日学习](references/daily-study-loop/WORKFLOW.md)，结合已确认的课程进度和最近结果，先给一个可执行动作。
- “这周怎么样、调整计划”：按 [每周复盘](references/weekly-study-review/WORKFLOW.md) 区分证据、假设和时间限制。
- “做完了，下一步”：按 [证据到下一步](references/evidence-to-next-action/WORKFLOW.md)，保留刚产生的学习结果。
- 需要课程或外部资料时，按 [课程路线](references/course-route.md) 或 [资源推荐](references/learning-resource-recommender/WORKFLOW.md) 挑选适量资源；不为了推荐强制制作文档。

## 站内待办

已有用户材料时可直接规划。读取个人记录或保存待办前才使用 [数据接入](references/api-access.md)。待办支持分页 search、批量 create、按精确 id update/delete；用户明确要求安排时可直接保存，不能额外要求确认草稿。

创建请求为 `items` 数组（1–30 条），每项 `title` 必填，`note/date/time/wechatEnabled/contentRef` 可选。日期为 YYYY-MM-DD、时间为 HH:mm，时区 Asia/Shanghai；仅日期无需追问提醒时间，精确提醒必须在未来。微信默认关闭。contentRef 只复用查询返回的 question_part、mock_paper、course_section 或 listening_dictation 引用，线下学习事项可不关联。

“今天安排三个任务”与“给我三个建议”含义不同：前者保存待办，后者只给建议。只有用户明确说已完成才写 done，不能用打开入口或估算时长代替完成事实。学习判断写在建议中；网站只有当前共享待办，没有旧计划代际或重排接口。
