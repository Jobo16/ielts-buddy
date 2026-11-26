---
name: ielts-buddy-skills-updater
description: 用户要求检查或更新已安装的 IELTS Buddy 学习 Skills 时使用；从GitHub Releases下载并验证完整目录，保留其他 Skills，失败时恢复旧版。
---

# 更新 IELTS Buddy Skills

命令从本 Skill 安装目录执行，实际运行时将脚本解析为绝对路径：

```sh
python3 scripts/update_skills.py check
python3 scripts/update_skills.py update
```

`check` 只读取版本和发行清单；只有用户要求更新时才执行 `update`。脚本从本仓库 GitHub Releases 读取最新稳定版清单，再下载版本对应的 ZIP。校验项目、版本、commit、大小、SHA-256 与 ZIP 路径后替换完整 Skill 目录。更新失败恢复旧目录，其他 Skills 不变。当前版本不再分发的旧 Skill 不自动删除，报告给用户；后台题库工作转到 Operator 工具。

目标属于 Git 维护者仓库时停止，使用 Git 发布流程。更新不改变账号权限，不发送学习数据。完成后读取结果说明实际版本和更新范围，不声称文件安装成功等于学习任务已经完成。
