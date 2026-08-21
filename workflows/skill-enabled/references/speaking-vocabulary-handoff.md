# 口语表达进入词汇本

口语反馈完成后，只有学习者明确提出“保存表达”“加入词汇本”或确认了候选清单，才写入个人词汇本。不要自动保存每次给出的自然表达，也不要把保存动作当作掌握。

## 候选选择

从本次真实回答或转写中选择 2–4 个可复用词块：

- 优先能帮助展开经历、表达原因、结果、对比或态度的自然口语块；
- 每项必须对应到学习者的一处原回答和本次给出的局部优化；
- 排除完整答案句、与本题绑定的专有名词和书面化过强的表达；
- 没有音频或转写证据时，不把发音问题转成词汇条目。

先展示候选清单，每项包含表达、简短含义、原回答语境和一个可迁移例句，然后等待学习者确认。

## 确认后写入

调用 `ielts_vocabulary_personal_add`，一次提交确认后的全部表达：

```text
sourceType: speaking_feedback
sourceId: speaking_session:<sessionId>，没有稳定 sessionId 时留空
sourceTitle: <Part 与题目>
context: <学习者原回答中的相关短句>
items: [{phrase, meaning, partOfSpeech, example, usage, expansion}]
```

写入成功后只说明保存数量和表达名称。需要马上练习时，再交给 `$ielts-vocabulary-coach`；学习者实际完成主动回忆后才记录复习结果。
