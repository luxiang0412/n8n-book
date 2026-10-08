"""Part II figures: data model, node types, expressions, engine, robustness, lab 1."""

from svg import MUTED, Fig


def fig_model() -> Fig:
    f = Fig(940, 430, "工作流 JSON 由 nodes 和按源节点索引的 connections 组成；Workflow 构造时生成反向索引；节点输出是 输出×item 的二维数组，item 用 pairedItem 记录来源。")
    f.title("数据模型：节点、连接与 items", "保存的 JSON → 运行时的两种索引 → If 节点的一次输出")
    # JSON
    f.group(20, 70, 280, 340, "工作流 JSON（保存）", tone="neutral")
    f.lines(36, 102, [
        '{ "nodes": [',
        '   { "name": "Orders", ... },',
        '   { "name": "Big order?",',
        '     "type": "n8n-nodes-base.if",',
        '     "position": [440, 0],',
        '     "parameters": {...} }, ...],',
        '  "connections": {',
        '   "Big order?": { "main": [',
        '     [{node:"VIP", index:0}],',
        '     [{node:"Normal",index:0}]',
        '   ]}, ... } }',
    ] and [r.replace("  ", "\u00a0\u00a0") for r in [
        '{ "nodes": [',
        '   { "name": "Orders", ... },',
        '   { "name": "Big order?",',
        '     "type": "n8n-nodes-base.if",',
        '     "position": [440, 0],',
        '     "parameters": {...} }, ...],',
        '  "connections": {',
        '   "Big order?": { "main": [',
        '     [{node:"VIP", index:0}],',
        '     [{node:"Normal",index:0}]',
        '   ]}, ... } }',
    ]], size=11, anchor="start", mono=True, gap=26)
    # indexes
    f.group(320, 70, 280, 340, "两种索引（运行时）", tone="accent")
    f.box(340, 104, 240, 60, "connectionsBySourceNode", "源 → 类型 → 输出号 → [目标]", tone="accent", size=12)
    f.box(340, 214, 240, 60, "connectionsByDestinationNode", "目标 → 类型 → 输入号 → [源]", tone="purple", size=12)
    f.arrow([(460, 164), (460, 214)], "mapConnectionsByDestination", tone="purple", label_dy=4, size=10)
    f.text(460, 310, "正向：执行时找下游（O(1)）", size=11, color=MUTED)
    f.text(460, 332, "反向：找 Merge 的输入、找祖先", size=11, color=MUTED)
    f.text(460, 354, "type: main / ai_tool / ai_languageModel…", size=11, color=MUTED)
    # items matrix
    f.group(620, 70, 300, 340, "If 节点的输出 INodeExecutionData[][]", tone="ok")
    f.text(640, 108, "输出 0（true）", size=12, anchor="start", weight="600")
    f.box(640, 118, 260, 40, '{ json: Ada 120 }', "pairedItem: { item: 0 }", tone="ok", size=11, mono=True)
    f.box(640, 166, 260, 40, '{ json: Grace 560 }', "pairedItem: { item: 2 }", tone="ok", size=11, mono=True)
    f.text(640, 236, "输出 1（false）", size=12, anchor="start", weight="600")
    f.box(640, 246, 260, 40, '{ json: Linus 35 }', "pairedItem: { item: 1 }", tone="warn", size=11, mono=True)
    f.text(770, 320, "空输出 → 下游节点不执行", size=11, color=MUTED)
    f.text(770, 342, "pairedItem.item = 输入里的下标", size=11, color=MUTED)
    return f


