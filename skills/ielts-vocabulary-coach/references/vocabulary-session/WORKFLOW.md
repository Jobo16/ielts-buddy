# Vocabulary Session

> 当当前学习任务需要本方法时按需读取。脚本命令中的 `scripts/` 相对于本 Skill 根目录；执行时解析为安装目录中的绝对路径。

开启“我的词书”模块即可使用四个管理工具；本工作流仅用于用户额外要求的对话练习。

## 使用已保存内容

调用 `ielts_vocabulary_search`，按用户意图检索词语或句子；使用 `nextOffset` 翻页。用户直接提供内容时，可以直接练习。词义、翻译、提示和例句由 Agent 给出。

## 对话练习

每次给一个简短题目，等用户回答后再反馈。可以做词义回忆、填空或造句；用户停止时结束。总结只依据本次实际回答，不宣称词书掌握度或到期复习状态已更新。

## 保存内容

用户明确要求保存时调用 `ielts_vocabulary_add`：

```json
{"kind":"word","items":[{"text":"allocate","meaning":"分配"}]}
```

保存句子使用 `kind="sentence"`，`meaning` 填翻译。需要修改或删除已有内容时，复制检索返回的完整 id，调用 `ielts_vocabulary_update` 或 `ielts_vocabulary_delete`。工具只管理词书内容，没有复习进度或卡片写回接口。
