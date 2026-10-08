"""Part III figures: persistence, hooks/push, credentials, triggers, lab 2."""

from svg import MUTED, Fig


def fig_tables() -> Fig:
    f = Fig(920, 380, "核心表：workflow_entity 保存定义；执行拆成小而常查的 execution_entity 和大而少读的 execution_data；credentials_entity 存密文；webhook_entity 是生产路由表。")
    f.title("核心表与关系", "表名与 n8n 相同（packages/@n8n/db/src/entities/）")

    def table(x, y, w, name, cols, tone):
        f.box(x, y, w, 30, name, tone=tone, size=12, mono=True)
        f.rect(x, y + 30, w, 18 * len(cols) + 10, fill="#ffffff", stroke="#cbd5e1", rx=4)
        for i, c in enumerate(cols):
            f.text(x + 10, y + 50 + i * 18, c, size=11, anchor="start", mono=True, color=MUTED if c.startswith("·") else "#1f2937")

    table(30, 80, 230, "workflow_entity", ["id (PK)", "name, active", "nodes, connections", "settings, pinData", "staticData, versionId"], "accent")
    table(330, 80, 250, "execution_entity", ["id (PK, 自增)", "workflowId", "mode, status, finished", "startedAt, stoppedAt", "waitTill  ← 索引"], "teal")
    table(330, 250, 250, "execution_data", ["executionId (PK, FK)", "workflowData  ← 快照", "data  ← IRunExecutionData"], "warn")
    table(650, 80, 240, "credentials_entity", ["id (PK)", "name, type", "data  ← 密文 v1:..."], "purple")
    table(650, 230, 240, "webhook_entity", ["(webhookPath, method) PK", "workflowId", "node"], "neutral")
    f.arrow([(260, 130), (330, 130)], "1 : N", label_dy=-8)
    f.arrow([(455, 202), (455, 250)], "1 : 1", label_dx=26, label_dy=4)
    f.arrow([(650, 280), (600, 280), (600, 60), (145, 60), (145, 80)], "属于", tone="muted", label_at=0.55)
    f.text(455, 360, "列表页只查 execution_entity；打开详情才 join execution_data", size=12, color=MUTED)
    return f


def fig_hooks() -> Fig:
    f = Fig(920, 360, "引擎只调用钩子；不同场景挂不同的处理函数组：regular main 保存并推送，worker 保存并经 Redis 转发，CLI 打印。")
    f.title("钩子把引擎与外部世界解耦", "WorkflowExecute 只认识 ExecutionLifecycleHooks")
    f.box(40, 140, 200, 80, "WorkflowExecute", "workflowExecuteBefore/After\nnodeExecuteBefore/After\nsendResponse · sendChunk", tone="teal", size=12)
    f.box(320, 150, 160, 60, "ExecutionLifecycleHooks", "handlers[] · 串行 await", tone="accent", size=11)
    f.arrow([(240, 180), (320, 180)], "runHook")
    rows = [
        (80, "regular main", "Save + Push + Statistics", "ok"),
        (160, "scaling worker", "Save + Push(→Redis 转发)", "warn"),
        (240, "CLI / 测试", "打印 / 断言", "neutral"),
    ]
    for y, name, sub, tone in rows:
        f.box(560, y, 200, 56, name, sub, tone=tone, size=12)
        f.arrow([(480, 180), (560, y + 28)], tone="muted")
    f.box(800, 80, 100, 56, "DB", "execution_*", tone="neutral", size=12)
    f.box(800, 160, 100, 56, "浏览器", "按 pushRef", tone="purple", size=12)
    f.arrow([(760, 100), (800, 106)])
    f.arrow([(760, 118), (800, 180)], tone="purple", dashed=True)
    f.arrow([(760, 188), (800, 196)], tone="purple", dashed=True)
    f.text(460, 330, "新增一个关注点 = 再挂一组处理函数，引擎代码不变", size=12, weight="600")
    return f


def fig_credentials() -> Fig:
    f = Fig(940, 340, "凭证路径：保存时加密，读取时把密码替换为占位符，执行时服务端解密并按凭证类型的 authenticate 规则改写请求；节点只声明凭证类型。")
    f.title("凭证：从填写到注入", "节点永远不拼认证头")
    f.box(20, 90, 150, 60, "编辑器表单", "name / value(password)", tone="purple", size=12)
    f.box(230, 90, 170, 60, "Cipher.encrypt", "AES-256-GCM · v1:iv:tag:data", tone="warn", size=11)
    f.box(460, 90, 170, 60, "credentials_entity", "data = 密文", tone="neutral", size=12, mono=True)
    f.arrow([(170, 120), (230, 120)], "POST")
    f.arrow([(400, 120), (460, 120)])
    f.box(700, 90, 220, 60, "GET 返回给编辑器", "value = __BLANK_VALUE__", tone="muted", size=11)
    f.arrow([(630, 120), (700, 120)], "redact")
    # execution path
    f.box(20, 220, 170, 70, "HTTP Request 节点", "httpRequestWithAuthentication\n('httpHeaderAuth', opts)", tone="teal", size=11)
    f.box(250, 220, 190, 70, "CredentialsHelper", "getDecrypted()\nauthenticate()", tone="accent", size=12)
    f.box(500, 220, 200, 70, "authenticate 规则", "headers: {\n'={{$credentials.name}}': ... }", tone="neutral", size=11, mono=True)
    f.box(760, 220, 160, 70, "发出的请求", "x-api-key: s3cret", tone="ok", size=12, mono=True)
    f.arrow([(190, 255), (250, 255)])
    f.arrow([(545, 150), (545, 185), (345, 185), (345, 220)], "解密", tone="warn", label_at=0.5)
    f.arrow([(440, 255), (500, 255)])
    f.arrow([(700, 255), (760, 255)])
    f.text(470, 320, "执行记录里只有凭证引用 { id, name }，没有密钥", size=12, color=MUTED)
    return f


