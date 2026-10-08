"""Part VI figures: RAG pipelines, vector store modes, nested agents, human approval."""

from svg import MUTED, Fig


def fig_rag() -> Fig:
    f = Fig(960, 400, "RAG 的两条流水线：写入时把条目切块、向量化后存入向量库；提问时 Agent 把问题交给检索工具，工具把问题向量化，用余弦相似度取前 k 块，作为工具结果交给模型生成回答。")
    f.title("RAG：先写入，再检索", "两个工作流共享同一个 Memory Key")
    xs = [40, 225, 410, 595, 780]
    w = 125
    f.group(20, 70, 920, 130, "写入工作流（Insert Documents）", tone="teal")
    top = [("Code / HTTP", "3 个条目", "neutral"), ("Data Loader", "切块 + 元数据", "teal"), ("Embeddings", "embedDocuments()", "purple"), ("向量库", "key = kb", "warn"), ("输出", "3 个块", "ok")]
    for x, (a, b, tone) in zip(xs, top):
        f.box(x, 110, w, 60, a, b, tone=tone, size=12)
    for i, label in enumerate([None, "文本块", "向量", None]):
        f.arrow([(xs[i] + w, 140), (xs[i + 1], 140)], label)

    f.group(20, 230, 920, 140, "提问工作流（Retrieve as Tool）", tone="accent")
    bottom = [("AI Agent", "调用工具", "accent"), ("检索工具", "{ query }", "teal"), ("Embeddings", "embedQuery()", "purple"), ("余弦相似度", "取前 k 块", "warn"), ("模型", "依据块作答", "neutral")]
    for x, (a, b, tone) in zip(xs, bottom):
        f.box(x, 270, w, 60, a, b, tone=tone, size=12)
    for i, label in enumerate([None, "问题", "问题向量", "工具结果"]):
        f.arrow([(xs[i] + w, 300), (xs[i + 1], 300)], label)
    f.arrow([(xs[3] + 62, 270), (xs[3] + 62, 170)], "查同一个库", tone="muted", dashed=True, label_at=0.5, label_dx=40)
    f.text(480, 392, "写入和检索必须用同一个 Embeddings 模型：向量只能和同一模型产生的向量比较", size=11, color=MUTED)
    return f


def fig_modes() -> Fig:
    f = Fig(960, 330, "同一个 Simple Vector Store 节点的三种模式：Insert 有主输入、Embedding 和 Document 子输入，输出主数据；Get Many 有主输入和 Embedding，输出匹配的块；Retrieve as Tool 只有 Embedding 输入，输出 ai_tool 连到 Agent。")
    f.title("一个节点，三种模式：端口由参数决定", "inputs / outputs 是以 $parameter 求值的表达式")
    cols = [
        (40, "Insert Documents", ["main", "Embedding*", "Document*"], "main（写入的块）", "warn"),
        (350, "Get Many", ["main", "Embedding*"], "main（匹配的块）", "teal"),
        (660, "Retrieve as Tool", ["Embedding*"], "ai_tool → Agent", "accent"),
    ]
    for x, name, ins, out, tone in cols:
        f.box(x, 90, 260, 70, "Simple Vector Store", f"mode = {name}", tone=tone, size=13)
        for i, label in enumerate(ins):
            sub = label != "main"
            f.box(x + i * 88, 200, 82, 34, label, tone="purple" if sub else "neutral", size=11, dashed=sub)
            f.arrow([(x + i * 88 + 41, 200), (x + i * 88 + 41, 160)], tone="purple" if sub else "neutral", dashed=sub)
        f.text(x + 30, 282, "输出", size=11, anchor="start", color=MUTED)
        f.box(x + 70, 265, 180, 30, out, tone="ok", size=11)
    f.text(480, 318, "切换模式时，编辑器重新求值表达式，画布上的端口随之变化", size=11, color=MUTED)
    return f


