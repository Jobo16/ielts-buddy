# IELTS Buddy Agent Skills

基于“躺着学”雅思教研团队长期教学与学员服务实践整理的 IELTS Agent Skills，持续维护中。面向 Codex、Claude Code、Cursor、WorkBuddy 等本地 Agent，每个 Skill 都可独立安装；安装全套后，Agent 会按任务选择合适的 Skill。

> 本仓库只分发 Agent Skills。面向网页 AI 的提示词、效果说明与使用引导，请前往 [IELTS Buddy 技能商店](https://ieltsbuddy.igopx.cn/skills)。

## 安装

需要 Node.js 18+。先查看可安装项：

```sh
npx skills@latest add Jobo16/ielts-all-in-one-skills --list
```

安装全套：

```sh
npx skills@latest add Jobo16/ielts-all-in-one-skills --skill '*' --global --yes
```

安装一个 Skill：

```sh
npx skills@latest add Jobo16/ielts-all-in-one-skills --skill ielts-writing-review --global --yes
```

安装完成后可以直接描述你的学习任务，或明确说“使用 `$ielts-writing-review` 批改这篇作文”。

## 更新

通过 `skills` 安装的 Skill 会保存其 GitHub 来源。需要更新时，安装器会从该来源检查并同步已安装的 Skill：

```sh
# 更新全局安装的 IELTS Buddy Skills
npx skills@latest update ielts-study-plan ielts-practice ielts-writing-review ielts-speaking-coach ielts-reading-review ielts-listening-review ielts-vocabulary-coach ielts-mock-review --global --yes
```

在项目内安装时，将 `--global` 改为 `--project`。也可以执行 `npx skills@latest update --global --yes` 更新所有可更新的全局 Skill。

更新只在用户或 Agent 明确执行上述命令时进行；Skill 不会在运行期间静默改写本地文件。

## 版本

仓库根目录的 [`manifest.json`](manifest.json) 是全套 Skills 的唯一版本来源。每次发布均在 GitHub 创建与该版本严格一致的 `v<version>` tag；发布工作流会校验两者一致后才生成 Release。因此，GitHub 仓库、tag 和 Release 是可追溯的版本记录，不依赖额外的版本服务。

## 内容来源与维护

本仓库基于“躺着学”雅思教研团队长期教学与学员服务实践整理，并结合 IELTS Buddy 的学习工作流持续维护。内容会随着教研复盘和产品能力更新而调整，版本变更以仓库记录为准。

这些 Skills 是学习辅助工具，不替代教师判断、IELTS 官方评分或正式考试材料，也不承诺固定分数结果。

## 可安装 Skills

| Skill | 适用场景 |
| --- | --- |
| [`ielts-study-plan`](skills/ielts-study-plan) | 诊断、跨技能闭环、每日计划、周复盘、资源推荐 |
| [`ielts-practice`](skills/ielts-practice) | 选一组题、浏览器完成练习、读取结果并复盘 |
| [`ielts-writing-review`](skills/ielts-writing-review) | Task 1/2 审题提纲、批改、二改、DOCX 批注、高价值表达交接 |
| [`ielts-speaking-coach`](skills/ielts-speaking-coach) | Part 1/2/3 陪练、真实经历串题覆盖、口语报告、表达交接 |
| [`ielts-reading-review`](skills/ielts-reading-review) | 阅读错题、证据分析、阅读词汇手册 |
| [`ielts-listening-review`](skills/ielts-listening-review) | 听力错因、精听、错题本 |
| [`ielts-vocabulary-coach`](skills/ielts-vocabulary-coach) | 主动回忆、搭配、词汇复习、CSV/JSON 数据迁移 |
| [`ielts-mock-review`](skills/ielts-mock-review) | 模考成绩、失分模式、训练重点 |

## 可选 IELTS Buddy 服务

每个 Skill 都内置请求脚本。公开预测和备考资讯不需要绑定；需要题库、课程、词汇、练习进度和学习记录时，在当前 Agent 中运行下面的 `bind` 命令，打开命令输出的链接并确认绑定当前 IELTS Buddy 账号。确认后脚本会自动完成绑定并保存本机凭据，适用于 WorkBuddy、Codex、Claude Code、Cursor 等本地 Agent：

```sh
python3 scripts/ielts_buddy_api.py bind
```

绑定链接由 `bind` 命令生成，不要手动打开空的绑定页。绑定完成后先运行 `capabilities` 检查连接，再开始调用个人数据能力；正式作答、听力播放和提交仍在 IELTS Buddy 浏览器页面完成。

```sh
python3 scripts/ielts_buddy_api.py capabilities
python3 scripts/ielts_buddy_api.py call ielts_practice_search_parts --json '{"subject":"reading","limit":1}'
```

服务器或 CI 不使用浏览器时，仍可显式设置 `IELTS_BUDDY_TOKEN`；不要把 Token、Cookie 或密码写入 Skill 或聊天记录。

默认 API 地址是 `https://work.ieltsbuddy.igopx.cn/api/v1/agent`，可用 `IELTS_BUDDY_API_URL` 覆盖。没有 Token 时，各 Skill 仍可基于用户主动提供的作文、题目、答案、文章、听力原文、词表、成绩或转写完成本地学习工作流。不要要求用户提供密码、API Key、浏览器 Cookie 或无关本地文件。

## 仓库边界

- 仅保存可公开分发的 Agent Skills、脚本、引用资料和验证工具。
- 不包含 IELTS Buddy 网站的卡片文案、网页 AI 提示词、产品源码或私有用户数据。
- 写作批改工作流改编自 MIT 许可来源，许可说明见 [ielts-writing-review-skills.txt](skills/ielts-writing-review/licenses/ielts-writing-review-skills.txt) 与 [third-party-skill-sources.txt](skills/ielts-writing-review/licenses/third-party-skill-sources.txt)。

## 验证

```sh
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests
```

## 许可证

本仓库的 Skills 指令和工具代码使用 [MIT 许可证](LICENSE) 发布。
