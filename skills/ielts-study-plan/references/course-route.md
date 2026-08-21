# 课程路径 API 数据契约

| 能力 | 输入 | 输出 |
| --- | --- | --- |
| `ielts_learning_route_read` | 可选 `subject`、`limit` | 已发布路径，按科目和单元分组的课程节点。 |
| `ielts_learning_route_progress` | 可选 `subject` | 同一路径的完成状态与进度汇总。 |
| `ielts_learning_route_next` | 可选 `subject`、`availableMinutes`、`limit` | 服务端计算的下一路径动作和可选 `browserUrl`。 |
| `ielts_resources_read` | `handle:"course:<courseId>"` | 指定课程的章节、资料和关联练习。 |

`subject` 只接受 `listening`、`reading`、`writing` 或 `speaking`；省略时读取全科路径。`browserUrl` 是可选的继续学习入口，必须原样使用。
