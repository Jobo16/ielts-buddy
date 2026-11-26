# IELTS Buddy 雅思学习 Skills

用 Codex、Claude Code 或 Cursor 批改雅思作文、练习口语、复盘错题。带上自己的材料就能开始。读取站内记录、查课程进度或保存待办时，可连接 IELTS Buddy 开放 API。

[选择 Skill](#选择-skill) · [连接 IELTS Buddy](#连接-ielts-buddy) · [开放 API](https://ieltsbuddy.igopx.cn/developers/api) · [发行版本](https://github.com/Jobo16/ielts-buddy/releases)

## 安装并试一次

使用 Node.js 22.20 或更高版本运行 Skills 安装器。先安装写作批改：

```sh
npx skills@latest add Jobo16/ielts-buddy --skill ielts-writing-review --global --yes
```

把题目和作文发给你的助手，例如：

> 用 `$ielts-writing-review` 批改下面这篇 IELTS Task 2 作文。按四项评分标准给出反馈，每项引用一处原文，并指出我二改时最该先改哪里。

## 选择 Skill

| Skill | 可以做什么 | 何时需要连接网站 |
| --- | --- | --- |
| [写作批改](skills/ielts-writing-review) | Task 1／2 批改、修改前后对照、生成 Word 批注稿 | 读取已保存的作文版本或批改记录 |
| [口语陪练](skills/ielts-speaking-coach) | 逐题陪练、表达反馈、整理真实经历 | 查站内题目或读写个人口语素材 |
| [阅读复盘](skills/ielts-reading-review) | 分析错因、同义替换和长难句 | 读取已提交练习或模考科目的证据 |
| [听力复盘](skills/ielts-listening-review) | 用提供的答案和稿件复盘，设计短段精听 | 读取站内听力练习或精听记录 |
| [选题与刷题](skills/ielts-practice) | 按需求选题，或用自带材料练习 | 查询站内题库、读取练习记录或按当前接口保存个人练习 |
| [模考复盘](skills/ielts-mock-review) | 复盘提供的模考结果，制定下一步训练任务 | 读取站内模考科目证据或组卷 |
| [词汇练习](skills/ielts-vocabulary-coach) | 用提供的词句做主动回忆与语境练习 | 查看或保存个人词书条目 |
| [学习规划](skills/ielts-study-plan) | 结合备考目标、时间和现有证据安排学习 | 查课程进度、读取学习快照或保存待办 |

课程播放、正式计时作答、交卷和站内作文二改在 [IELTS Buddy 工作台](https://work.ieltsbuddy.igopx.cn/workspace) 完成。

## 连接 IELTS Buddy

公开备考资讯与预测记录可匿名读取。需要读取或写入个人数据时，先安装 [`ielts-buddy`](skills/ielts-buddy) 数据接入 Skill：

```sh
npx skills@latest add Jobo16/ielts-buddy --skill ielts-buddy --global --yes
```

使用 Python 3.10 或更高版本，在安装后的 `ielts-buddy` 目录运行：

```sh
python3 scripts/ielts_buddy_api.py bind
python3 scripts/ielts_buddy_api.py me
```

先打开第一条命令给出的链接，在 IELTS Buddy 确认账号授权。绑定完成后用第二条命令核对账号。外部调用方也可以按网站指南直接通过 HTTP 接入。当前接口、参数和权限以网站目录为准。[HTTP 接入指南](https://ieltsbuddy.igopx.cn/developers/api/agent.md) · [接口目录](https://ieltsbuddy.igopx.cn/developers/api)

## 安装全部与更新

```sh
npx skills@latest add Jobo16/ielts-buddy --skill '*' --global --yes
```

通过 GitHub 安装的 Skills 可按名称更新，例如 `npx skills@latest update ielts-writing-review`。完整包在 [GitHub Releases](https://github.com/Jobo16/ielts-buddy/releases) 提供。已安装新版 [Skills 更新工具](skills/ielts-buddy-skills-updater) 时，可从 GitHub 检查稳定版本并在确认后更新。

若当前使用的是 `0.18.0` 的完整包，请在新版发行后从 GitHub Releases 获取新包。之后可继续使用包内更新工具。

## 社区与维护

[社区雅思 Agent Skills 索引](catalog/community-ielts-skills.md)收录其他作者维护的项目。仓库的 [API 契约快照](contracts/agent-api-public.json)用于校验兼容性，实际开放能力以网站为准。

<details>
<summary>维护与验证命令</summary>

```sh
python3 scripts/sync_shared.py --check
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests
python3 scripts/check_contract.py --live
```

</details>

这些方法辅助备考。Skill 代码和指令采用 [MIT License](LICENSE)。
