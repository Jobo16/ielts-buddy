---
name: ielts-listening-review
description: Review IELTS Listening or dictation errors from transcripts, answers, and timestamps, then generate targeted replay drills and a validated Listening Error Notebook DOCX. Use when a learner asks why they missed listening answers, wants a dictation review, provides a transcript or answer key, or needs a focused listening repair plan.
---

# IELTS 听力复盘

默认用简体中文。播放、计时和答题由用户的练习界面完成；本 Skill 在作答后分析证据、设计精听和安排复练。

## 工作流

| 需求 | 读取 |
| --- | --- |
| 错题原因、回放目标和错题本 | [听力错题复盘](workflows/listening-error-review/WORKFLOW.md) |
| 浏览器完成后，对错题做短段回放、跟读与重测 | [逐句精听](workflows/intensive-listening/WORKFLOW.md) |

## 执行要求

- 使用用户提供的题目、答案、正确答案、原文、时间点和练习结果；没有证据时说明不确定性，不要臆测。
- 区分听辨、弱读连读、拼写、单复数、数字日期、词界、干扰、同义替换、语法和注意力问题。
- 从 IELTS Buddy 已提交练习进入精听时，使用 `ielts_practice_read_review` 读取同一 session 的事实；只有需要原始材料时才传 `includeMaterial=true`。
- 每题给一个可执行的回放目标和 1–2 分钟微练习；不要用“多听”代替诊断。
- 两题及以上、整段精听或用户要求保存时，交付已验证的 Listening Error Notebook DOCX。
- 需要网页精听入口、题库或记录进度时，先读 [Agent API 配置](references/setup.md)、[网页入口](references/web-workspace.md) 和 [学习循环](references/learning-loop.md)。
