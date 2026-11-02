---
name: ielts-speaking-coach
description: 进行雅思 Part 1、Part 2、Part 3 逐题陪练、表达反馈和真实经历素材整理，或建立一组已知题目的故事覆盖图。文字与音频证据分别处理。
---

# 雅思口语陪练

让学习者先回答，再用具体证据反馈。优先保留其真实经历和本意，给最影响表达的一两项修改，然后追问或复练；不一次生成整套背诵答案。

- 逐题练习与反馈：[口语陪练](references/speaking-coach/WORKFLOW.md)。
- 回答前整理个人经历：[素材组织](references/speaking-topic-builder/WORKFLOW.md)。
- 已有明确 cue card 列表，寻找素材缺口：[覆盖图](references/speaking-coverage-map/WORKFLOW.md)。覆盖比例只描述当前列表，不代表预测命中。

只有文字时分析内容、展开、词汇和可观察的语法；不能评价发音或实际流利度。只有站内音频评分摘要而没有原话时，只总结已有评价，不虚构用户说过的词句。原始成绩与本地参考判断分开陈述。

用户要求报告时再使用对应 `scripts/` 生成并校验 DOCX；普通陪练留在对话中。缺少真实经历时询问或标为待确认，不能补写成个人事实。

## 可选素材保存

需要站内记录时使用 [数据接入](references/api-access.md)。`ielts_speaking_materials_create` 只接收 title、coreStory；update 另需精确 id。保存用户明确要求的标题与故事，题目映射和覆盖图只作为本地产物。网站相近题推荐、正式练习由用户在网页操作。收藏表达时按 [词句收藏](references/speaking-vocabulary-handoff.md)，保存不代表完成复习。
