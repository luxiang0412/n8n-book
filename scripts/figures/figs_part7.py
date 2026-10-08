"""Part VII figures: sub-workflow waiting, queue mode, task runner, auth, deployment."""

from svg import MUTED, Fig


def fig_subworkflow() -> Fig:
    f = Fig(980, 400, "子工作流等待：父执行的 Execute Workflow 启动子执行；子执行进入等待后，父执行也以 WAIT_FOR_SUB_EXECUTION 停下并记下子执行 ID；WaitTracker 到期恢复子执行，子执行结束时把输出写进父执行栈顶条目的输入，再恢复父执行，节点以禁用状态把它传下去。")
    f.title("父执行等子执行：两段执行，一次补丁", "两段执行之间的状态都在数据库里")
    lanes = [("父执行", 110), ("子执行", 200), ("WaitTracker", 290), ("数据库", 360)]
    for name, y in lanes:
        f.text(20, y + 4, name, size=12, anchor="start", weight="600")
        f.line(120, y, 960, y, dashed=True)
    f.box(130, 94, 150, 32, "Execute Workflow", tone="accent", size=11)
    f.arrow([(205, 126), (205, 184)], "启动", tone="accent", label_dx=22)
    f.box(150, 184, 150, 32, "Wait 3600 s → 等待", tone="warn", size=11)
    f.arrow([(300, 200), (330, 126)], "waitTill", tone="warn", label_dx=-6)
    f.box(320, 94, 230, 32, "也等待：WAIT_FOR_SUB_EXECUTION", tone="warn", size=11)
    f.box(320, 344, 230, 32, "metadata.waitingChildExecutionIds", tone="muted", size=11, mono=True)
    f.arrow([(435, 126), (435, 344)], tone="muted", dashed=True)
    f.box(580, 274, 150, 32, "到期：认领并恢复", tone="purple", size=11)
    f.arrow([(655, 274), (655, 216)], tone="purple")
    f.box(590, 184, 140, 32, "跑完：Done", tone="ok", size=11)
    f.arrow([(730, 200), (760, 360)], "补丁：输出 → 父的输入", tone="teal", label_dx=70, label_dy=10)
    f.box(750, 344, 200, 32, "栈顶 data.main = 子输出", tone="muted", size=11)
    f.arrow([(850, 344), (850, 126)], "恢复父执行", tone="teal", label_dx=46)
    f.box(770, 94, 180, 32, "节点禁用 → 传出子输出", tone="ok", size=11)
    f.text(490, 392, "子执行失败时写入 metadata.resumeError：父执行的这个节点直接报错", size=11, color=MUTED)
    return f


def fig_queue() -> Fig:
    f = Fig(980, 400, "队列模式：main 接收 Webhook，把执行数据写入数据库，只把执行 ID 放进 Redis 队列；worker 用 BLMOVE 取任务，从数据库读数据、运行、写回结果，通过 pub/sub 把 Webhook 响应、流式块和 job-finished 发回 main；main 再回复 HTTP 请求。")
    f.title("队列模式：main 接活，worker 干活", "队列里只有 ID；数据在共享的数据库里")
    f.box(20, 170, 120, 60, "HTTP 客户端", "Webhook 调用", tone="neutral", size=12)
    f.box(200, 150, 190, 100, "main", "编辑器 · API · Webhook\n触发器 · WaitTracker\n手动执行在这里跑", tone="accent", size=12)
    f.box(470, 80, 170, 70, "Redis", "list: mini-n8n:jobs\nchannel: job-messages", tone="warn", size=11, mono=False)
    f.box(470, 280, 170, 60, "数据库", "执行数据 · 结果", tone="muted", size=12)
    f.box(720, 90, 200, 70, "worker A", "concurrency 5\nTask Runner 子进程", tone="teal", size=11)
    f.box(720, 200, 200, 70, "worker B", "concurrency 5\nTask Runner 子进程", tone="teal", size=11)
    f.arrow([(140, 200), (200, 200)], "请求")
    f.arrow([(390, 170), (470, 115)], "① LPUSH {executionId}", tone="warn", label_dx=-10)
    f.arrow([(390, 230), (470, 300)], "② 先写执行数据", tone="muted", label_dx=-20, label_dy=14)
    f.arrow([(640, 105), (720, 115)], "③ BLMOVE", tone="warn")
    f.arrow([(640, 130), (720, 225)], tone="warn")
    f.arrow([(760, 270), (640, 310)], "④ 读数据 / 写结果", tone="muted", label_dx=10, label_dy=16)
    f.arrow([(720, 150), (680, 190), (390, 190)], "⑤ respond / chunk / job-finished", tone="purple", label_at=0.62, label_dy=16)
    f.arrow([(200, 215), (140, 215)], "⑥ 回复", tone="ok", label_dy=16)
    f.text(490, 385, "SQLite 只适合单机（共享卷 + busy_timeout）；n8n 在队列模式下建议 PostgreSQL", size=11, color=MUTED)
    return f