def fig_description() -> Fig:
    f = Fig(900, 360, "一份 INodeTypeDescription 同时被画布、参数面板、Workflow 构造函数和引擎使用。")
    f.title("description 驱动一切", "节点类型 = 声明式描述 + 行为方法")
    f.box(330, 140, 240, 110, "INodeTypeDescription", "name · version · defaults\ninputs / outputs\nproperties · displayOptions\nrequiredInputs", tone="accent")
    f.box(40, 80, 210, 56, "画布", "按 inputs/outputs 画端口", tone="purple", size=12)
    f.box(40, 250, 210, 56, "参数面板 (NDV)", "按 properties 渲染表单", tone="purple", size=12)
    f.box(650, 80, 210, 56, "Workflow 构造", "getNodeParameters 填默认值", tone="ok", size=12)
    f.box(650, 250, 210, 56, "引擎", "requiredInputs · 输出数", tone="teal", size=12)
    f.arrow([(330, 170), (250, 108)])
    f.arrow([(330, 220), (250, 278)], "displayParameter", label_at=0.35, label_dy=-8)
    f.arrow([(570, 170), (650, 108)])
    f.arrow([(570, 220), (650, 278)])
    f.text(450, 300, "execute() / supplyData() / trigger() / webhook()", size=12, mono=True, color=MUTED)
    f.text(450, 322, "决定节点“是哪一种”", size=12, color=MUTED)
    return f


def fig_expression() -> Fig:
    f = Fig(940, 300, "表达式求值三阶段：拆分模板、AST 检查与改写、在只含数据代理变量的作用域中执行；单个代码块保留类型。")
    f.title("表达式求值的三个阶段", '"=Hi {{ $json.name }}, {{ $json[key] }}"')
    f.box(20, 100, 200, 90, "① 拆分", "文本: \"Hi \"\n代码: $json.name\n文本: \", \"\n代码: $json[key]", tone="neutral", size=12)
    f.box(270, 100, 240, 90, "② AST 检查 / 改写", "$x.constructor → 报错\n$json[key] →\n$json[__sanitize(key)]", tone="warn", size=12)
    f.box(560, 100, 200, 90, "③ 受限作用域执行", "只看得到 $json $input $()\nprocess / require → undefined", tone="accent", size=11)
    f.box(800, 100, 120, 90, "结果", "1 个代码块：原类型\n否则：拼字符串", tone="ok", size=11)
    f.arrow([(220, 145), (270, 145)])
    f.arrow([(510, 145), (560, 145)])
    f.arrow([(760, 145), (800, 145)])
    f.text(390, 230, "n8n：@n8n/tournament + PrototypeSanitizer 等钩子", size=11, color=MUTED)
    f.text(660, 230, "n8n 默认：isolated-vm 中执行", size=11, color=MUTED)
    f.text(390, 252, "mini-n8n：acorn + 同样的黑名单", size=11, color=MUTED)
    f.text(660, 252, "mini-n8n：with + Proxy 白名单", size=11, color=MUTED)
    return f


def fig_paired_item() -> Fig:
    f = Fig(940, 330, "$('Webhook').item 的回溯：从当前 item 出发，每一步用 item 的 pairedItem 和节点运行记录的 source，退回上一个节点的对应 item。")
    f.title("沿 pairedItem 回溯：$('Webhook').item", "在 Greet 节点处理 item 0 时求值")
    xs = [30, 250, 470, 690]
    names = ["Webhook", "Strip (Set)", "Filter (If)", "Greet"]
    items = [
        ["0 Ada", "1 Linus ←", "2 Grace"],
        ["0 {id:1}", "1 {id:2} p=1", "2 {id:3}"],
        ["true: 0 {id:2} p=1", "false: …", ""],
        ["当前 item 0", "", ""],
    ]
    for x, name, rows in zip(xs, names, items):
        f.box(x, 80, 200, 34, name, tone="accent" if name == "Greet" else "neutral", size=12)
        for i, r in enumerate(rows):
            if not r:
                continue
            tone = "ok" if ("←" in r or "p=1" in r or "当前" in r) else "muted"
            f.box(x, 126 + i * 44, 200, 34, r, tone=tone, size=11, mono=True, bold=False)
    f.arrow([(690, 143), (670, 143)], tone="ok")
    f.arrow([(690, 160), (600, 230), (480, 160)], "① source[0] = Filter 输出0", tone="ok", label_at=0.5, label_dy=16)
    f.arrow([(470, 143), (450, 187)], tone="ok")
    f.text(570, 284, "② Filter 的 item0：pairedItem.item=1，source → Strip", size=11, color=MUTED)
    f.arrow([(250, 187), (230, 187)], tone="ok")
    f.text(240, 264, "③ Strip 的 item1：pairedItem.item=1，source → Webhook", size=11, color=MUTED)
    f.text(130, 300, "结果：Webhook 输出 item 1（Linus）", size=12, weight="600")
    return f


