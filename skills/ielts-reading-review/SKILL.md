---
name: ielts-reading-review
description: 根据阅读题目、用户答案和原文证据解释错因、同义替换与干扰项，开展精读或整理阅读词块；也可读取已提交 IeltsBuddy 练习或模考科目。
---

# 雅思阅读复盘

先核对题目、用户答案、答案依据和原文是否足够。用户已提供材料时直接分析；从网站取数时按 [数据接入](references/api-access.md) 与 [复盘记录](references/review-records.md) 先列表再取证据。

- 错题诊断和证据定位：[阅读复盘](references/reading-review/WORKFLOW.md)。每个结论要有原文证据，区分错误与缺少作答。
- 围绕一篇材料练证据、替换、定位和重测：[精读](references/intensive-reading/WORKFLOW.md)。先提示再揭示答案，不批量复刻网站整篇材料。
- 用户要整理表达：[阅读词块](references/reading-lexicon/WORKFLOW.md)。按使用价值选择，引用与释义要可核对。

先解释最关键的问题，再给一个短练习或下一动作。不能从局部正确率估算完整 IELTS 分数。用户要求证据图或词汇文档时才运行本 Skill 的生成/校验脚本；普通复盘直接用对话。用户要求保存词句时使用当前词书 API，不能将收藏说成已完成复习。
