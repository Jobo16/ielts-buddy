# MCP 配置说明

刷题数据、练习历史和浏览器入口来自可选的 IELTS Buddy MCP 服务。没有连接 MCP 时，不要虚构题库数据；可继续处理用户主动提供的题目和答案，并给出网页入口。

```text
name: ielts-buddy
url: https://ieltsbuddy.igocn.cn/mcp
transport: streamable HTTP
auth: OAuth
```

不要向用户索要 `client_id`、`client_secret`、access token、refresh token、密码、API Key、私钥或浏览器 cookie。客户端会通过浏览器完成 OAuth 授权。

MCP OAuth 只授权本地 Agent 调用 IELTS Buddy 接口。首次打开 MCP 返回的练习链接时，浏览器可能仍需登录 IELTS Buddy；登录后会自动回到原练习，且应使用创建该 session 的同一账号。

## Codex

```toml
[mcp_servers.ielts-buddy]
url = "https://ieltsbuddy.igocn.cn/mcp"
```

```sh
codex mcp login ielts-buddy
```

## Claude Code

```sh
claude mcp add --scope user --transport http ielts-buddy "https://ieltsbuddy.igocn.cn/mcp"
claude mcp login ielts-buddy
```

其他客户端创建一个名为 `ielts-buddy` 的 streamable HTTP MCP server，使用 OAuth 授权即可。
