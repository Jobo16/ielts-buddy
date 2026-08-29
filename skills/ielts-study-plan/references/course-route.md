# 课程路径 API 数据契约

| 能力 | 输入 | 输出 |
| --- | --- | --- |
| `ielts_learning_route_read` | 可选 `subject`、`limit`、`view:"route"|"progress"` | 已发布路径与完成事实；`route` 返回课程节点，`progress` 返回紧凑进度。 |
| `ielts_courses_search_sections` | 可选 `subject`、`search`、`tagQueries`、`limit` | 已发布的精确课程章节，以及可直接用于计划任务的 `contentRef`。 |

路径能力的 `subject` 只接受 `listening`、`reading`、`writing` 或 `speaking`；章节搜索还接受 `grammar`。省略时读取全科路径。下一步由 Agent 根据路线与进度事实选择。创建计划时复用章节搜索返回的 `{ "kind":"course_section", "courseId":..., "sectionId":... }`，不要从标题猜 ID。
