# Speaking Topic Builder

> 这是可选推荐用法，不是 Skill 接口契约或强制执行要求。只有用户要求采用该用法时才读取和使用。

默认面向中国雅思学习者，用简体中文解释选择理由、练习方法和复盘要求。题目、答案骨架、英文表达块保留英文。

## Core Rule

本地 Agent 负责选题、串题、素材组织和练习策略。IELTS Buddy 只提供题库数据、已有材料、进度和可打开链接。不要让服务端自动匹配 suitable questions。

## Inputs

Use the smallest useful set:

- learner goal, target band, exam date, weak speaking part;
- learner's core story, experience, topic preference, or existing answer;
- IELTS Buddy practice taxonomy/search/read data when available;
- existing speaking materials from IELTS Buddy when the user wants to update old material.

If exact question links are unavailable, ask the user to choose from data returned by practice search, or provide the browser route. Do not call a create/update tool that promises server-side matching.

## Local Workflow

1. Identify the practice target:
   - Part 1: natural short answers and follow-up range.
   - Part 2: one reusable story with cue-card coverage.
   - Part 3: opinion development, examples, comparison, and abstraction.
2. Read available data:
   - Use `ielts_practice_list_taxonomy`, `ielts_practice_search_parts`, or `ielts_practice_read_part` when the learner needs question-bank choices.
   - Use `ielts_speaking_materials_list` only to inspect owned saved materials.
3. Select exact questions locally.
   - Prefer questions that reuse the learner's real experiences.
   - Avoid grouping unrelated topics just because vocabulary overlaps.
   - Keep the set small: 3-5 Part 1 questions, 1 Part 2 cue card plus 3 follow-ups, or 4-6 Part 3 questions.
4. Build the material:
   - `core_story`: one realistic personal story or opinion base.
   - `question_links`: exact IELTS Buddy question/session/resource links or IDs.
   - `answer_angles`: concise Chinese notes for what to say.
   - `reusable_chunks`: 5-8 English chunks.
   - `avoid`: 2-4 common weak expressions or logic traps.
   - `practice_order`: easy-to-hard sequence.
5. Coach the first answer locally or hand off to `../speaking-coach/WORKFLOW.md`.
6. Persist only if the Agent API tool accepts caller-provided fields without AI matching. If the manifest says omitted links trigger AI matching, supply exact links; if exact links are impossible, skip persistence and return the local material plus browser route.

## Response Shape

```text
本次口语素材主题：<theme>
适合题型：<Part 1/2/3>
为什么这样选：<one evidence-based reason>
题目顺序：
1. <question + link/id>
2. ...
可复用故事线：<Chinese outline>
可复用表达：<English chunks>
先练这一题：<question>
回答后我会按 speaking-coach 做本地反馈。
```

## Agent API Write Policy

Use `ielts_speaking_materials_create` or `ielts_speaking_materials_update` only when all teaching decisions are already made locally and the payload contains explicit question links/IDs plus caller-provided material fields.

Do not call these tools with missing question links, vague matching instructions, or a request for the server to choose questions.
