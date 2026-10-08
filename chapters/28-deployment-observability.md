# 第 28 章 部署与可观测

> 本章目标：读完你能把 mini-n8n 用 Docker Compose 部署成“Redis + 一个 main + 两个 worker”，并给它加上生产必需的三样东西：健康检查（存活 / 就绪）、Prometheus 指标和结构化日志；还要让它优雅关闭——`docker stop` 时先停止接活、等正在跑的执行做完，不丢数据。前置：第 24、25、27 章。对应代码：mini-n8n v1.0 的 `Dockerfile`、`docker-compose.yml`、`deploy/e2e.sh`、`cli/src/logger.ts`、`metrics.ts`、`executions-pruning.ts`

## 1. 问题与概念

前面各章已经把 mini-n8n 做成了能横向扩展的系统。要真正跑在生产上，还缺几块：

| 需要 | 为什么 |
|---|---|
| **容器镜像** | 部署的标准单位；一个镜像两种角色（main / worker），只换启动命令 |
| **健康检查** | 编排系统（Compose、Kubernetes）靠它决定“这个容器能不能收流量”、“要不要重启” |
| **指标** | 看清楚系统在干什么：执行了多少、多快、队列积压多少、内存多大 |
| **结构化日志** | 出了问题能检索；日志收集系统（Loki、ELK）要能解析 |
| **执行数据清理** | 每次 Webhook 都产生一条执行记录，不清理数据库会无限膨胀 |
| **优雅关闭** | 部署新版本时正在跑的执行不能被硬杀 |

![一键部署](./images/fig-28-deploy.svg)

*图 28-1：Redis、一个 main（:5678）和两个 worker（:5680 健康检查和指标）共享一个数据卷和同一个加密密钥；`docker stop` 时 tini 转发 SIGTERM，进程停止接活、等执行做完。*

两个健康检查要分清：

- **存活（liveness）** `/healthz`：进程还活着吗？一直返回 200。挂了就重启。
- **就绪（readiness）** `/healthz/readiness`：能收流量吗？启动完成、数据库可查才返回 200；关闭时先变成 503，让编排器把它从负载均衡里摘掉。

## 2. n8n 是怎么做的

### 2.1 镜像

n8n 的 `docker/images/n8n/Dockerfile` 是多阶段构建：一个阶段编译原生模块（`isolated-vm`、`sqlite3`），最终镜像基于精简的 base 镜像，`USER node`（不用 root），`EXPOSE 5678`，`ENTRYPOINT ["tini", "--", "/docker-entrypoint.sh"]`。**tini** 是关键：它当 PID 1，把 `docker stop` 发来的 SIGTERM 正确转发给 Node 进程（Node 直接当 PID 1 时对信号处理有坑）。

### 2.2 健康检查

```ts
// packages/cli/src/abstract-server.ts:149 setupHealthCheck（节选）
this.app.get(healthPath, ..., (_req, res) => res.send({ status: 'ok' }));   // liveness：不看数据库
this.app.get(readinessPath, ..., (_req, res) => {
	const { connected, migrated } = connectionState;
	if (connected && migrated && this.fullyReady) res.status(200).send({ status: 'ok' });
	else res.status(503).send(...);
});
```

`markAsReady()`（`:140`）在所有初始化完成后把 `fullyReady` 置真。

### 2.3 指标

开启 `N8N_METRICS=true` 后，`/metrics` 用 `prom-client` 暴露 Prometheus 指标，前缀 `n8n_`：执行时长直方图、活跃工作流数、队列里等待和处理中的任务数、缓存命中、事件总线……（`metrics/prometheus/*.ts`，二十多个服务，每个管一类指标）。比如队列指标（`queue-metrics.service.ts`）：

```text
n8n_scaling_mode_queue_jobs_waiting   队列里还没被领走的任务数
n8n_scaling_mode_queue_jobs_active    所有 worker 正在处理的任务数
```

### 2.4 清理

每隔一段时间删掉太旧或太多的已完成执行（`EXECUTIONS_DATA_MAX_AGE` 默认 336 小时，`EXECUTIONS_DATA_PRUNE_MAX_COUNT` 默认 10000）。n8n 分两步：先软删除，过了缓冲期再硬删除。

### 2.5 优雅关闭

收到 SIGTERM 后，n8n 在 `N8N_GRACEFUL_SHUTDOWN_TIMEOUT`（默认 30 秒）内：就绪检查转 503、停止接受新执行、等正在跑的执行结束，worker 做完手上的任务，然后退出。

