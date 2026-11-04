# IELTS Buddy 数据接入

只有任务需要站内个人数据时连接；用户提供的题目、作文或答案可直接处理。当前授权与接口以 [Agent 接入文档](https://ieltsbuddy.igopx.cn/developers/api/agent.md) 和运行环境的 `/api/v1/agent/capabilities` 为准，公开操作文档可 GET `/api/v1/agent/capabilities/<operation>.md`。无需安装连接器；有 HTTP 能力的 Agent 可以直接使用公开 REST。

如已安装 `ielts-buddy`，从其安装目录执行 `python3 scripts/ielts_buddy_api.py bind`，让用户打开输出的链接确认当前账号；凭据保存在本地。用 `capabilities` 核对接口，再以 `call <operation> --json '<JSON>'` 调用。只发送 Token 到 IELTS Buddy API origin，不能要求密码、Cookie 或将凭据写入聊天。

查询先读列表，再按稳定 id 读取必要详情；翻页按对应的 nextOffset、nextCursor 或 nextPage，不从部分结果宣称完整。写入只在用户当前任务要求时执行，检查 code、返回 id 与状态，必要时读回。网页正式作答和提交由用户完成，不能调用未开放的内部接口。