def _stack_state(f: Fig, ox: int, title: str, ran: str, stack: list[str], waiting: str | None):
    f.text(ox, 92, title, size=12, anchor="start", weight="700")
    f.text(ox, 112, f"刚运行：{ran}", size=11, anchor="start", color=MUTED)
    f.rect(ox, 124, 190, 120, fill="#ffffff", stroke="#cbd5e1")
    f.text(ox + 8, 142, "执行栈（头在上）", size=10, anchor="start", color=MUTED)
    for i, s in enumerate(stack):
        f.box(ox + 20, 150 + i * 30, 150, 26, s, tone="accent", size=11)
    if not stack:
        f.text(ox + 95, 190, "（空）", size=11, color=MUTED)
    f.rect(ox, 256, 190, 70, fill="#ffffff", stroke="#cbd5e1")
    f.text(ox + 8, 274, "等待区", size=10, anchor="start", color=MUTED)
    if waiting:
        f.box(ox + 20, 282, 150, 32, waiting, tone="warn", size=11, mono=True)
    else:
        f.text(ox + 95, 304, "（空）", size=11, color=MUTED)


def fig_stack() -> Fig:
    f = Fig(940, 360, "并行分支汇入 Merge：Up 运行后 Merge 只有输入0，进入等待区；Down 运行后输入到齐，Merge 进栈。")
    f.title("执行栈与等待区（Start → Up / Down → Merge）", "每格是一个节点运行完、子节点已入栈之后的状态")
    _stack_state(f, 20, "① Start 之后", "Start", ["Up", "Down"], None)
    _stack_state(f, 250, "② Up 之后", "Up", ["Down"], "Merge[1, ·]")
    _stack_state(f, 480, "③ Down 之后", "Down", ["Merge"], None)
    _stack_state(f, 710, "④ Merge 之后", "Merge（2 个 item）", [], None)
    return f


def _tree(f: Fig, ox: int, oy: int, order: list[str], title: str):
    pos = {"Start": (0, 60), "A": (90, 20), "B": (90, 100), "A1": (180, 0), "A2": (180, 40), "B1": (180, 100)}
    edges = [("Start", "A"), ("Start", "B"), ("A", "A1"), ("A", "A2"), ("B", "B1")]
    f.text(ox, oy - 14, title, size=12, anchor="start", weight="700")
    for a, b in edges:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        f.arrow([(ox + x1 + 60, oy + y1 + 13), (ox + x2, oy + y2 + 13)], sw=1.2)
    for name, (x, y) in pos.items():
        n = order.index(name) + 1
        f.box(ox + x, oy + y, 60, 26, f"{n}·{name}", tone="accent" if name.startswith("A") else ("teal" if name.startswith("B") else "neutral"), size=11)


def fig_order() -> Fig:
    f = Fig(900, 260, "同一棵树：v1 深度优先，先跑完上方的 A 分支；v0 广度优先，先跑完同一层。")
    f.title("执行顺序：v1（默认）vs v0（legacy）", "格子里的数字是执行顺序")
    _tree(f, 40, 110, ["Start", "A", "A1", "A2", "B", "B1"], "v1：unshift + 上方优先（深度优先）")
    _tree(f, 500, 110, ["Start", "A", "B", "A1", "A2", "B1"], "v0：push（广度优先）")
    return f


