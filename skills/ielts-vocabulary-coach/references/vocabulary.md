# 我的词书数据契约

四个工具统一操作当前账号的词语与收藏句子。

| 工具 | 输入 | 结果 |
| --- | --- | --- |
| `ielts_vocabulary_search` | `kind=all/word/sentence`，`query`，`limit`（1–50，默认 20），`offset`（默认 0） | `items`、`hasMore`、`nextOffset`；条目包含 `id/kind/text/meaning/sources/createdAt`。完整单词匹配时额外返回 `wordMatch`，无匹配时为 null。 |
| `ielts_vocabulary_add` | `kind=word/sentence`，1–100 条 `items: [{text, meaning?, sourcePartId?}]` | 已保存的 `items` 与 `savedCount`；单条新增也使用同一接口。 |
| `ielts_vocabulary_update` | 完整 `id`，至少一个 `text/meaning` | 更新后的 `item`。 |
| `ielts_vocabulary_delete` | 完整 `id` | `deletedId`。 |

- `text`：词语最长 300 字，句子最长 1000 字；`meaning` 最长 1000 字，由调用方提供。
- 复制工具返回的完整 id，不猜测或拆分 id。
- 重复新增复用条目并更新传入的非空释义。清除释义使用 `update` 的空 `meaning`。
- 普通新增标记“对话添加”。确实从题目收录时，可传已取得的 `sourcePartId`；后端检查已发布并填充标题，不接受自行编造来源标题。修改保留已有来源；句子正文改变时解除旧音频片段。
- 检索、新增和修改均返回“我的词书” `resourceEntry`；条目匹配现有词库时额外返回单词详情入口。`sources` 包含保存的来源标题/语境，可核实的来源还返回 Part 或练习 ID 及原题入口。引用返回的入口，不猜测 URL。
- `wordMatch` 是公开词库匹配，不代表用户已收藏；`items` 才是个人词书。自动匹配只补充入口，不覆盖保存的释义。`dictionaryStatus=unavailable` 表示此次未能检查词库。
- 查找包含该词的其他题目，使用已开启的 `ielts_practice_search_parts`，必要时 `ielts_practice_read_part` 核对；这些是相关题目，不自动写入收藏来源。
- 工具不读写学习进度，不修改公共词库，不执行复习流程。