def fig_nested() -> Fig:
    f = Fig(960, 380, "嵌套 EngineRequest：外层 Agent 请求 Research 工具；Research 本身是 Agent，它又请求 Calculator；引擎先执行 Calculator，恢复 Research，再恢复外层 Agent。每一层都只是“返回请求、带着结果被再次调用”。")
    f.title("Agent 调用 Agent：请求嵌套请求", "引擎不知道“多 Agent”，它只处理 EngineRequest")
    steps = [
        ("① 弹出 AI Agent", [], "返回请求：Research"),
        ("② Research 在栈顶", [("Research", "teal"), ("AI Agent（resume）", "warn")], "Research 也是 Agent"),
        ("③ Research 返回请求", [("Calculator", "teal"), ("Research（resume）", "warn"), ("AI Agent（resume）", "warn")], "返回请求：Calculator"),
        ("④ Calculator 完成", [("Research（resume）", "warn"), ("AI Agent（resume）", "warn")], "Research 得到 42"),
        ("⑤ Research 完成", [("AI Agent（resume）", "warn")], "Agent 得到 Research 的回答"),
    ]
    for i, (title, items, note) in enumerate(steps):
        ox = 20 + i * 188
        f.text(ox, 88, title, size=12, anchor="start", weight="700")
        f.rect(ox, 98, 176, 150, fill="#ffffff", stroke="#cbd5e1")
        for j, (name, tone) in enumerate(items):
            f.box(ox + 10, 112 + j * 40, 156, 32, name, tone=tone, size=11)
        if not items:
            f.text(ox + 88, 178, "（空）", size=11, color=MUTED)
        f.text(ox, 272, note, size=11, anchor="start", color=MUTED)
    f.text(480, 318, "运行次数：AI Agent 1 · Boss Model 2 · Research 1 · Research Model 2 · Calculator 1", size=12, weight="600")
    f.text(480, 346, "Research 的“运行”包含两次 execute() 调用；嵌套深度只受 maxIterations 和栈内存限制", size=11, color=MUTED)
    return f


def fig_hitl() -> Fig:
    f = Fig(980, 420, "人工审批跨两段执行：第一段里 Agent 请求被保护的工具，引擎运行 Human Approval，它保存一次性令牌、调用 putExecutionToWait，执行以 waiting 状态存入数据库；审批人打开链接后，服务器校验令牌、写入决定，从数据库恢复执行；Human Approval 再次运行并请求真正的工具，结果交回 Agent。")
    f.title("人工审批：执行停下，等人，再继续", "两段执行之间，所有状态都在数据库里的 IRunExecutionData")
    lanes = [("AI Agent", 100), ("Human Approval", 160), ("Refund（被保护）", 220), ("数据库", 280), ("审批人 / 服务器", 340)]
    for name, y in lanes:
        f.text(20, y + 4, name, size=11, anchor="start", weight="600")
        f.line(150, y, 960, y, dashed=True)
    f.box(160, 86, 120, 28, "请求工具", tone="accent", size=11)
    f.arrow([(220, 114), (220, 146)], tone="accent")
    f.box(230, 146, 150, 28, "存令牌 · 等待", tone="warn", size=11)
    f.arrow([(305, 174), (305, 266)], "status = waiting", tone="warn", label_at=0.75, label_dx=50)
    f.box(260, 266, 110, 28, "执行已保存", tone="muted", size=11)
    f.rect(400, 76, 120, 290, fill="#f8fafc", stroke="#e5e7eb", dashed=True)
    f.text(460, 230, "……几分钟", size=11, color=MUTED)
    f.text(460, 248, "或几天……", size=11, color=MUTED)
    f.box(540, 326, 170, 28, "GET …?token&decision", tone="purple", size=11, mono=True)
    f.arrow([(600, 326), (600, 294)], "校验令牌", tone="purple", label_dx=34)
    f.box(550, 266, 140, 28, "写入决定 · 恢复", tone="muted", size=11)
    f.arrow([(650, 266), (650, 174)], tone="neutral")
    f.box(610, 146, 140, 28, "再次运行：批准", tone="warn", size=11)
    f.arrow([(750, 160), (780, 206)], "EngineRequest", tone="teal", label_dx=20)
    f.box(770, 206, 100, 28, "执行退款", tone="teal", size=11)
    f.arrow([(870, 206), (900, 114)], "结果", tone="ok", label_dx=18)
    f.text(880, 252, "（经 Human Approval 交回）", size=10, color=MUTED)
    f.box(860, 86, 100, 28, "最终回答", tone="ok", size=11)
    f.text(490, 404, "拒绝时：Human Approval 不发请求，直接告诉 Agent “人类拒绝了这次调用”", size=11, color=MUTED)
    return f


FIGS = {
    "fig-22-rag": fig_rag,
    "fig-22-modes": fig_modes,
    "fig-23-nested": fig_nested,
    "fig-23-hitl": fig_hitl,
}
