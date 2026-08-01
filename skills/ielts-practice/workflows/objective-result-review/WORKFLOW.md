# 客观题结果复盘

## 读取结果

1. 优先使用当前对话中保存的 `sessionId` 调用 `ielts_practice_read_session`。
2. 没有 `sessionId` 时，读取 `ielts_practice_recent_activity`，让用户确认是哪一次练习；不要猜测。
3. 如果 session 仍未提交，返回它的 `launchUrl` 让用户继续，不开始复盘。
4. 已提交后，调用 `ielts_practice_read_review`，默认 `scope="incorrect"`、`includeMaterial=false`。先陈述作答数、正确数、正确率、用时和错题编号；不要改写为虚构的能力结论。

## 本地复盘

- 阅读：需要逐题证据、同义替换、长难句或干扰项分析时，重新调用 `ielts_practice_read_review` 并设 `includeMaterial=true`，再交给 `$ielts-reading-review` 的“四步精读”。
- 听力：需要听辨错因、拼写、定位或精听练习时，以同一工具的受限材料快照交给 `$ielts-listening-review` 的“逐句精听”。
- 只基于有证据的多题结果归纳模式；一次偶发错误只能作为待验证线索。
- `ielts_practice_read_review` 不产生错因、证据或教学结论。不要让服务端替本地 Agent 做这些判断；不要在聊天中批量复刻整篇原文或整份听力转录。

## 结束

浏览器提交已经产生权威学习事件，不重复写入。以一个具体动作结束：继续完成未答题、复练一个明确技能，或开始下一组题。用户需要把这个动作排入学习计划时，交给 `$ielts-study-plan` 的“证据到下一步”；未明确确认前不要写入计划。
