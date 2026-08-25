# 课程路径 API 数据契约

| 能力 | 输入 | 输出 |
| --- | --- | --- |
| `ielts_learning_route_read` | 可选 `subject`、`limit` | 已发布路径，按科目和单元分组的课程节点。 |
| `ielts_learning_route_progress` | 可选 `subject` | 同一路径的完成状态与进度汇总。 |
| `ielts_learning_route_next` | 可选 `subject`、`availableMinutes`、`limit` | 服务端计算的下一路径动作和可选 `browserUrl`。 |
| `ielts_courses_search_sections` | 可选 `subject`、`search`、`tagQueries`、`limit` | 已发布的精确课程章节，以及可直接用于计划任务的 `contentRef`。 |

路径能力的 `subject` 只接受 `listening`、`reading`、`writing` 或 `speaking`；章节搜索还接受 `grammar`。省略时读取全科路径。`browserUrl` 是可选的继续学习入口，必须原样使用。创建计划时复用章节搜索返回的 `{ "kind":"course_section", "courseId":..., "sectionId":... }`，不要从标题猜 ID。
