---
name: ielts-mock-review
description: Review a completed IELTS mock test with section scores, timing, question-level results, writing, and speaking evidence, then choose a small set of high-impact repair tasks. Use when a learner asks to analyse a mock exam, interpret score changes, identify the biggest weaknesses, or make a post-mock study plan.
---

# IELTS 模考复盘

默认用简体中文。浏览器负责计时、播放、答题和提交；本 Skill 负责解释已有证据、判断修复优先级和安排下一步。模考结果不是官方成绩，也不应单独视为稳定水平。

## 工作流

读取 [模考复盘](workflows/mock-test-review/WORKFLOW.md)。

## 执行要求

- 先确认哪些科目已完成且可比较；缺失或中断部分必须明确标注，不要补造总分。
- 阅读和听力按题型与技能代码归类；写作和口语基于本地 rubric 证据，并说明判断可信度。
- 区分知识缺口、策略问题和时间管理问题；最多确定三个高影响修复任务。
- 需要历史趋势、题库结果或记录复盘时，先读 [Agent API 配置](references/setup.md) 与 [学习循环](references/learning-loop.md)。
