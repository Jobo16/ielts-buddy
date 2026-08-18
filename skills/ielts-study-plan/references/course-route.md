# Course Route

Use the course-route tools when the learner asks for the IELTS full-course roadmap, route progress, or what course to study next. These tools are data-first: they return route nodes and optional browser URLs, but do not require the learner to open the web app.

## Tools

- `ielts_learning_route_read` returns the published IELTS Buddy course route grouped by subject and unit.
- `ielts_learning_route_progress` returns progress summaries for the same route.
- `ielts_learning_route_next` returns prioritized next route actions, favoring in-progress courses before untouched courses.

Use `subject` only when the user asks for one skill (`listening`, `reading`, `writing`, or `speaking`). Leave it empty for the full-course route.

## Operating Policy

1. For "我该学什么", "全科课路线", "课程路线进度", or "下一门课", call the route tools before giving advice.
2. Treat returned route data as the source of truth for course order, unit grouping, and completion state.
3. Give the learner the concrete next course title, course id, success criteria, and why it is next.
4. Use the returned `browserUrl` only as an optional continuation link. Do not force a browser jump when the data already answers the planning question.
5. If the learner asks for sections, videos, materials, or linked practice inside a course, call `ielts_resources_read` with `handle=course:<courseId>`.
6. If the learner wants to actually watch, read courseware, or do linked practice, provide the relevant `browserUrl` or open the Learning center when the client has browser-control tools.

## Examples

Full route:

```json
{
  "subject": "",
  "limit": 200
}
```

Next reading course:

```json
{
  "subject": "reading",
  "availableMinutes": 45,
  "limit": 3
}
```

Recommended response shape:

```text
下一步学「课程标题」（courseId: 123）。原因：已有学习记录，优先续学完成闭环。
完成标准：完成 3 个课程视频；完成 2 个关联练习。
继续学习链接：https://work.ieltsbuddy.igopx.cn/learning-center?course=123
```
