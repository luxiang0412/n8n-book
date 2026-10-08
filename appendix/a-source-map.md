# 附录 A 源码阅读地图

把书里的每个概念对应到 n8n 的真实路径和 mini-n8n 的对应实现。n8n 的路径以仓库根为基准（本书对照的提交见 `README.md`）；mini-n8n 的路径以 `code/mini-n8n/` 为基准。读 n8n 源码时，先在这里查到入口，再顺着读。

> 所有路径都在写作时用 grep 核对过。n8n 迭代很快，行号可能变，但目录结构相对稳定。找不到时，用文件名或导出的函数名全局搜索。

## 数据模型与图（第 4 章）

| 概念 | n8n | mini-n8n |
|---|---|---|
| 工作流的运行时视图 | `packages/workflow/src/workflow.ts` | `packages/workflow/src/workflow.ts` |
| 节点 / 连接 / 执行数据等接口 | `packages/workflow/src/interfaces.ts` | `packages/workflow/src/interfaces.ts` |
| 图遍历（父/子节点、按目标反转连接） | `packages/workflow/src/common/` | `packages/workflow/src/graph.ts` |
| 条目与配对项（pairedItem） | `interfaces.ts` 的 `INodeExecutionData` | 同名 |

## 节点类型（第 5、16 章）

| 概念 | n8n | mini-n8n |
|---|---|---|
| 节点描述（声明式参数） | `INodeTypeDescription` | 同名 |
| 内置节点 | `packages/nodes-base/nodes/` | `packages/nodes-base/src/nodes/` |
| 动态输入/输出（表达式） | `NodeHelpers.getNodeInputs` | `workflow.ts` 的 `getNodeInputs` / `evaluateDescriptionExpression` |
| 合成的 xxxTool / xxxHitlTool | `packages/cli/src/tool-generation/` | `core/src/node-as-tool.ts`、`node-types.ts` |

## 表达式（第 6 章）

| 概念 | n8n | mini-n8n |
|---|---|---|
| 表达式求值 | `packages/workflow/src/expression.ts` | `packages/workflow/src/expression.ts` |
| 数据代理（`$json`、`$(...)`、`$execution`） | `packages/workflow/src/workflow-data-proxy.ts` | `packages/workflow/src/workflow-data-proxy.ts` |
| 沙箱（tournament + PrototypeSanitizer / isolated-vm） | `packages/workflow/src/ExpressionExtensions/` 等 | `packages/workflow/src/expression-sandbox.ts` |

## 执行引擎（第 7、8 章）

| 概念 | n8n | mini-n8n |
|---|---|---|
| 执行引擎主体 | `packages/core/src/execution-engine/workflow-execute.ts` | `packages/core/src/workflow-execute.ts` |
| 执行上下文 | `.../node-execution-context/` | `packages/core/src/execute-context.ts` |
| 执行栈 + waitingExecution（v1 深度优先） | `workflow-execute.ts` | `workflow-execute.ts` |
| onError 模式、重试、错误输出 | `workflow-execute.ts` 的 `runNode` | 同名 |
| Wait 与恢复 | `workflow-execute.ts` 的 `handleWaitingState` | `workflow-execute.ts:416` |
| 部分执行 | `partial-execution-utils/` | `packages/core/src/partial-execution.ts` |

## 持久化与凭证（第 9、11 章）

| 概念 | n8n | mini-n8n |
|---|---|---|
| 数据库实体 | `packages/@n8n/db/src/entities/` | `packages/cli/src/databases/db.ts` |
| 执行元数据 / 执行数据分表 | `execution_entity` / `execution_data` | 同名表 |
| 凭证加密（envelope、cipher） | `packages/core/src/encryption/`、`Cipher` | `packages/cli/src/cipher.ts` |
| 凭证装配（authenticate、注入请求） | `packages/core/src/credentials-helper.ts` | `packages/cli/src/credentials-helper.ts` |
| 凭证脱敏（CREDENTIAL_BLANKING_VALUE） | 后端 | `server.ts` 的 `redact` |

## 钩子、推送、触发器（第 10、12 章）

| 概念 | n8n | mini-n8n |
|---|---|---|
| 生命周期钩子（save / push） | `execution-lifecycle/` | `packages/cli/src/execution-lifecycle-hooks.ts` |
| 推送（SSE / WebSocket、pushRef） | `packages/cli/src/push/` | `packages/cli/src/push.ts` |
| 活跃工作流管理 | `active-workflow-manager.ts` | `active-workflow-manager.ts` |
| Schedule 触发器、cron | `packages/@n8n/scheduler/`、`scheduled-task-manager.ts` | `core/src/scheduled-task-manager.ts` |
| Webhook（test / live / waiting） | `packages/cli/src/webhooks/` | `packages/cli/src/webhooks/` |

