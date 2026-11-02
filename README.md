# IELTS Buddy 本地学习 Skills

给 Codex、Claude Code、Cursor 等本地 Agent 使用的雅思学习方法。作文批改、口语陪练、阅读与听力复盘、词汇训练、刷题、模考和学习安排均可处理用户提供的材料；需要本人网站记录时，再按 [IELTS Buddy Agent API](https://ieltsbuddy.igopx.cn/developers/api/agent.md) 连接账号。

## 安装

需要 Node.js 18+ 与 Python 3。每个 Skill 目录都包含自己的方法、资料和必要脚本，可以单独安装：

```sh
npx skills@latest add Jobo16/ielts-buddy --list
npx skills@latest add Jobo16/ielts-buddy --skill ielts-writing-review --global --yes
```

安装全部：

```sh
npx skills@latest add Jobo16/ielts-buddy --skill '*' --global --yes
```

安装完后直接描述学习任务，例如“用 `$ielts-writing-review` 批改这篇 Task 2 作文”。用户给出作文、题目或答案时可以立即工作；没有必要先绑定网站账号。需要网站中的个人记录时，安装 `$ielts-buddy`，从其安装目录运行 `python3 scripts/ielts_buddy_api.py bind`，打开输出链接确认当前账号，再运行 `python3 scripts/ielts_buddy_api.py capabilities`。也可以使用 Agent 自带的 HTTP 能力按在线文档直接连接。Token 只保存在私有凭据中。

## 可安装内容

| Skill | 完成的任务 |
| --- | --- |
| [`ielts-buddy`](skills/ielts-buddy) | 可选的网站数据接入、个人学习快照和授权写入 |
| [`ielts-study-plan`](skills/ielts-study-plan) | 每日学习、周复盘和按要求保存待办 |
| [`ielts-practice`](skills/ielts-practice) | 选题、本地练习或网页正式练习交接 |
| [`ielts-writing-review`](skills/ielts-writing-review) | Task 1/2 批改、写前规划、二改对照和按需 Word 文档 |
| [`ielts-speaking-coach`](skills/ielts-speaking-coach) | 逐题陪练、真实经历整理和覆盖图 |
| [`ielts-reading-review`](skills/ielts-reading-review) | 阅读错题复盘、精读和词块整理 |
| [`ielts-listening-review`](skills/ielts-listening-review) | 听力错题、精听记录与修复练习 |
| [`ielts-vocabulary-coach`](skills/ielts-vocabulary-coach) | 少量词句主动回忆和按需收藏 |
| [`ielts-mock-review`](skills/ielts-mock-review) | 模考科目证据复盘及按要求组卷 |
| [`ielts-buddy-skills-updater`](skills/ielts-buddy-skills-updater) | 从固定 OSS 源检查、更新本机发行包 |

每个 Skill 只读取当前任务所需的方法文件。实际课程学习、听力播放、正式计时作答、交卷与站内写作修订在 [IELTS Buddy 工作台](https://work.ieltsbuddy.igopx.cn/workspace) 完成。后台题库管理及研究请使用独立 Operator Skills；学习者账号授权不能代替后台权限。

## 更新与发行

使用 GitHub 来源安装的 Skill 可由 `npx skills@latest update --global --yes` 在用户要求时更新。网络不稳定时，已安装的 `$ielts-buddy-skills-updater` 可执行 `python3 scripts/update_skills.py check` 或 `update`；它使用固定 [OSS 发行清单](https://ieltsbuddy-content.oss-cn-hangzhou.aliyuncs.com/learner-skills/latest.json)，核对版本、提交、大小和 SHA-256，失败恢复旧版。更新不会在学习任务中静默进行。

根目录 `manifest.json` 是版本和 Skill 清单。GitHub tag、GitHub Release 与 OSS 发行包使用同一版本和 commit。单个 Skill 从 GitHub 安装与从 OSS 安装后都应能找到其引用的方法和脚本。

## 维护验证

```sh
python3 scripts/sync_shared.py --check
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests
python3 scripts/check_contract.py --live  # 发布前核对已部署的公开接口
```

公开 API 快照在 [`contracts/agent-api-public.json`](contracts/agent-api-public.json)，由主应用能力注册表导出。新增或修改外部能力时，先修改主应用契约，再刷新快照及受影响的 Skill。当前网页 AI 的提示词属于主站，不在此仓库复制维护。

这些方法辅助备考，不代表 IELTS 官方评分或正式考试结果。Skill 代码和指令按 [MIT License](LICENSE) 发布；第三方改编来源见写作 Skill 中的许可文件。
