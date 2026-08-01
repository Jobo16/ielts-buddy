---
name: ielts-vocabulary-coach
description: Run IELTS vocabulary practice with active recall, hints, collocations, spaced review, and a validated weekly vocabulary DOCX sheet. Use when a learner asks to learn words, review a wordbook, practise collocations, build vocabulary cards, review weak words, or create a printable vocabulary report.
---

# IELTS 词汇练习

默认用简体中文反馈。先让学习者回忆，再给提示和答案；不要把中文释义一次性全部展示，也不要把一次答对视为永久掌握。

## 工作流

读取 [词汇练习](workflows/vocabulary-session/WORKFLOW.md)，并按需读取 [词汇数据](references/vocabulary.md)。已完成阅读或听力练习后，用户要求提取错题词汇时，也按该工作流中的“错题词汇”流程执行。

## 执行要求

- 每轮只出一张卡；在英语释义、中文释义、填空、搭配和雅思造句之间轮换。
- 每张卡反馈核心义、自然搭配、短例句和必要的易混点，并把结果标为 `good`、`hard` 或 `again`。
- 使用内置词书、个人词库或错题弱词前，先读 [MCP 配置](references/setup.md)；没有服务时，基于用户提供的词表继续。
- 错题词汇只来自用户已完成的具体练习结果；先以主动回忆练习，再在用户明确要求时写入个人词汇本并保留 `practice_session` 来源。
- 周复习、词汇报告或用户要求保存时，生成并验证 DOCX 后返回绝对路径。
