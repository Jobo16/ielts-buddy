---
name: ielts-listening-review
description: 根据真实听力或精听作答分析定位、理解、拼写与答案形式问题，并设计短时修复练习；需要听觉成因判断时要求相应音频证据。
---

# 雅思听力复盘

先区分正式听力题、逐句精听、用户自带听写材料。网站结果按 [数据接入](references/api-access.md) 和 [复盘记录](references/review-records.md) 读取，精听使用 attemptId，不能与 sessionId 混用。

- 错题分类、证据与修复练法：[听力错题复盘](references/listening-error-review/WORKFLOW.md)。
- 根据已提交结果练答案句：[逐句精听](references/intensive-listening/WORKFLOW.md)。网页播放、填答、核对和提交由用户操作。

只见文字作答时，可以确定漏答、拼写或词形差异；连读、弱读、重音等听觉成因只能是待核实假设。不要把一处偶发错误扩展为稳定弱项，或拿脚本文字冒充听过的音频。

输出有依据的关键问题和短练法。用户要求错题本时再调用本 Skill `scripts/` 的生成器和校验器。保存词句或待办只在用户要求时进行；不重复上报网站已经记录的练习事件。
