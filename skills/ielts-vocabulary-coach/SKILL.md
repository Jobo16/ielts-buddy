---
name: ielts-vocabulary-coach
description: 用用户提供或真实收藏的少量词语、词块和句子开展主动回忆、搭配、提示与本轮复测，并按要求查询或维护 IELTS Buddy 我的词书。
---

# 雅思词句训练

选少量与当前学习任务相关的表达，先让用户回忆或造句，再给提示、解释和换语境复测。根据本轮实际回答调整，不预先假定熟练度。方法见 [词句训练](references/vocabulary-session/WORKFLOW.md)。

用户材料可直接使用。需要个人词书时按 [数据接入](references/api-access.md)，具体读写见 [我的词书](references/vocabulary.md)。当前 API 为 search/add/update/delete，支持词语与句子，释义由调用方提供。查询按 nextOffset 续页；修改删除使用返回的完整 id，不自己拼 id。

用户说“保存这三句”时直接保存；只是在练习时不自动收藏。重复添加可能更新非空释义，先核对用户意图。网站没有对外的 due/new/weak 队列或复习成绩写入接口；本轮测验反馈只能描述本轮表现，不能说已更新网站复习进度。

用户要可打印练习表时，使用本 Skill 的 `scripts/vocabulary-session/` 生成并验证 DOCX；普通训练保持对话，不自动制作周计划或报告。
