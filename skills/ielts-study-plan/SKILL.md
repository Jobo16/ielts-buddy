---
name: ielts-study-plan
description: Build an evidence-backed IELTS baseline, daily study session, cross-skill next action, weekly review, course route, or learning-resource plan for Chinese learners. Use when the learner asks what to study today, needs a plan, wants to turn a practice, speaking, writing, or vocabulary result into the next task, review progress, diagnose a starting level, choose the next practice, or receive a printable learning workbook.
---

# IELTS 学习计划

默认用简体中文。把未知信息标为未知，不要把自我感觉或完成次数当作能力证据；分数、建议和诊断都只作备考参考。

## 选择工作流

| 需求 | 读取 |
| --- | --- |
| 初次使用、没有可靠近况或需要诊断 | [诊断基线](workflows/diagnostic-baseline/WORKFLOW.md) |
| 今天学什么、20–30 分钟学习块、课程路线 | [每日学习](workflows/daily-study-loop/WORKFLOW.md) |
| 把刷题、精读精听、口语覆盖、写作或词汇结果转为下一任务 | [证据到下一步](workflows/evidence-to-next-action/WORKFLOW.md) |
| 周复盘、下周优先项、调整计划 | [每周复盘](workflows/weekly-study-review/WORKFLOW.md) |
| 外部 IELTS 或英语资源、一周资源安排 | [学习资源推荐](workflows/learning-resource-recommender/WORKFLOW.md) |

## 数据与边界

- 使用 IELTS Buddy 的题库、课程、进度或历史记录前，先读 [Agent API 配置](references/setup.md)。没有 Agent API 时，基于用户主动提供的信息继续，不要虚构服务数据。
- 学习循环、证据记录和本地离线镜像见 [学习循环](references/learning-loop.md)；只在有明确结果后记录。
- 课程、练习、词汇和网页入口分别读取 [课程路线](references/course-route.md)、[练习数据](references/practice.md)、[词汇](references/vocabulary.md)、[网页入口](references/web-workspace.md)。
- 跨 Skill 的输入证据、交接和计划写入边界见 [跨 Skill 交接](references/cross-skill-handoffs.md)。
- 使用 `scripts/learning_store.py` 时，本地镜像只作缓存和离线队列，不替代 IELTS Buddy 的已认证数据。
- 训练任务由本地 Agent 从证据中决定。持久化计划必须先展示拟写入内容，并得到用户明确确认；不要用服务端生成的结构化计划代替本地判断。

## 输出要求

每次只确定一个最先执行的动作，写清做法、预计时间、完成标准和完成后需要反馈的结果。优先到期复习和已有证据支持的薄弱项；没有足够证据时，先做最小诊断。
