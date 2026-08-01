---
name: ielts-reading-review
description: Review IELTS Reading mistakes with passage evidence and paraphrase bridges, extract useful passage vocabulary, and create validated DOCX evidence maps or lexicons. Use when a learner provides a Reading passage, questions, answers, result, or DOCX and asks for error analysis, answer evidence, paraphrase explanation, distractor analysis, or a vocabulary handout.
---

# IELTS 阅读复盘

默认用简体中文解释。先定位原文证据和同义替换，再解释错误；不要只报正确答案，也不要编造题库答案。

## 选择工作流

| 需求 | 读取 |
| --- | --- |
| 错题证据、同义替换、干扰项、错因 | [阅读复盘](workflows/reading-review/WORKFLOW.md) |
| 浏览器完成后，把一组题做透、练定位和长难句 | [四步精读](workflows/intensive-reading/WORKFLOW.md) |
| 从文章或 DOCX 提取高价值词组与例句 | [阅读词汇手册](workflows/ielts-reading-lexicon/WORKFLOW.md) |

## 执行要求

- 使用用户提供的文章、题目、答案或已认证题库数据；缺少原文或答案时先索取，或提供网页练习入口。
- 每道错题说明证据、同义替换、干扰来源和下一次定位动作；把错误归为可复练的技能，不泛泛说“多练”。
- 从 IELTS Buddy 已提交练习进入精读时，使用 `ielts_practice_read_review` 读取同一 session 的事实；需要材料才传 `includeMaterial=true`，不要改用无答案的目录读取来猜测作答结果。
- 两道及以上错题或用户要求保存时，生成并验证 DOCX 后返回最终绝对路径。
- 需要题库或学习记录时，先读 [MCP 配置](references/setup.md) 与 [学习循环](references/learning-loop.md)。
