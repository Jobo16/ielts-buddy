# 练习与模考复盘记录

用户给出精确 sessionId 或 reviewTarget 时直接用；说“最近一次”时先用 `ielts_review_recent_activity` 选真实记录。未提交练习用 `ielts_practice_read_session` 确认状态，用户在网页继续完成。已提交普通练习或已完成模考科目使用 `ielts_review_read_snapshot`，请求体含 `target:{kind:"practice",sessionId}` 或 `target:{kind:"mock_section",sessionId,subject}`；`scope` 默认 incorrect，需要完整作答时用 all，`includeMaterial` 仅在证据分析确需原文时开启。按 nextOffset 续页，直到覆盖本次问题，不批量复制完整材料。

精听先用 `ielts_dictation_recent_attempts` 找 attemptId，再 `ielts_dictation_read_attempt` 分页读取逐句输入。足迹 `ielts_footprints_list` 的 summary、dailyCounts 是服务端统计；活动页长度不能当作历史总数。口语音频无转录时仅概括存量评分事实；answerRecovered 或 needs_regrade 的结果不能当成有效判分。只有文字证据时，发音、连读和弱读原因仅为待核实假设。
