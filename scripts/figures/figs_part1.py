"""Part I figures: forms, architecture, one execution trace."""

from svg import MUTED, Fig


def fig_spectrum() -> Fig:
    f = Fig(900, 330, "从确定性工作流到自主 Agent：越往右，控制权越多地交给模型；n8n 在同一张画布上覆盖全部五种形态。")
    f.title("Workflow ↔ Agent 光谱", "谁决定下一步做什么？")
    xs = [30, 205, 380, 555, 730]
    forms = [
        ("① 触发→动作", "一条直线", "Webhook → HTTP", "neutral"),
        ("② 分支/合并/循环", "人画好的图", "If · Merge · Loop", "neutral"),
        ("③ LLM Chain", "步骤里调模型", "Basic LLM Chain", "teal"),
        ("④ 工作流中的 Agent", "模型选工具", "AI Agent + Tools", "accent"),
        ("⑤ 多 Agent / HITL", "Agent 调 Agent", "Agent Tool · 审批", "purple"),
    ]
    for x, (name, sub, example, tone) in zip(xs, forms):
        f.box(x, 100, 150, 70, name, sub, tone=tone, size=13)
        f.text(x + 75, 196, example, size=11, color=MUTED, mono=True)
    for a, b in zip(xs, xs[1:]):
        f.arrow([(a + 150, 135), (b, 135)])
    f.arrow([(40, 240), (870, 240)], tone="accent", sw=2)
    f.text(40, 262, "人决定路径：可预测、可审计、便宜", size=12, anchor="start", color=MUTED)
    f.text(870, 262, "模型决定路径：灵活、难预测、更贵", size=12, anchor="end", color=MUTED)
    f.text(450, 300, "n8n 的选择：Agent 只是图里的一个节点，外层仍是确定性工作流", size=12, weight="600")
    return f


def fig_packages() -> Fig:
    f = Fig(900, 400, "n8n 的包依赖分层：cli 组装一切；节点包只依赖 n8n-workflow 的接口；n8n-workflow 前后端共用。")
    f.title("包依赖分层", "箭头 = 依赖方向（只能向下）")
    f.box(330, 80, 240, 56, "n8n (packages/cli)", "REST · DB · Webhook · Push · 队列", tone="accent")
    f.box(40, 80, 220, 56, "editor-ui (Vue 3)", "画布 · NDV · Pinia", tone="purple")
    f.box(640, 80, 220, 56, "@n8n/db", "TypeORM 实体与仓储", tone="neutral")
    f.box(330, 190, 240, 56, "n8n-core", "WorkflowExecute · 节点上下文", tone="teal")
    f.box(640, 190, 220, 56, "nodes-base / nodes-langchain", "445 + 125 个节点", tone="neutral", size=12)
    f.box(330, 300, 240, 56, "n8n-workflow", "类型 · 图 · 表达式（前后端共用）", tone="ok")
    f.arrow([(450, 136), (450, 190)])
    f.arrow([(570, 108), (640, 108)])
    f.arrow([(570, 125), (640, 205)])
    f.arrow([(450, 246), (450, 300)])
    f.arrow([(750, 246), (750, 328), (570, 328)], "只依赖接口", tone="ok", label_at=0.3)
    f.arrow([(150, 136), (150, 328), (330, 328)], "表达式预览", tone="purple", label_at=0.35)
    f.arrow([(640, 222), (570, 222)], "注入", tone="teal", dashed=True, label_dy=-8)
    return f