def fig_runner() -> Fig:
    f = Fig(980, 360, "Task Runner：Code 节点不再在主进程里运行代码，而是把代码和数据交给一个子进程；子进程以禁止从字符串生成代码、只带白名单环境变量的方式启动；任务超时、死循环或内存耗尽时，主进程杀掉并重启 runner，自身不受影响。")
    f.title("Task Runner：把不可信代码关进另一个进程", "隔离靠进程，不靠 node:vm")
    f.group(20, 70, 430, 250, "主进程（main 或 worker）", tone="accent")
    f.box(40, 110, 180, 60, "Code 节点", "startJob('javascript')", tone="accent", size=12)
    f.box(250, 110, 180, 60, "TaskRunnerProcess", "计时 · 重启 · 分派", tone="neutral", size=12)
    f.box(40, 200, 390, 90, "进程里有的东西", "加密密钥 · 数据库连接 · 凭证 · 其他执行\n——代码一个也碰不到", tone="muted", size=11)
    f.arrow([(220, 140), (250, 140)])
    f.group(530, 70, 430, 250, "runner 子进程（fork + IPC）", tone="teal")
    f.box(550, 104, 390, 72, "node 启动参数", "--disallow-code-generation-from-strings\n--disable-proto=delete", tone="teal", size=11, mono=True)
    f.box(550, 190, 180, 50, "env 白名单", "PATH · HOME · TZ", tone="ok", size=11)
    f.box(760, 190, 180, 50, "vm 上下文", "$input · $json · $(...)", tone="ok", size=11)
    f.box(550, 255, 390, 45, "死循环 / 挂起 / 内存耗尽 → 进程退出或被杀", tone="warn", size=11)
    f.arrow([(430, 130), (550, 130)], "broker:task（代码 + 数据）", tone="teal", label_dy=-8)
    f.arrow([(550, 155), (430, 155)], "runner:taskdone / taskerror", tone="ok", label_dy=16)
    f.arrow([(745, 300), (745, 336), (340, 336), (340, 170)], "超时：SIGKILL，下一个任务启动新进程", tone="warn", label_at=0.5, label_dy=-6)
    return f