## 3. 从零实现

### 3.1 结构化日志

`cli/src/logger.ts` 支持 text（给人看）和 json（给日志系统）两种格式，有级别过滤和 `child()`（给每行附加字段，比如 worker id）：

```ts
// :20
const line = this.format === 'json'
	? JSON.stringify({ time: ..., level, message, ...all })
	: `${new Date().toISOString()} ${level.padEnd(5)} ${message}${...}`;
```

`MINI_N8N_LOG_FORMAT=json` 切到 JSON。各处原来的 `console.log` 换成了 `logger.info(...)`，带上 `executionId`、`workerId` 等字段。

### 3.2 指标

`cli/src/metrics.ts` 不引库，直接拼 Prometheus 文本格式：执行计数（按状态和模式）、时长直方图、若干 gauge 和进程内存。gauge 用回调，由值的所有者注册：

```ts
// server.ts:174
ctx.metrics.gauge('active_workflow_count', '...', () => db.workflows.list().filter((w) => w.active).length);
if (ctx.queue) ctx.metrics.gauge('scaling_mode_queue_jobs_waiting', '...', () => ctx.queue!.waitingCount());
```

执行结束时 `WorkflowRunner` 记一笔 `metrics.executionFinished(status, mode, seconds)`。`/metrics` 仅在 `MINI_N8N_METRICS=true` 时注册。

### 3.3 就绪检查

```ts
// server.ts:165
app.get('/healthz/readiness', async (_req, reply) => {
	let dbOk = true;
	try { db.db.prepare('SELECT 1').get(); } catch { dbOk = false; }
	const ok = ctx.status.ready && dbOk;
	return reply.code(ok ? 200 : 503).send({ status: ok ? 'ok' : 'error' });
});
```

`ctx.status.ready` 在 `startCommand()` 里等 `app.listen()` 之后置真，关闭时先置假。

### 3.4 清理

`cli/src/executions-pruning.ts` 每小时调一次 `db.executions.pruneFinished()`（`databases/db.ts:304`）：

```sql
DELETE FROM execution_entity WHERE status NOT IN ('new', 'running', 'waiting')
  AND (stoppedAt < ? OR id NOT IN (SELECT id FROM execution_entity ORDER BY id DESC LIMIT ?))
```

删太旧的、或排在最新 N 条之外的，但绝不删 running / waiting 的。执行数据表有外键级联，一起删掉。

### 3.5 优雅关闭

main（`commands/start.ts:21`）：

```ts
const shutdown = async (signal: string) => {
	ctx.status.ready = false;                                             // 就绪检查转 503
	await ctx.activeWorkflowManager.removeAll();                          // 不再有触发器 / Webhook 执行
	const left = await ctx.activeExecutions.waitForAll(ctx.config.gracefulShutdownTimeout * 1000);
	if (left.length) ctx.logger.warn('Executions still running at shutdown', { executionIds: left });
	await app.close();
	process.exit(0);
};
process.once('SIGTERM', () => void shutdown('SIGTERM'));
```

`waitForAll()`（`active-executions.ts`）等所有在跑的执行结束，最多等 `gracefulShutdownTimeout` 秒。worker（`commands/worker.ts:36`）类似：就绪转 503，`queue.close()` 等手上的任务做完（第 25 章那个“空闲循环断开、忙循环做完”的 `close()`），再关 runner 和数据库。

### 3.6 镜像与 Compose

`Dockerfile` 一个镜像两种角色：

~~~~dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY . .
RUN npm ci && npm run build:editor          # tsx 直接跑 TS 源码，保留 devDependencies

FROM node:22-alpine
RUN apk add --no-cache tini                 # PID 1，转发 SIGTERM
WORKDIR /app
COPY --from=build /app /app
ENV MINI_N8N_HOST=0.0.0.0 MINI_N8N_USER_FOLDER=/home/node/.mini-n8n
USER node
EXPOSE 5678
ENTRYPOINT ["tini", "--", "node", "--import", "tsx", "packages/cli/src/bin.ts"]
CMD ["start"]                               # worker 用 command 覆盖成 worker
~~~~

`docker-compose.yml` 定义 redis、main 和两个 worker（`deploy: replicas: 2`）。要点：

