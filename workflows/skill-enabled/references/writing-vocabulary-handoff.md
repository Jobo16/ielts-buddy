# 批改表达进入词汇本

批改完成后，只有学习者明确提出“保存表达”“加入词汇本”或确认了候选清单，才写入个人词汇本。不要自动收集所有改写，也不要把保存动作记成一次复习。

## 候选选择

从本次原文与批改证据中选择 3–5 个可迁移词或词块：

- 优先自然搭配、论证句块、数据比较表达和学习者反复用错的表达；
- 每项必须能对应到一处原句或局部改写；
- 排除只适用于当前题目的专有名词、完整范文句和为了显得高级而生硬的替换；
- 保留学习价值更高的词块，例如 `pose a threat to`，而不是拆成孤立单词。

先展示候选清单，每项包含英文表达、简短含义、原文语境和为什么值得复习，然后等待学习者确认。

## 确认后写入

调用 `ielts_vocabulary_personal_add`，一次提交确认后的全部表达：

```text
sourceType: writing_review
sourceId: writing_session:<sessionId>，没有稳定 sessionId 时留空
sourceTitle: <作文题目或本地文件名>
context: <与这些表达直接相关的原句或短上下文>
items: [{phrase, meaning, partOfSpeech, example, usage, expansion}]
```

`example` 使用可模仿的局部改写，`usage` 说明原文问题或适用语境，`expansion` 只放紧密相关的搭配或变体。不得把 AI 评分、整篇范文或未经学习者确认的表达写入词汇本。

写入成功后只说明保存数量和表达名称。需要马上练习时，再交给 `$ielts-vocabulary-coach`；学习者实际作答后才记录 `again`、`hard` 或 `good`。
