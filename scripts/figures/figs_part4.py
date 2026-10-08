"""Part IV figures: partial execution."""

from svg import MUTED, Fig


def fig_partial() -> Fig:
    f = Fig(940, 360, "部分执行：只改了 VIP。子图是 Start 到 VIP 的路径；从触发器往前走遇到的第一个脏节点 VIP 是起始节点，输入取自 Big order? 上次的输出；Orders 不重跑。")
    f.title("部分执行：只重跑脏节点", "用户修改了 VIP，点了 VIP 的 Execute step")
    xs = {"Start": 30, "Orders": 190, "Big order?": 350, "VIP": 530, "Normal": 530, "Merge": 710}
    ys = {"Start": 150, "Orders": 150, "Big order?": 150, "VIP": 90, "Normal": 220, "Merge": 150}
    tone = {"Start": "muted", "Orders": "muted", "Big order?": "muted", "VIP": "warn", "Normal": "neutral", "Merge": "neutral"}
    sub = {"Start": "复用", "Orders": "复用（慢 API）", "Big order?": "复用", "VIP": "起始节点（脏）", "Normal": "子图外", "Merge": "子图外"}
    for name in xs:
        f.box(xs[name], ys[name], 140, 52, name, sub[name], tone=tone[name], size=12)
    f.arrow([(170, 176), (190, 176)], tone="muted")
    f.arrow([(330, 176), (350, 176)], tone="muted")
    f.arrow([(490, 166), (530, 116)], tone="accent")
    f.text(400, 120, "输入 = 上次的 true 输出", size=11, color="#2563eb")
    f.arrow([(490, 186), (530, 246)], tone="muted")
    f.arrow([(670, 116), (710, 166)], tone="muted")
    f.arrow([(670, 246), (710, 186)], tone="muted")
    f.group(20, 70, 670, 150, "子图（Start → VIP）", tone="accent")
    f.text(30, 300, "① 找触发器 Start   ② 子图 = VIP 及其祖先   ③ 从 Start 往前走，第一个脏节点 = VIP", size=12, anchor="start", color=MUTED)
    f.text(30, 324, "④ 清理 VIP 及下游的旧数据   ⑤ VIP 入栈，输入 = Big order? 上次 true 输出   ⑥ 主循环执行", size=12, anchor="start", color=MUTED)
    return f


FIGS = {"fig-15-partial": fig_partial}
