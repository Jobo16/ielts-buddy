# IELTS Buddy Agent Skills

IELTS Buddy 本地 Agent 仓库，面向 Codex、Claude Code、Cursor、WorkBuddy 等本地 Agent。仓库把可执行脚本、服务接口说明和可选推荐用法分开维护。

> 本仓库只分发本地 Agent 的 Scripts、Skills 与 Workflows。面向网页 AI 的提示词、效果说明与使用引导，请前往 [IELTS Buddy 技能商店](https://ieltsbuddy.igopx.cn/skills)。

## 仓库分层

| 层级 | 位置 | 职责 |
| --- | --- | --- |
| Scripts | [`scripts/`](scripts) | 通用 API、数据和文档处理脚本。 |
| Skills | [`skills/`](skills) | 说明脚本如何调用、可传输/获得的数据及权限边界。 |
| Workflows | [`workflows/`](workflows) | 可选推荐用法；不改变接口，也不强制本地 Agent 采用。 |

## 安装

需要 Node.js 18+。先查看可安装项：

```sh
npx skills@latest add Jobo16/ielts-buddy --list
```

安装全套：

```sh
npx skills@latest add Jobo16/ielts-buddy --skill '*' --global --yes
```

安装一个 Skill：

```sh
npx skills@latest add Jobo16/ielts-buddy --skill ielts-writing-review --global --yes
```

安装完成后可以直接描述你的学习任务，或明确说“使用 `$ielts-writing-review` 批改这篇作文”。

## 更新

通过 `skills` 安装的学习 Skill 会保存其 GitHub 来源。网络稳定时，可以继续使用 GitHub 更新：

```sh
# 更新全局安装的 IELTS Buddy Skills
npx skills@latest update ielts-study-plan ielts-practice ielts-writing-review ielts-speaking-coach ielts-reading-review ielts-listening-review ielts-vocabulary-coach ielts-mock-review --global --yes
```

在项目内安装时，将 `--global` 改为 `--project`。也可以执行 `npx skills@latest update --global --yes` 更新所有可更新的全局 Skill。

更新只在用户或 Agent 明确执行上述命令时进行；Skill 不会在运行期间静默改写本地文件。

### OSS 更新（网络不稳定时优先使用）

每次 GitHub Release 都会同步生成一份固定 commit、版本和 SHA-256 的 OSS 完整发行包。安装 `ielts-buddy-skills-updater` 后，检查和更新不再依赖 GitHub：

```sh
python3 scripts/update_skills.py check
python3 scripts/update_skills.py update
```

固定入口：

```text
https://ieltsbuddy-content.oss-cn-hangzhou.aliyuncs.com/learner-skills/latest.json
https://ieltsbuddy-content.oss-cn-hangzhou.aliyuncs.com/learner-skills/ielts-buddy-agent-skills.zip
```

如果尚未安装更新 Skill，可以从上面的 OSS ZIP 下载完整包，再用本地目录安装：

```sh
npx skills@latest add ./ielts-buddy-agent-skills --skill '*' --global --yes
```

## 版本

仓库根目录的 [`manifest.json`](manifest.json) 是全套 Skills 的唯一版本来源。每次发布均在 GitHub 创建与该版本严格一致的 `v<version>` tag；发布工作流会校验两者一致，生成 GitHub Release，并同步更新 OSS 的不可变 release、稳定 ZIP 和 `latest.json`。GitHub 是维护真源，OSS 是面向用户的默认下载和更新源。

## 内容来源与维护

脚本、接口契约和可选工作流独立维护；产品能力变化以仓库版本记录为准。

这些 Skills 是学习辅助工具，不替代教师判断、IELTS 官方评分或正式考试材料，也不承诺固定分数结果。

## 可安装 Skills

| Skill | 适用场景 |
| --- | --- |
| [`ielts-study-plan`](skills/ielts-study-plan) | 读取和写入计划、学习路径、资源与学习事件 |
| [`ielts-practice`](skills/ielts-practice) | 查询预测、题库、浏览器练习 session 与已提交结果 |
| [`ielts-buddy-question-research`](skills/ielts-buddy-question-research) | 后台题库权限下读取题库覆盖、目录、材料与标签 |
| [`ielts-writing-review`](skills/ielts-writing-review) | 读取和保存写作提交与修订记录 |
| [`ielts-speaking-coach`](skills/ielts-speaking-coach) | 读取和维护口语素材与练习入口 |
| [`ielts-reading-review`](skills/ielts-reading-review) | 读取已提交阅读练习的结果和按需材料 |
| [`ielts-listening-review`](skills/ielts-listening-review) | 读取已提交听力练习的结果和按需材料 |
| [`ielts-vocabulary-coach`](skills/ielts-vocabulary-coach) | 读取、维护、导入导出和记录词汇数据 |
| [`ielts-mock-review`](skills/ielts-mock-review) | 读取模考试卷目录和已产生的活动数据 |
| [`ielts-buddy-skills-updater`](skills/ielts-buddy-skills-updater) | 从固定 OSS 源检查和更新用户端 Skills 发行包 |

推荐用法见 [`workflows/README.md`](workflows/README.md)。它们需要时才读取，不是安装或调用某个 Skill 的前置条件。

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

默认 API 地址是 `https://work.ieltsbuddy.igopx.cn/api/v1/agent`，可用 `IELTS_BUDDY_API_URL` 覆盖。没有 Token 时，只调用服务端公开能力；不要要求用户提供密码、API Key、浏览器 Cookie 或无关本地文件。

`ielts-buddy-question-research` 同样使用这套绑定，但服务端只向当前拥有后台题库权限的账号暴露题库工具；普通用户无法通过该 Skill 获取内部题库数据。

## 仓库边界

- 仅保存可公开分发的 Scripts、Skills、Workflows、引用资料和验证工具。
- 不包含 IELTS Buddy 网站的卡片文案、网页 AI 提示词、产品源码或私有用户数据。
- 写作批改工作流改编自 MIT 许可来源，许可说明见 [ielts-writing-review-skills.txt](skills/ielts-writing-review/licenses/ielts-writing-review-skills.txt) 与 [third-party-skill-sources.txt](skills/ielts-writing-review/licenses/third-party-skill-sources.txt)。

## 验证

```sh
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests
```

## 许可证

本仓库的 Skills 指令和工具代码使用 [MIT 许可证](LICENSE) 发布。
