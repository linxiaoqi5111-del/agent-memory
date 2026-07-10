---
name: session-tutor
description: "tutor 的别名入口。用户输入“session tutor”、@session-tutor，或要求在会话结束时整理科普内容时触发；先提交候选摘要供用户检阅，明确批准后才写入 70_tutor。"
---

# Session Tutor Alias

立即激活并严格执行 `tutor` skill 的完整流程。

- 第一阶段只生成候选摘要，不创建或修改 `70_tutor/` 文件。
- 阻塞等待用户明确批准具体候选编号或标题。
- 只有收到“批准 <编号/标题> 落库”后，才能进入写入、校验和提交阶段。
- 如果当前环境无法加载 `tutor` skill，停止写入并告知用户；不得用简化流程绕过人审闸门。
