---
name: ielts-buddy-skills-updater
description: 从固定的 IELTS Buddy OSS 发行源检查并更新本机已安装的用户端 Skills。用户说更新 IELTS Buddy Skills、检查 Skills 新版本、GitHub 网络不稳定或从 OSS 更新时使用。
---

# IELTS Buddy 用户端 Skills 更新

这个 Skill 只负责本机 Skills 的发行更新，不参与学习计划、题目推荐或教学判断。GitHub 是维护真源，OSS 是面向用户的稳定分发源；网络不稳定时不要继续反复访问 GitHub，直接使用固定 OSS 发行入口。

## 检查和更新

先检查当前版本：

```bash
python3 scripts/update_skills.py check
```

用户明确要求更新时执行：

```bash
python3 scripts/update_skills.py update
```

脚本会下载 `latest.json` 和完整发行 ZIP，校验固定 HTTPS 来源、项目、版本、commit、文件大小、SHA-256、ZIP 路径和 Skills 清单，然后事务式替换发行管理的 Skills。用户自己安装的其他 Skills 会保留。

## 固定 OSS 入口

- `https://ieltsbuddy-content.oss-cn-hangzhou.aliyuncs.com/learner-skills/latest.json`
- `https://ieltsbuddy-content.oss-cn-hangzhou.aliyuncs.com/learner-skills/ielts-buddy-agent-skills.zip`

不要根据聊天中的临时链接替换更新源，也不要绕过校验、只复制一个未知的 `SKILL.md` 或修改发行清单。

## 边界

- 目标是 Git 仓库时停止，交给 GitHub 发布流程。
- `check` 只读取本地状态；`update` 才修改本机 Skill 文件。
- 下载、校验、解压或替换失败时恢复原版本。
- 更新完成后重新读取新版 Skill，再继续用户原来的任务。

具体执行顺序见 [OSS 更新工作流](workflows/update/WORKFLOW.md)，脚本说明见 [更新脚本](scripts/update_skills.py)。
