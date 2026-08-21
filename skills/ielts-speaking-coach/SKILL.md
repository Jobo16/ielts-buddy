---
name: ielts-speaking-coach
description: 说明如何读写当前账号的 IELTS Buddy 口语素材和练习入口；不定义口语陪练、反馈或素材组织方法。
---

# IELTS Buddy 口语素材接口

本 Skill 只说明用户口语素材的读写接口。调用前，先按[Agent API 配置](references/setup.md)绑定并检查能力。

## 接口

| 能力 | 数据或动作 | 调用约束 |
| --- | --- | --- |
| `ielts_speaking_materials_list` | 当前账号的口语素材目录 | 仅读取当前账号数据。 |
| `ielts_speaking_materials_create`、`ielts_speaking_materials_update`、`ielts_speaking_materials_archive` | 创建、更新、归档用户确认的素材 | 仅提交用户明确确认的内容。 |
| `ielts_speaking_materials_start_practice` | 指定素材的练习入口 | 原样使用服务端返回入口，不自行拼接 URL。 |

```sh
python3 scripts/ielts_buddy_api.py capabilities
python3 scripts/ielts_buddy_api.py call ielts_speaking_materials_list --json '{}'
```

## 边界

- 不把对话中的推断自动写成用户素材。
- 本 Skill 不定义话题选择、回答反馈、评分或练习顺序。
- `workflows/` 是独立的可选推荐层，不属于本 Skill 的接口契约。