def fig_error_modes() -> Fig:
    f = Fig(940, 340, "三种 onError：stopWorkflow 让执行失败；continueRegularOutput 把错误 item 混在正常输出里；continueErrorOutput 多出 Error 输出，错误 item 带回原始字段。")
    f.title("onError 的三种模式", "输入 3 个订单，第 2 个金额为负，节点逐条处理")
    cols = [(20, "stopWorkflow（默认）", "bad"), (330, "continueRegularOutput", "warn"), (640, "continueErrorOutput", "ok")]
    for x, name, tone in cols:
        f.box(x, 80, 280, 36, name, tone=tone, size=12)
        f.box(x, 140, 90, 70, "Validate", "#1 #2 #3", tone="neutral", size=12)
    # stop
    f.box(150, 150, 150, 50, "执行失败", "status: error", tone="bad", size=12)
    f.arrow([(110, 175), (150, 175)], tone="bad")
    f.text(160, 250, "下游都不执行", size=11, color=MUTED)
    # regular
    f.box(460, 140, 150, 70, "下游收到 3 个", "#1  {error}  #3", tone="warn", size=11)
    f.arrow([(420, 175), (460, 175)], tone="warn")
    f.text(470, 250, "错误 item 只有 error 字段", size=11, color=MUTED)
    # error output
    f.box(770, 130, 150, 40, "Success", "#1  #3", tone="ok", size=11)
    f.box(770, 190, 150, 40, "Error", "#2 + error", tone="bad", size=11)
    f.arrow([(730, 160), (770, 150)], "0", tone="ok")
    f.arrow([(730, 190), (770, 210)], "1", tone="bad")
    f.text(780, 260, "按 pairedItem 合并原始字段", size=11, color=MUTED)
    f.text(470, 310, "节点整体抛异常且设置了继续：引擎把输入原样传给输出 0", size=12, weight="600")
    return f


def fig_lab1() -> Fig:
    f = Fig(940, 300, "Lab 1 工作流：Issues 经 Loop Over Items 分批打分（循环），done 输出经 If 分流到两个 Set，再 Merge、Aggregate、Report。")
    f.title("Lab 1：工单分诊", "循环 + 分支 + 合并 + 表达式 + 跨节点引用")
    boxes = {
        "Start": (20, 120), "Issues": (130, 120), "Loop": (250, 120), "Score": (250, 220),
        "Urgent?": (380, 120), "Urgent": (500, 70), "Backlog": (500, 170), "Merge": (620, 120),
        "Aggregate": (730, 120), "Report": (840, 120),
    }
    tones = {"Loop": "purple", "Score": "purple", "Urgent?": "warn", "Merge": "teal"}
    for name, (x, y) in boxes.items():
        f.box(x, y, 84, 36, name, tone=tones.get(name, "neutral"), size=11)

    def a(p, q, label=None, tone="neutral", **kw):
        f.arrow([p, q], label, tone=tone, **kw)

    a((104, 138), (130, 138))
    a((214, 138), (250, 138))
    a((334, 138), (380, 138), "done", tone="ok", size=10)
    f.arrow([(292, 156), (292, 220)], "loop", tone="purple", size=10, label_dx=18, label_dy=4)
    f.arrow([(250, 238), (226, 238), (226, 150), (250, 150)], tone="purple", dashed=True)
    a((464, 130), (500, 88), "true", tone="ok", size=10)
    a((464, 146), (500, 188), "false", tone="warn", size=10)
    a((584, 88), (620, 130))
    a((584, 188), (620, 146))
    a((704, 138), (730, 138))
    a((814, 138), (840, 138))
    f.text(470, 280, "Score: {{ $json.comments * 2 + ($json.label === 'bug' ? 10 : 0) }}   Report: $('Issues').all().length", size=11, mono=True, color=MUTED)
    return f


FIGS = {
    "fig-04-model": fig_model,
    "fig-05-description": fig_description,
    "fig-06-expression": fig_expression,
    "fig-06-paired-item": fig_paired_item,
    "fig-07-stack": fig_stack,
    "fig-07-order": fig_order,
    "fig-08-error-modes": fig_error_modes,
    "fig-lab1-triage": fig_lab1,
}
