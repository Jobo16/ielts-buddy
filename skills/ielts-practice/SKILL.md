---
name: ielts-practice
description: 根据科目、题型、标签或用户提供的内容选择雅思练习，核对真实题目与音频并交接网页作答；也可围绕用户自带材料进行明确标注的本地练习。
---

# 雅思刷题与选题

先明确用户要找题、做本地练习，还是继续一次网站练习。方法见 [浏览器练习](references/browser-practice/WORKFLOW.md)，完成后的记录读取见 [复盘记录](references/review-records.md)。个人题库访问需要时才使用 [数据接入](references/api-access.md)。

## 找到可用题目

- 用户给出原文片段、经历或观点：用 `ielts_practice_match_parts`，保留原始 query；hardTagQueries 只使用用户明确指定的题库或标签。
- 科目、Part 编号和题型筛选：用 `ielts_practice_search_parts`；分类歧义或目录浏览才用 `ielts_practice_list_taxonomy`。
- 听力刷题必须指定 `subject=listening`、`requiresAudio=true`，并核对返回的 audioAvailable。精听用 `ielts_dictation_search_materials`，没有音频时不能自编朗读替代正式练习。
- 题名、来源、Part id、contentRef 与练习链接只取服务端结果。预测回忆与候选题是不同事实，详细规则见 [题库与预测](references/practice-contract.md)。

## 练习边界

给出清楚的一项推荐及理由。正式练习由用户在网页开始、作答、计时和提交；推荐入口不代表已创建 session。用户回来后读取真实记录，再按 [客观题复盘](references/objective-result-review/WORKFLOW.md) 解释结果。

用户提供题目并要求聊天内训练时可以进行本地练习：先让其作答，再给证据、提示和答案。明确这是本轮本地练习，不能把它保存成网站已提交试卷或正式分数。
