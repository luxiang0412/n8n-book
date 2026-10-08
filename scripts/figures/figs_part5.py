"""Part V figures: models, agent loop, engine request, tools, streaming."""

from svg import MUTED, Fig


def fig_models() -> Fig:
    f = Fig(920, 330, "Agent 只依赖 ChatModel.invoke(messages, {tools, onToken})；Mock 实现离线确定，OpenAI 兼容实现覆盖 OpenAI、Ollama 等；日志包装把每次调用记为模型节点的一次运行。")
    f.title("模型抽象：一个接口，多种实现", "packages/nodes-ai/src/models/")
    f.box(30, 120, 170, 80, "AI Agent / LLM Chain", "只调用 invoke()", tone="accent", size=12)
    f.box(270, 110, 220, 100, "ChatModel", "invoke(messages, {\n  tools?, signal?, onToken?\n}) → { content, toolCalls }", tone="neutral", size=12, mono=True)
    f.box(560, 70, 160, 50, "logModel 包装", "addInput/OutputData", tone="purple", size=11)
    f.box(560, 150, 160, 50, "MockChatModel", "离线 · 确定", tone="teal", size=12)
    f.box(560, 230, 160, 50, "OpenAI 兼容", "fetch + SSE 解析", tone="teal", size=12)
    f.box(770, 200, 130, 34, "OpenAI / DeepSeek", tone="muted", size=11)
    f.box(770, 244, 130, 34, "Ollama /v1", tone="muted", size=11)
    f.arrow([(200, 160), (270, 160)])
    f.arrow([(490, 140), (560, 95)])
    f.arrow([(490, 165), (560, 175)])
    f.arrow([(490, 190), (560, 255)])
    f.arrow([(720, 250), (770, 217)])
    f.arrow([(720, 258), (770, 261)])
    f.text(460, 310, "工具调用 = 模型输出的结构化“意图”，执行由调用方负责", size=12, weight="600")
    return f


def fig_loop() -> Fig:
    f = Fig(940, 380, "Tools Agent 循环：第一轮模型请求工具，Agent 返回 EngineRequest 由引擎执行工具；引擎带着 EngineResponse 恢复 Agent，Agent 把调用和结果拼进 scratchpad，第二轮模型给出最终回答并写入记忆。")
    f.title("Tools Agent 的一次循环", "Agent.execute() 被调用两次；状态保存在 EngineRequest.metadata 里")
    f.box(30, 90, 220, 120, "① Agent.execute()", "messages = system\n+ 记忆历史 + user\n+ scratchpad(空)", tone="accent", size=12)
    f.box(320, 90, 170, 60, "模型", "toolCalls: Calculator", tone="neutral", size=12)
    f.box(560, 90, 160, 60, "EngineRequest", "actions + metadata", tone="warn", size=12)
    f.box(780, 90, 140, 60, "引擎执行", "Calculator 节点", tone="teal", size=12)
    f.arrow([(250, 120), (320, 120)], "invoke")
    f.arrow([(490, 120), (560, 120)], "return")
    f.arrow([(720, 120), (780, 120)])
    f.box(30, 250, 220, 100, "② Agent.execute(response)", "scratchpad = buildSteps()\n= [调用 + 结果 \"87\"]", tone="accent", size=12)
    f.box(320, 260, 170, 60, "模型", "content: \"...87.\"", tone="neutral", size=12)
    f.box(560, 260, 160, 60, "最终输出", "{ output }", tone="ok", size=12)
    f.box(780, 260, 140, 60, "Simple Memory", "saveContext()", tone="purple", size=12)
    f.arrow([(850, 150), (850, 200), (140, 200), (140, 250)], "EngineResponse（工具结果 + metadata）", tone="teal", label_at=0.5)
    f.arrow([(250, 290), (320, 290)], "invoke")
    f.arrow([(490, 290), (560, 290)])
    f.arrow([(720, 290), (780, 290)])
    f.text(470, 368, "iterationCount ≥ maxIterations 时报错；多个工具调用放进同一个 EngineRequest", size=11, color=MUTED)
    return f


def _stack(f: Fig, ox: int, title: str, items: list[tuple[str, str]], note: str):
    f.text(ox, 88, title, size=12, anchor="start", weight="700")
    f.rect(ox, 98, 200, 170, fill="#ffffff", stroke="#cbd5e1")
    f.text(ox + 8, 116, "执行栈（头在上）", size=10, anchor="start", color=MUTED)
    for i, (name, tone) in enumerate(items):
        f.box(ox + 14, 124 + i * 34, 172, 28, name, tone=tone, size=11)
    if not items:
        f.text(ox + 100, 190, "（空）", size=11, color=MUTED)
    f.lines(ox, 290, note.split("\n"), size=11, anchor="start", color=MUTED)


