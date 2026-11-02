# 每日学习接续

> 当前任务需要本方法时按需读取。脚本命令中的 `scripts/` 相对于本 Skill 根目录；实际运行时解析为安装目录中的绝对路径。

## 取证与选择

1. 先复用用户当前对话给出的学习结果、目标和今日可用时间。需要网站记录时再按 [数据接入](../api-access.md) 读取近期活动、学习快照或课程路线；没有授权时继续处理用户给出的材料。
2. 刚完成练习、写作或口语反馈时，按 [证据到下一步](../evidence-to-next-action/WORKFLOW.md) 接续。已有待办时先查 `ielts_study_todos_search`，优先考虑用户明确承诺且尚未完成的事项；网站不提供自动排序或词汇到期队列。
3. 有课程进度时可用 `ielts_learning_route_read` 对照未完成章节。需要正式作答、听力播放或课程学习时，把真实题目或课程入口交给用户在网页完成，不代替提交。
4. 只给当前最值得做的一个动作，说明证据、做法和完成信号。证据不足时使用 [最小诊断](../diagnostic-baseline/WORKFLOW.md)，不要臆测薄弱项。

## 输出

```text
今天先做：<一个任务>
依据：<当前对话或已读取记录中的事实；不足时直说>
做法：<最多三步>
完成后带回：<答案、作答结果、草稿或口语文本>
```

用户明确要求保存安排时，用 `ielts_study_todos_create` 直接保存；仅要建议时不写入。完成状态只根据用户明确声明或网站真实返回更新。词汇本轮复测不能写成网站复习进度。

## 按需制作课程路线文档

用户要求完整的可下载 Word 路线表时，读取 `ielts_learning_route_read` 的 `route` 与 `progress` 视图，只使用真实课程 ID 和状态生成计划。运行 `scripts/daily-study-loop/create_course_route_workbook_docx.py <plan.json>`，再用同目录的 `validate_course_route_workbook_docx.py` 校验生成结果。缺少课程数据时说明限制，不编造课程或链接。
