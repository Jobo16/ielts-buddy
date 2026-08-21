# 访问边界

本 Skill 使用与其他 IELTS Buddy Skills 相同的用户绑定和 `IELTS_BUDDY_TOKEN`。服务端会在每次 capability discovery 和每次题库工具调用时，检查该 token 对应用户当前是否拥有后台 `question.manage` 权限。

普通用户可以安装本 Skill，但不会看到或调用这三项题库工具，也不能通过普通刷题、资源搜索或浏览器练习接口获取完整内部题库。

运行以下命令生成绑定链接：

```sh
python3 scripts/ielts_buddy_api.py bind
```

绑定后先确认当前账号实际可用的能力：

```sh
python3 scripts/ielts_buddy_api.py capabilities
```

不要把 token、Cookie、题库导出文件或数据库凭据放进对话、Skill、代码仓库或内容成稿。