## 前端（第 13、14、15 章）

| 概念 | n8n | mini-n8n |
|---|---|---|
| 画布（Vue Flow 映射） | `features/.../canvas/composables/useCanvasMapping.ts` | `editor/src/composables/useCanvasMapping.ts` |
| 节点详情（NDV） | `features/.../ndv/` | `editor/src/components/NodeDetailsView.vue` |
| 状态管理（Pinia stores） | `features/.../*.store.ts` | `editor/src/stores/` |
| 节点面板（NodeCreator、mode 动作） | `features/shared/nodeCreator/` | `editor/src/components/NodeCreator.vue` |

## AI（第 16–23 章）

| 概念 | n8n | mini-n8n |
|---|---|---|
| Cluster node、supplyData、getInputConnectionData | `.../node-execution-context/utils/get-input-connection-data.ts` | `core/src/get-input-connection-data.ts` |
| 日志包装（logWrapper / N8nLlmTracing） | `packages/@n8n/ai-utilities/src/utils/log-wrapper.ts` | `nodes-ai/src/models/log-wrapper.ts` |
| Tools Agent（V3，EngineRequest/Response） | `.../nodes-langchain/nodes/agents/Agent/` | `nodes-ai/src/agent/execute.ts` |
| 引擎处理工具请求（压栈、恢复） | `core/src/execution-engine/requests-response.ts` | `core/src/workflow-execute.ts`（handleEngineRequest） |
| 向量库工厂、三种模式 | `packages/@n8n/ai-utilities/src/utils/vector-store/createVectorStoreNode/` | `nodes-ai/src/nodes/rag.ts`、`rag/` |
| 结构化输出（format_final_json_response） | `.../ToolsAgent/common.ts`、`V3/helpers/runAgent.ts` | `nodes-ai/src/agent/execute.ts`、`nodes/output-parser.ts` |
| 人工审批（HITL 工具合成） | `cli/src/tool-generation/hitl-tools.ts`、`.../createHitlToolkit` | `nodes-ai/src/nodes/approval-tool.ts` |
| Chat Trigger、流式 | `.../trigger/ChatTrigger/` | `nodes-ai/src/nodes/chat-trigger.ts`、`webhooks/webhook-helpers.ts` |

## 平台化（第 24–28 章）

| 概念 | n8n | mini-n8n |
|---|---|---|
| Execute Workflow 节点 | `nodes-base/nodes/ExecuteWorkflow/` | `nodes-base/src/nodes/ExecuteWorkflow.node.ts` |
| 子工作流等待、WaitTracker | `base-execute-context.ts`、`cli/src/wait-tracker.ts` | `core/src/execute-context.ts`、`cli/src/wait-tracker.ts` |
| 队列模式（Bull、job-processor、pub/sub） | `packages/cli/src/scaling/` | `packages/cli/src/scaling/` |
| worker 进程 | `cli/src/commands/worker.ts` | `cli/src/commands/worker.ts` |
| Task Runner（Code 节点隔离） | `packages/@n8n/task-runner/`、`cli/src/task-runners/` | `packages/task-runner/`、`cli/src/task-runners/task-runner-process.ts` |
| 用户、会话、权限 | `packages/cli/src/auth/`、`@n8n/permissions` | `packages/cli/src/auth/` |
| 开放 API | `packages/cli/src/public-api/` | `packages/cli/src/public-api/routes.ts` |
| 健康检查、指标 | `abstract-server.ts`、`metrics/prometheus/` | `server.ts`、`cli/src/metrics.ts` |
| 执行清理 | `services/pruning/` | `cli/src/executions-pruning.ts` |
| 镜像、部署 | `docker/images/n8n/` | `Dockerfile`、`docker-compose.yml` |

## 怎么高效读 n8n 源码

1. **从一个真实请求入手**：想懂某个功能，先在 `packages/cli/src/controllers/` 或 `webhooks/` 找到入口路由，再往下追。
2. **用导出名搜索，别记路径**：`grep -rn "export function xxx" packages`。n8n 的函数名很稳定，路径常变。
3. **先读 mini-n8n，再读 n8n**：mini-n8n 是同一个概念去掉企业功能、多后端、边界情况后的样子。懂了主干，再去 n8n 里看它多处理了哪些情况。
4. **测试是最好的文档**：n8n 的 `__tests__/` 展示了每个模块的输入输出和边界。