- main 和 worker **共享加密密钥**（`MINI_N8N_ENCRYPTION_KEY`）和 **数据卷**（SQLite 文件）——第 25 章说过，worker 要解密凭证、要读执行数据。
- `depends_on` + `condition: service_healthy`：worker 等 main 健康（main 先建好表），main 等 redis 健康。
- `stop_grace_period: 40s`：比 `gracefulShutdownTimeout`（30 秒）长，给优雅关闭留出余量，否则 Docker 会提前 SIGKILL。
- 每个服务有 `healthcheck`，指向 `/healthz/readiness`。

单机上 SQLite + 共享卷够用；真正多机部署要把数据库换成 PostgreSQL（第 25 章的警告）。

## 4. 运行与验证

### 4.1 一键起

```bash
cp .env.example .env            # 设 MINI_N8N_ENCRYPTION_KEY
docker compose up -d --build
```

### 4.2 端到端脚本

`deploy/e2e.sh` 把整套部署当作一个黑盒，像用户一样用一遍再拆掉。真实输出：

```text
== build and start (port 5688)
✓ redis, main and 2 workers are healthy:  1 main  1 redis  2 worker
== owner and API key
✓ owner set up, API key created (…m0Xa)
== a workflow through the public API: Webhook -> Code (task runner on a worker)
✓ workflow wlBEQZfC8rnYLWoZ created and activated with the API key
== 30 concurrent webhook calls
✓ 30/30 responses correct (e.g. n=12 -> 144)
✓ public API lists 30 successful executions
== who did the work
✓ both workers ran jobs: 15 15
✓ main /metrics: active_workflow_count 1, scaling_mode_queue_jobs_waiting 0
✓ worker 1 /metrics: mini_n8n_worker_jobs_completed 15
== graceful shutdown: stop the workers while an execution waits 5 s
✓ docker compose stop took 4 s; the running execution finished: success
== restart: data and active workflows survive
✓ after restarting main and workers the webhook answers again (n=9 -> 81)
✓ the REST API still needs a session
```

这一个脚本把前五章串了起来：公开 API（27 章）建并激活工作流 → 30 个并发 Webhook 被两个 worker 平分、Code 节点在各自的 Task Runner 里跑（25、26 章）→ 指标反映实况 → `docker compose stop` 时一个等 5 秒的执行仍然跑完（本章优雅关闭）→ 重启后数据和激活状态都还在。

“both workers ran jobs: 15 15” 正是横向扩展的意义：30 个任务被两个 worker 平分。

### 4.3 踩坑记录

1. **三个容器同时开 SQLite**：见第 25 章踩坑 1（`busy_timeout`）。部署里还靠 `depends_on` 让 worker 等 main 先建表。
2. **公开 API 激活工作流返回 400**：`curl -X POST .../activate` 带 `content-type: application/json` 但没 body，Fastify 默认解析器拒绝空 body。根因和修复在第 27 章踩坑 1。这个坑正是 `deploy/e2e.sh` 跑出来的——本地单进程测试都带 body，没碰到。
3. **`curl -sf` 把错误响应吞了**。脚本第一版用 `curl -sf`，服务器返回 4xx 时 curl 直接失败、不打印响应体，报错是没头没尾的 `SyntaxError: Unexpected end of JSON input`。改成 `curl -s --fail-with-body` 才看到真正的错误信息，定位到上面那个空 body 问题。工具的失败模式也会藏住真正的 bug。

## 5. 练习

1. **巩固**：`docker compose up -d --build` 起来后，`curl localhost:5678/metrics` 看指标；在编辑器里激活一个工作流，再看 `active_workflow_count` 变了没有。`docker compose logs -f worker` 看 JSON 日志（把 compose 里的 `MINI_N8N_LOG_FORMAT` 改成 `json`）。
2. **扩展**：加一个 `mini_n8n_workflow_executions_total` 按 `workflowId` 分标签的计数，用它配一条告警规则思路：“某个工作流 5 分钟内失败率超过 50%”。
3. **读源码**：阅读 n8n 的 `docker/images/n8n/docker-entrypoint.sh` 和 `packages/cli/src/commands/start.ts` 的 `stopProcess`，对比它的优雅关闭和我们的，列出我们省略的步骤（提示：外部 secret、binary data、license）。

## 6. 延伸阅读

- `docker/images/n8n/`：n8n 的官方镜像和 entrypoint。
- `packages/cli/src/metrics/prometheus/`：所有 Prometheus 指标。
- n8n 文档 “Monitoring” 与 “Scaling” 两节：生产环境的指标、告警和部署拓扑建议。