def fig_topology() -> Fig:
    f = Fig(900, 400, "regular 模式下 main 进程自己执行；queue 模式下 main/webhook 进程只接活，把执行放进 Redis 队列，由 worker 执行，数据统一写数据库。")
    f.title("两种执行模式的进程拓扑", "EXECUTIONS_MODE=regular（默认）/ queue")
    # regular
    f.group(24, 76, 300, 300, "regular", tone="ok")
    f.box(54, 110, 240, 70, "n8n start (main)", "API · 推送 · 触发器 · 执行", tone="ok")
    f.box(54, 230, 110, 50, "SQLite / PG", tone="neutral", size=12)
    f.box(184, 230, 110, 50, "Task Runner", "Code 节点", tone="muted", size=12)
    f.arrow([(110, 180), (110, 230)], "读写")
    f.arrow([(240, 180), (240, 230)], "代码")
    f.text(174, 320, "一个进程做所有事", size=12, color=MUTED)
    # queue
    f.group(350, 76, 526, 300, "queue", tone="accent")
    f.box(380, 106, 150, 56, "main ×N", "API · 推送 · 手动执行", tone="accent", size=12)
    f.box(380, 196, 150, 56, "webhook ×N", "生产 Webhook", tone="accent", size=12)
    f.box(590, 150, 110, 56, "Redis", "Bull 队列", tone="warn", size=12)
    f.box(740, 106, 110, 56, "worker", "执行", tone="teal", size=12)
    f.box(740, 196, 110, 56, "worker", "执行", tone="teal", size=12)
    f.box(560, 296, 170, 50, "Postgres", "工作流 · 执行数据", tone="neutral", size=12)
    f.arrow([(530, 134), (590, 170)], "入队 ID", label_dy=-4)
    f.arrow([(530, 224), (590, 190)])
    f.arrow([(700, 170), (740, 134)])
    f.arrow([(700, 186), (740, 224)])
    f.arrow([(795, 252), (795, 321), (730, 321)], "写结果", tone="teal", label_at=0.4)
    f.arrow([(455, 252), (455, 321), (560, 321)], "读写", label_at=0.6)
    f.arrow([(740, 120), (640, 96), (530, 120)], "进度 pub/sub", tone="purple", dashed=True, label_at=0.5, label_dy=-6)
    return f


def fig_trace() -> Fig:
    f = Fig(940, 560, "一次手动执行：前端 POST /run，控制器只执行数据库中的版本，Runner 登记执行并构建钩子，引擎循环执行节点，钩子把进度推送回前端并在结束时写库。")
    f.title("一次手动执行的完整链路", "实线：调用；虚线：推送/回调")
    lane_x = [30, 250, 480, 720]
    lanes = ["编辑器 (Vue)", "cli: HTTP 层", "cli: 执行层", "core: 引擎"]
    tones = ["purple", "accent", "accent", "teal"]
    for x, name, tone in zip(lane_x, lanes, tones):
        f.box(x, 72, 190, 34, name, tone=tone, size=12)
        f.line(x + 95, 106, x + 95, 540, dashed=True)

    def step(n, x, y, label, sub=None, tone="neutral", w=190, h=44):
        f.box(x, y, w, h, label, sub, tone=tone, size=11)
        f.circle(x - 2, y + 4, 10, tone="dark", label=str(n), size=10)

    step(1, 30, 124, "runEntireWorkflow()", "useRunWorkflow.ts")
    step(2, 250, 124, "runManually()", "POST /workflows/:id/run")
    step(3, 480, 124, "executeManually()", "部分 / 触发器 / 自动")
    step(4, 480, 194, "WorkflowRunner.run()", "activeExecutions.add → DB")
    step(5, 480, 264, "runMainProcess()", "Workflow + 钩子 + 超时")
    step(6, 720, 264, "WorkflowExecute.run()", "栈中放入起始节点")
    step(7, 720, 334, "主循环：弹栈→runNode", "→ 子节点压栈")
    step(8, 480, 404, "hookFunctionsPush", "nodeExecuteAfter(+Data)")
    step(9, 30, 404, "handlers/nodeExecuteAfter", "画布变绿 · 显示 item 数")
    f.box(480, 474, 190, 44, "hookFunctionsSave", "结束时写入执行记录", tone="neutral", size=11)

    f.arrow([(220, 146), (250, 146)])
    f.arrow([(440, 146), (480, 146)])
    f.text(400, 118, "只执行 DB 中的版本", size=10, color=MUTED)
    f.arrow([(575, 168), (575, 194)])
    f.arrow([(575, 238), (575, 264)])
    f.arrow([(670, 286), (720, 286)])
    f.arrow([(815, 308), (815, 334)])
    f.arrow([(815, 378), (815, 426), (670, 426)], "钩子", tone="teal", dashed=True, label_at=0.3)
    f.arrow([(480, 426), (220, 426)], "WebSocket push", tone="purple", dashed=True)
    f.arrow([(815, 378), (815, 496), (670, 496)], "workflowExecuteAfter", tone="teal", dashed=True, label_at=0.75)
    f.arrow([(345, 168), (345, 210), (220, 210), (125, 210), (125, 404)], "{ executionId }", tone="muted", dashed=True, label_at=0.45)
    return f


FIGS = {
    "fig-01-spectrum": fig_spectrum,
    "fig-02-packages": fig_packages,
    "fig-02-topology": fig_topology,
    "fig-03-trace": fig_trace,
}
