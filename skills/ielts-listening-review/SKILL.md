---
name: ielts-listening-review
description: 说明如何读取 IELTS Buddy 已提交听力练习的结果与按需材料；不定义听力诊断、精听或教学方案。
---

# IELTS Buddy 听力结果接口

本 Skill 只说明已提交练习数据的读取方式。需要账号数据时，先按[Agent API 配置](references/setup.md)绑定并检查能力。

## 接口

| 能力 | 数据 | 调用约束 |
| --- | --- | --- |
| `ielts_practice_read_review` | 已提交 session 的题目编号、题型、题干、用户作答、答案 key 与可选材料快照 | 只读取当前账号已提交的 session；仅需要原始材料时传 `includeMaterial:true`。 |
| `ielts_practice_read_session` | session 状态和浏览器入口 | 用于确认 session 是否存在及是否已提交。 |

```sh
python3 scripts/ielts_buddy_api.py capabilities
python3 scripts/ielts_buddy_api.py call ielts_practice_read_review --json '{"sessionId":"<session-id>","includeMaterial":false}'
```

## 边界

- 服务端返回事实数据，不定位证据、不判断错因、不生成训练建议。
- 正式作答、播放和提交在浏览器练习页完成。
- `workflows/` 是独立的可选推荐层，不属于本 Skill 的接口契约。
