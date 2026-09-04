---
name: ielts-study-plan
description: 说明如何读取和写入 IELTS Buddy 学习计划、精确课程与练习内容、任务提醒、学习路径、资源和学习事件；不定义诊断、推荐或计划内容。
---

# IELTS Buddy 学习数据接口

本 Skill 只说明学习数据接口。调用前，先按[Agent API 配置](references/setup.md)绑定并检查当前账号实际可用的能力。

## 接口

| 能力组 | 数据或动作 | 调用约束 |
| --- | --- | --- |
| `ielts_study_plans_list`、`ielts_study_plans_get` | 读取计划和完整任务 | 使用返回的精确 `planId`、任务 ID 与 revision，不猜 ID；下一项由调用方根据事实选择。 |
| `ielts_courses_search_sections`、`ielts_practice_search_parts`、`ielts_dictation_search_materials`、`ielts_mock_search_papers` | 发现可写入计划的精确内容与稳定 `contentRef` | 内容由调用方选择；服务端只返回事实候选。 |
| `ielts_study_plans_create` | 从已选定任务创建计划 | 每项任务必须包含服务端返回的 `contentRef`、中国日历日期和 `morning`、`afternoon` 或 `evening` 时段。 |
| `ielts_study_plans_update`、`ielts_study_plans_change_tasks`、`ielts_study_plans_replan`、`ielts_study_plans_delete` | 修改标题/目标，原子增改删完任务，重排未完成任务或删除计划 | 写入前读取计划；`change_tasks` 不是局部计划 patch，`replan` 会整体替换未完成任务。 |
| `ielts_notifications_get_status`、`ielts_notifications_configure_wechat_task_reminders` | 读取微信 iLink 状态，为现有任务启停微信投递 | 只传精确 `taskId`；提醒工具不创建任务，也不修改日期或时段。 |
| `ielts_learning_route_read`、`ielts_learner_read_profile`、`ielts_learning_pull_events` | 学习路径、画像和历史事实 | 路径用 `view:"route"` 或 `view:"progress"`；缺失字段保持未知，不补造数据。 |
| `ielts_assets_search`、`ielts_resources_related`、`ielts_prep_search_guides`、`ielts_prep_read_guide`、`ielts_prediction_search_hits` | 用户资产、备考内容、考场记录、候选题及关联资源 | 保持考场记录与候选题分层，仅使用服务端返回的记录、`contentRef` 和可选链接。 |
| `ielts_learning_push_events` | 记录已经发生且有证据的学习事件 | 不把建议、草案或推断写成事件。 |

```sh
python3 scripts/ielts_buddy_api.py capabilities
python3 scripts/ielts_buddy_api.py call ielts_study_plans_list --json '{}'
```

## 边界

- 计划的目标、优先级和任务内容由调用方与用户决定；服务端只保存经确认的数据。
- `contentRef` 只接受 `practice_part`、`mock_paper`、`course_section` 或 `listening_dictation`；直接复用目录工具返回的对象，不手工补全内容快照。
- 修改计划标题或目标使用 `update`；改变具体任务使用 `change_tasks`；整体替换未完成安排使用 `replan`，不要混用。
- `workflows/` 是独立的可选推荐层，不属于本 Skill 的接口契约。
