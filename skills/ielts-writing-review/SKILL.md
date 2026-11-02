---
name: ielts-writing-review
description: 批改雅思 Task 1 或 Task 2 作文，进行写前规划、原文证据批注和二改对照；需要可下载 Word 时生成并验证文档。用户提供作文即可使用，网站连接可选。
---

# 雅思写作批改

依据题目和原文判断，先服从用户要求的范围：只改语法时不扩展成完整评分。没有题目时可分析语言，但不判断是否切题或编造任务分。区分明确错误与可选表达改进，不承诺固定提分。

## 按任务阅读

- 写前审题或提纲：[写前规划](references/writing-task-planning/WORKFLOW.md)。
- Academic Task 1 图表、地图或流程：[Task 1 批改](references/ielts-task1-review/WORKFLOW.md)。先看图，缺图时只做明确限定的语言反馈；不要套用到 General Training 信件。
- Task 2 议论文：[Task 2 批改](references/ielts-task2-review/WORKFLOW.md)。以原文支持四项标准的判断，给少量最值得修复的问题。
- 已有首稿与改稿：[改稿对照](references/writing-revision-loop/WORKFLOW.md)。没有可比版本时不声称能力提升。

## 输出与文档

普通请求先交付聊天反馈。只有用户要求文档或需要保留 Word 批注时，才使用所选方法的生成器和校验器。脚本在本 Skill 的 `scripts/`；执行时解析为安装目录的绝对路径，输出到用户指定位置或私有工作目录。

逐字保留被批改原文，引用必须能定位；同一句多次出现时明确位置。源 Word 生成新的副本，保留段落、图片和版式，不覆盖源文件。校验失败修正后再交付；文档生成成功不证明评分判断正确。

## 可选网站数据

网站已有作文可通过 [数据接入](references/api-access.md) 和 `ielts_writing_read_practice` 读取不可变版本。正式写作提交、二改和站内评分由用户在网页完成；当前开放 API 没有本地批改上传接口。本地意见和文档留在本地，不声称已保存到网站。

用户要求保存有用表达时按 [表达收藏](references/writing-vocabulary-handoff.md)，只选择原文或明确修改中有依据的词句。