def fig_request() -> Fig:
    f = Fig(940, 360, "EngineRequest 前后执行栈：Agent 返回请求后，两个工具压到栈顶，Agent 带着恢复元数据压在它们下面；工具依次执行；Agent 再次被弹出并拿到两条结果。")
    f.title("EngineRequest：工具压栈，Agent 压回去", "Calculator 和 Shout 被同一轮请求")
    _stack(f, 20, "① 弹出 Agent", [], "Agent.execute() 返回\nEngineRequest（2 个 action）")
    _stack(f, 250, "② handleEngineRequest", [("Calculator", "teal"), ("Shout", "teal"), ("AI Agent（resume）", "warn")], "工具预留运行记录\ninputOverride = 模型给的参数")
    _stack(f, 480, "③ 工具执行完", [("AI Agent（resume）", "warn")], "工具输出记为 ai_tool\n不会调度下游")
    _stack(f, 710, "④ 恢复 Agent", [], "collectSubNodeResults()\n→ EngineResponse（2 条结果）")
    return f


def fig_tools() -> Fig:
    f = Fig(940, 340, "四种工具来源：专用工具节点、由普通节点合成的工具（$fromAI 填参数）、子工作流、MCP 服务器的工具集；最终都是一个带 name/description/schema 和 sourceNodeName 的工具定义。")
    f.title("工具从哪里来", "最终都变成 AiTool { name, description, schema, metadata.sourceNodeName }")
    rows = [
        (80, "专用工具节点", "Calculator · Code Tool", "supplyData() 自己给定义", "teal"),
        (140, "节点即工具", "HTTP Request Tool …", "合成 xxxTool · $fromAI() → schema", "accent"),
        (200, "工作流即工具", "Call Workflow Tool", "executeWorkflow() 跑子工作流", "purple"),
        (260, "MCP", "MCP Client Tool", "tools/list → 一个 Toolkit 多个工具", "warn"),
    ]
    for y, name, ex, how, tone in rows:
        f.box(30, y, 170, 46, name, ex, tone=tone, size=12)
        f.text(220, y + 28, how, size=11, anchor="start", color=MUTED)
        f.arrow([(470, y + 23), (560, 190)], tone="muted")
    f.box(560, 150, 180, 80, "AiTool", "给模型看的定义\n+ 由哪个节点执行", tone="ok", size=12)
    f.box(780, 150, 130, 80, "AI Agent", "tools 列表", tone="accent", size=12)
    f.arrow([(740, 190), (780, 190)])
    return f


def fig_streaming() -> Fig:
    f = Fig(940, 320, "流式：模型 token 经 onToken 到 Agent，Agent 调 sendChunk，sendChunk 钩子由创建执行的一方注册：生产 Webhook 写 NDJSON 到 HTTP 响应，编辑器手动执行则推送给标签页。")
    f.title("流式数据穿过的层次", "每层只知道下一层的接口")
    f.box(20, 120, 140, 60, "模型", "SSE delta", tone="neutral", size=12)
    f.box(210, 120, 150, 60, "AI Agent", "sendChunk(type, i, text)", tone="accent", size=11)
    f.box(410, 120, 170, 60, "生命周期钩子", "sendChunk 处理函数", tone="teal", size=12)
    f.box(640, 70, 270, 56, "生产 Webhook（streaming）", "NDJSON → HTTP 响应", tone="warn", size=12)
    f.box(640, 180, 270, 56, "编辑器手动执行", "push: chatChunk → 聊天面板", tone="purple", size=12)
    f.arrow([(160, 150), (210, 150)], "onToken")
    f.arrow([(360, 150), (410, 150)])
    f.arrow([(580, 140), (640, 98)])
    f.arrow([(580, 160), (640, 208)])
    f.text(470, 290, '{"type":"begin"} {"type":"item","content":"Based "} … {"type":"end"}', size=11, mono=True, color=MUTED)
    return f


FIGS = {
    "fig-17-models": fig_models,
    "fig-18-loop": fig_loop,
    "fig-19-request": fig_request,
    "fig-20-tools": fig_tools,
    "fig-21-streaming": fig_streaming,
}