def fig_auth() -> Fig:
    f = Fig(980, 380, "两条认证路径：编辑器请求带 httpOnly cookie，JWT 验签、检查用户的密码哈希片段；公开 API 带 X-N8N-API-KEY，按哈希查找 key 并检查 scope。两条路径都得到一个用户，再按全局角色和共享表判断能否访问某个工作流或凭证。")
    f.title("谁在请求？能碰什么？", "认证得到用户；授权查角色和共享表")
    f.box(20, 90, 180, 60, "编辑器 /rest/*", "Cookie: mini-n8n-auth", tone="accent", size=12)
    f.box(20, 230, 180, 60, "脚本 /api/v1/*", "X-N8N-API-KEY", tone="purple", size=12)
    f.box(260, 80, 230, 80, "JWT 验签 + 未过期", "payload.hash == sha256(email:密码哈希)\n改密码 → 旧会话失效", tone="neutral", size=11)
    f.box(260, 220, 230, 80, "sha256(key) 查表", "key 的 scopes\n如 workflow:read", tone="neutral", size=11)
    f.box(560, 150, 150, 60, "用户", "global:owner\nglobal:member", tone="ok", size=11)
    f.box(770, 70, 190, 70, "工作流", "owner 全可见\nshared_workflow:\nworkflow:owner / editor", tone="teal", size=10)
    f.box(770, 160, 190, 60, "凭证", "shared_credentials:\ncredential:owner / user", tone="teal", size=10)
    f.box(770, 240, 190, 60, "保存工作流时", "用到的凭证必须可用", tone="warn", size=11)
    f.arrow([(200, 120), (260, 120)])
    f.arrow([(200, 260), (260, 260)])
    f.arrow([(490, 120), (560, 170)])
    f.arrow([(490, 260), (560, 190)])
    f.arrow([(710, 170), (770, 105)])
    f.arrow([(710, 180), (770, 190)])
    f.arrow([(710, 195), (770, 265)])
    f.text(490, 340, "API key 的权限 = key 的 scopes ∩ 它所属用户能访问的资源", size=12, weight="600")
    f.text(490, 364, "看不到的工作流返回 404（不暴露它存在）；能看到但不能做的操作返回 403", size=11, color=MUTED)
    return f


def fig_deploy() -> Fig:
    f = Fig(980, 380, "Docker Compose 部署：Redis、一个 main（端口 5678，提供 /healthz、/healthz/readiness、/metrics）和两个 worker（端口 5680 提供健康检查和指标）共享一个数据卷与同一个加密密钥；docker stop 时 tini 转发 SIGTERM，进程停止接活并等待正在运行的执行。")
    f.title("一键部署：一个镜像，两种角色", "docker compose up -d --build")
    f.box(40, 160, 150, 70, "用户 / 浏览器", ":5678", tone="neutral", size=12)
    f.box(260, 130, 210, 130, "main", "command: start\n/healthz · /healthz/readiness\n/metrics", tone="accent", size=11)
    f.box(560, 60, 160, 60, "redis:7-alpine", "healthcheck: ping", tone="warn", size=11)
    f.box(560, 160, 160, 60, "worker × 2", "command: worker\n:5680 health · metrics", tone="teal", size=11)
    f.box(560, 270, 160, 60, "volume: data", "database.sqlite", tone="muted", size=11)
    f.box(790, 60, 170, 110, "环境变量（共享）", "ENCRYPTION_KEY\nEXECUTIONS_MODE=queue\nREDIS_URL\nMETRICS=true", tone="purple", size=10)
    f.box(790, 200, 170, 130, "docker stop", "tini → SIGTERM\nreadiness → 503\n停止触发器\n等运行中的执行 ≤ 30 s\nstop_grace_period 40 s", tone="ok", size=10)
    f.arrow([(190, 195), (260, 195)])
    f.arrow([(470, 160), (560, 95)])
    f.arrow([(470, 195), (560, 190)])
    f.arrow([(470, 230), (560, 295)])
    f.arrow([(640, 160), (640, 120)], tone="warn")
    f.arrow([(640, 220), (640, 270)], tone="muted")
    f.text(490, 365, "depends_on: worker 等 main 健康（main 先建表），main 等 redis 健康", size=11, color=MUTED)
    return f


FIGS = {
    "fig-24-subworkflow": fig_subworkflow,
    "fig-25-queue": fig_queue,
    "fig-26-runner": fig_runner,
    "fig-27-auth": fig_auth,
    "fig-28-deploy": fig_deploy,
}
