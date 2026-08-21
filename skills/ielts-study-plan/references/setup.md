# IELTS Buddy API 配置

本 Skill 通过仓库根目录的 `scripts/ielts_buddy_api.py` 调用 IELTS Buddy REST API，不需要安装额外连接器，也不需要浏览器授权跳转。

## 绑定账号

1. 在当前 Agent 中运行 `python3 scripts/ielts_buddy_api.py bind`。
2. 打开命令输出的链接；如果已登录，点击“确认绑定当前账号”。
3. 回到 Agent 等待它自动完成绑定；凭据会保存在本机，不需要复制到聊天记录。
4. 再运行 `python3 scripts/ielts_buddy_api.py capabilities` 验证连接。

绑定链接由 bind 命令生成，不要手动打开空的绑定页。请求脚本默认调用 `https://work.ieltsbuddy.igopx.cn/api/v1/agent`；本地测试可通过 `IELTS_BUDDY_API_URL` 或 `--base-url` 覆盖。

```sh
export IELTS_BUDDY_TOKEN='服务器或 CI 环境使用的 token'
python3 scripts/ielts_buddy_api.py capabilities
python3 scripts/ielts_buddy_api.py call ielts_practice_search_parts --json '{"subject":"reading","limit":1}'
```

公开预测和备考资讯操作不需要 Token；个人题库、练习、进度和写入操作需要 Token。脚本只发送 `Authorization: Bearer`，不会输出 Token。

## 调用规则

- 先调用 `capabilities`，以返回的操作、输入和 scope 为准；不要凭记忆拼接操作名或 URL。
- `call` 的参数必须是 JSON；参数很多时使用 `--json -` 并从 stdin 传入。
- API 返回的 `data` 是权威业务结果。写操作完成后按返回结果读回验证；不要把成功 HTTP 状态当成业务验收。
- 401 表示凭据缺失、过期或已撤销；重新运行 `bind`。服务器或 CI 也可以显式设置 `IELTS_BUDDY_TOKEN`。不要改用 Cookie、密码或数据库连接。

没有 API 配置时，仅使用服务端公开能力或说明当前数据不可用；不虚构远程数据。

## 安全说明

Token 只应保存在客户端 Secret 或环境变量中。不要索要或检查密码、私钥、API Key、Token 凭据、浏览器 Cookie 或无关本地目录。

本 Skill 非 IELTS 官方产品，不代表任何考试主办方；分数参考、批改和学习建议仅供备考学习使用，不等同于官方成绩。