def fig_activation() -> Fig:
    f = Fig(920, 330, "激活：Webhook 节点写入 webhook_entity；trigger 节点的 trigger() 被调用并注册 cron；之后每次请求或 emit 启动一次新执行。")
    f.title("激活一个工作流", "ActiveWorkflowManager.add()")
    f.box(30, 130, 180, 70, "ActiveWorkflowManager", "add(workflowId)", tone="accent", size=12)
    f.box(290, 70, 200, 56, "Webhook 节点", "description.webhooks", tone="neutral", size=12)
    f.box(290, 200, 200, 56, "Schedule Trigger", "trigger()", tone="neutral", size=12)
    f.box(560, 70, 170, 56, "webhook_entity", "(orders, POST)", tone="warn", size=12, mono=True)
    f.box(560, 200, 170, 56, "ScheduledTaskManager", "cron */2 * * * * *", tone="warn", size=11)
    f.box(780, 130, 130, 70, "新执行", "triggerToStartFrom", tone="ok", size=12)
    f.arrow([(210, 150), (290, 98)])
    f.arrow([(210, 180), (290, 228)])
    f.arrow([(490, 98), (560, 98)], "insert")
    f.arrow([(490, 228), (560, 228)], "registerCron")
    f.arrow([(730, 98), (780, 150)], "请求", tone="ok")
    f.arrow([(730, 228), (780, 182)], "emit", tone="ok")
    f.text(460, 300, "停用 = 删路由 + 注销 cron + closeFunction()", size=12, color=MUTED)
    return f


def fig_response_modes() -> Fig:
    f = Fig(940, 330, "三种响应模式：onReceived 在执行开始时回复；lastNode 等执行结束用最后节点的数据回复；responseNode 在执行中途由 Respond to Webhook 节点回复。")
    f.title("Webhook 的三种响应模式", "时间从左到右；橙色竖线是 HTTP 响应发出的时刻")
    rows = [(90, "onReceived"), (170, "lastNode"), (250, "responseNode")]
    for y, name in rows:
        f.text(30, y + 22, name, size=12, anchor="start", weight="700", mono=True)
        f.box(150, y, 110, 34, "Webhook", tone="neutral", size=11)
        f.box(290, y, 110, 34, "Set", tone="neutral", size=11)
        if name == "responseNode":
            f.box(430, y, 150, 34, "Respond to Webhook", tone="accent", size=11)
            f.box(610, y, 110, 34, "Slack", tone="neutral", size=11)
        else:
            f.box(430, y, 110, 34, "HTTP Request", tone="neutral", size=11)
        f.arrow([(260, y + 17), (290, y + 17)], tone="muted")
        f.arrow([(400, y + 17), (430, y + 17)], tone="muted")
        if name == "responseNode":
            f.arrow([(580, y + 17), (610, y + 17)], tone="muted")
    # response markers
    for x, y, label in [(272, 90, "200 {message: started}"), (560, 170, "200 最后节点的 json"), (596, 250, "sendResponse 钩子")]:
        f.line(x, y - 8, x, y + 42, color="#d97706", sw=3)
        f.text(x + 6, y - 12, label, size=11, anchor="start", color="#78350f")
    f.text(470, 312, "responseNode：回复之后，后面的节点照常运行", size=12, color=MUTED)
    return f


def fig_lab2() -> Fig:
    f = Fig(940, 360, "v0.2 服务端：路由交给执行服务，执行服务决定立即执行还是等待测试 Webhook，Runner 登记执行、组装钩子、启动引擎；ActiveWorkflowManager 管理激活后的路由和 cron。")
    f.title("Lab 2：mini-n8n v0.2 服务端", "packages/cli/src")
    f.box(20, 90, 160, 210, "Fastify 路由", "/rest/workflows\n/rest/executions\n/rest/credentials\n/rest/push (SSE)\n/webhook/*\n/webhook-test/*", tone="purple", size=12)
    f.box(240, 90, 200, 56, "WorkflowExecutionService", "executeManually / runWorkflow", tone="accent", size=11)
    f.box(240, 170, 200, 56, "TestWebhooks / LiveWebhooks", "executeWebhook", tone="accent", size=11)
    f.box(240, 250, 200, 56, "ActiveWorkflowManager", "Webhook 路由 · cron", tone="accent", size=11)
    f.box(500, 130, 180, 56, "WorkflowRunner", "登记 · 钩子 · 启动", tone="teal", size=12)
    f.box(740, 90, 170, 56, "WorkflowExecute", "v0.1 引擎", tone="teal", size=12)
    f.box(740, 180, 170, 56, "hooks: Save + Push", tone="neutral", size=12)
    f.box(740, 270, 170, 56, "SQLite", "node:sqlite", tone="neutral", size=12)
    f.arrow([(180, 118), (240, 118)])
    f.arrow([(180, 198), (240, 198)])
    f.arrow([(180, 278), (240, 278)])
    f.arrow([(440, 118), (500, 150)])
    f.arrow([(440, 198), (500, 168)])
    f.arrow([(440, 278), (590, 278), (590, 186)], "emit", tone="ok", label_at=0.3)
    f.arrow([(680, 150), (740, 118)])
    f.arrow([(825, 146), (825, 180)])
    f.arrow([(825, 236), (825, 270)])
    return f


FIGS = {
    "fig-09-tables": fig_tables,
    "fig-10-hooks": fig_hooks,
    "fig-11-credentials": fig_credentials,
    "fig-12-activation": fig_activation,
    "fig-12-response-modes": fig_response_modes,
    "fig-lab2-server": fig_lab2,
}
