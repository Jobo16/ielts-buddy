# 词汇 API 数据契约

## 内置词书

| 能力 | 输入 | 输出或写入 |
| --- | --- | --- |
| `ielts_vocabulary_builtin_progress` | `setId`：`core`、`listening` 或 `reading` | 词书进度汇总。 |
| `ielts_vocabulary_builtin_prepare_cards` | `setId`、`mode`、`limit`、可选 `excludeRecentlyReviewedDays` | 数据型卡片，卡片包含稳定的 `entryId`。 |
| `ielts_vocabulary_builtin_record_review` | `setId`、`entryId`、`rating`：`again`、`hard` 或 `good` | 已发生复习的记录。 |

## 个人词汇本

| 能力 | 输入 | 输出或写入 |
| --- | --- | --- |
| `ielts_vocabulary_personal_list`、`ielts_vocabulary_personal_progress`、`ielts_vocabulary_personal_prepare_cards` | 搜索、筛选或卡片参数 | 当前账号个人词汇条目、进度或数据型卡片。 |
| `ielts_vocabulary_personal_add` | 用户确认的词条与可选 `sourceType`、`sourceId`、`sourceTitle`、`context` | 新建或按大小写无关规则合并来源的词条。 |
| `ielts_vocabulary_personal_update`、`ielts_vocabulary_personal_delete` | 条目 `id` 和用户确认的修改或删除 | 修改或删除当前账号词条。 |
| `ielts_vocabulary_personal_record_review` | 条目 `id` 和实际回答的 `rating` | 已发生复习的记录。 |
| `ielts_vocabulary_personal_import`、`ielts_vocabulary_personal_export` | 用户确认的 JSON 或 CSV 内容/格式 | 仅迁移词汇内容，不包含复习历史、掌握度、到期日或 FSRS 状态。 |

所有写入、删除和导入均需用户明确确认。卡片准备接口只返回数据，不执行教学或展示流程。
