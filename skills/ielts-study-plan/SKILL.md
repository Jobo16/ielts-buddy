---
name: ielts-study-plan
description: 说明如何读取和写入 IELTS Buddy 学习计划、学习路径、课程、资源与学习事件；不定义诊断、推荐或计划内容。
---

# IELTS Buddy 学习数据接口

本 Skill 只说明学习数据接口。调用前，先按[Agent API 配置](references/setup.md)绑定并检查当前账号实际可用的能力。

## 接口

| 能力组 | 数据或动作 | 调用约束 |
| --- | --- | --- |
| `ielts_study_plans_list`、`ielts_study_plans_get`、`ielts_study_plans_create`、`ielts_study_plans_update`、`ielts_study_plans_update_task`、`ielts_study_plans_delete` | 读取、创建、更新、删除计划和任务 | 任何写入均须由用户明确确认；先读取目标对象。 |
| `ielts_learning_route_read`、`ielts_learning_route_progress`、`ielts_learning_route_next`、`ielts_learner_read_profile`、`ielts_learning_pull_events` | 学习路径、资料和历史事实 | 缺失字段保持未知，不补造数据。 |
| `ielts_resources_search`、`ielts_resources_read`、`ielts_resources_related`、`ielts_prep_search`、`ielts_prep_read_guide` | 公开资料、备考内容及关联资源 | 仅使用服务端返回的公开记录和链接。 |
| `ielts_learning_push_events` | 记录已经发生且有证据的学习事件 | 不把建议、草案或推断写成事件。 |

```sh
python3 scripts/ielts_buddy_api.py capabilities
python3 scripts/ielts_buddy_api.py call ielts_study_plans_list --json '{}'
```

## 边界

- 计划的目标、优先级和任务内容由调用方与用户决定；服务端只保存经确认的数据。
- 不调用会替调用方生成计划内容的能力。
- `workflows/` 是独立的可选推荐层，不属于本 Skill 的接口契约。
