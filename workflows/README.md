# IELTS Buddy 可选工作流

这里的内容是推荐用法，不是 Skill 接口契约，也不会因安装某个 Skill 自动生效。

- [`common/`](common)：不要求 IELTS Buddy 接口的通用本地工作流。
- [`skill-enabled/`](skill-enabled)：需要先安装并按对应 Skill 接口获得数据或执行写入的工作流。

每个工作流的 `requiresSkills` 由仓库根目录 [`manifest.json`](../manifest.json) 声明。调用方可以不采用任何工作流，直接按 Skills 中的接口说明取数、传数或调用脚本。
