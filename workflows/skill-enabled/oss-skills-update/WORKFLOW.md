# OSS 更新工作流

> 这是可选推荐用法，不是 Skill 接口契约或强制执行要求。只有用户要求采用该用法时才读取和使用。

1. 确认用户要求的是检查还是实际更新；只检查时运行 `python3 ../../../scripts/update_skills.py check`。
2. 确认当前 Skills 根目录不是 Git 维护仓库，也不是用户要求保留的源码工作区。
3. 用户明确要求更新时运行 `python3 ../../../scripts/update_skills.py update`。
4. 向用户报告更新前后的 commit、版本、Skills 数量和保留的其他 Skills。
5. 如果更新失败，报告失败阶段，不手动复制文件，不绕过 HTTPS、大小或 SHA-256 校验。
