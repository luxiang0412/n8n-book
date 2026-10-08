# 附录 B 术语表

按主题分组。每条给出中文、英文（n8n 代码里用的词）和一句话解释。括号里是首次出现的章节。

## 工作流与节点

- **工作流（workflow）**：一张由节点和连接组成的图，描述“数据怎样从触发器流到各个动作”。（第 1 章）
- **节点（node）**：工作流里的一个步骤。有触发节点、普通节点、子节点三类。（第 1 章）
- **连接（connection）**：两个节点之间的一条边，有类型（`main` 或 `ai_*`）。`workflow.connections` 按 **源节点** 索引。（第 4 章）
- **条目（item）**：节点之间流动的数据单元，形如 `{ json, binary?, pairedItem? }`。一个节点处理一个条目数组。（第 4 章）
- **配对项（pairedItem）**：记录一个输出条目来自哪个输入条目，支撑“跨节点回溯数据”。（第 4 章）
- **触发器（trigger）**：启动工作流的节点，如 Manual、Webhook、Schedule、Chat Trigger。（第 12 章）
- **子节点（sub-node）**：没有 `main` 输出、通过 `ai_*` 连接挂在根节点下的节点，如 Chat Model、Memory、Tool。由根节点通过 `supplyData` 拉取。（第 16 章）
- **Cluster Node**：一个根节点带一组子节点的整体，如 AI Agent + 模型 + 记忆 + 工具。（第 16 章）

## 表达式

- **表达式（expression）**：`{{ ... }}` 里的一段 JS，在运行时按当前数据求值。（第 6 章）
- **数据代理（data proxy）**：表达式里 `$json`、`$('节点名')`、`$execution` 等变量背后的对象。（第 6 章）
- **沙箱（sandbox）**：隔离表达式求值的机制。n8n 用 tournament + PrototypeSanitizer，默认引擎是 isolated-vm。（第 6 章）

## 执行

- **执行（execution）**：工作流的一次运行，有状态（new/running/success/error/waiting/crashed）。（第 7 章）
- **执行数据（run execution data，`IRunExecutionData`）**：一次执行的全部可序列化状态：执行栈、各节点的运行记录、等待信息。能存库、能恢复。（第 7 章）
- **执行栈（node execution stack）**：待执行节点的栈。v1 执行顺序靠 unshift + 位置排序实现深度优先。（第 7 章）
- **等待区（waitingExecution）**：等待多个输入到齐才能执行的节点暂存区（如 Merge）。（第 7 章）
- **运行记录（run data，`ITaskData`）**：一个节点一次运行的输入、输出、耗时、状态。（第 7 章）
- **onError 模式**：节点出错时的行为：停止、继续（正常输出）、走错误输出。（第 8 章）
- **部分执行（partial execution）**：编辑器里“执行某个节点”时，只重跑到该节点的脏子图。（第 15 章）
- **pin data**：把某节点的输出钉住，之后执行直接用钉住的数据，不再真正运行它。（第 15 章）

## 持久化与凭证

- **凭证（credential）**：一组加密保存的密钥/令牌，节点用它认证外部服务。（第 11 章）
- **信封加密（envelope encryption）**：用密钥管理模块决定的密钥加密凭证数据；新代码只用 `cipher.encryptV2 / decryptV2`。（第 11 章）
- **脱敏值（`CREDENTIAL_BLANKING_VALUE`）**：读凭证时返回的占位符，表示“这里有个密钥但不给你看”；写回时它表示“不改”。（第 11 章）

## 钩子、推送、触发

- **生命周期钩子（lifecycle hooks）**：执行各阶段触发的回调，用来存库、推送进度。（第 10 章）
- **推送（push）**：服务器主动把执行进度发给编辑器标签页，走 SSE 或 WebSocket，用 `pushRef` 标识标签页。（第 10 章）
- **活跃工作流管理（ActiveWorkflowManager）**：激活工作流时注册它的触发器和 Webhook。（第 12 章）
- **Webhook：test / live / waiting**：test 是编辑器里“监听一次”；live 是激活后的生产 URL；waiting 是等待执行恢复用的 URL。（第 12、23 章）

## AI

- **supplyData**：子节点提供能力的方法（返回模型、记忆、工具或向量库），区别于普通节点的 `execute`。（第 16 章）
- **EngineRequest / EngineResponse**：Agent V3 让引擎执行工具的协议：Agent 返回“请执行这些节点”，引擎执行后带结果再调用 Agent。（第 19 章）
- **节点即工具（node as tool）**：把普通节点合成成 Agent 可调用的工具；参数用 `$fromAI()` 由模型填。（第 20 章）
- **RAG（检索增强生成）**：先从向量库检索相关文本块，只把它们交给模型作答。（第 22 章）
- **Embedding（向量化）**：把文本变成定长数字数组，语义相近则方向相近。（第 22 章）
- **向量库（vector store）**：保存“文本块 + 向量 + 元数据”，按余弦相似度检索。（第 22 章）
- **结构化输出（structured output）**：让 Agent 通过 `format_final_json_response` 工具按 JSON Schema 作答。（第 23 章）
- **人工审批（HITL，Human in the Loop）**：某些工具调用前停下来等人批准，批准后再执行。（第 23 章）

## 平台化

- **子工作流（sub-workflow）**：被另一个工作流用 Execute Workflow 节点调用的工作流。（第 24 章）
- **WaitTracker**：轮询数据库、恢复到期等待执行的组件。（第 24 章）
- **`WAIT_FOR_SUB_EXECUTION`**：父执行等子执行时用的遥远到期日（2999-12-31），WaitTracker 不会主动恢复它。（第 24 章）
- **认领（claim）**：用带条件的 UPDATE 把 `waiting` 原子地改成 `running`，保证一个等待执行只被恢复一次。（第 24 章）
- **队列模式（queue mode）**：main 接活、worker 干活；执行入队，队列里只放执行 ID。（第 25 章）
- **worker**：从队列取执行并运行的进程，不提供编辑器和触发器。（第 25 章）
- **Task Runner**：运行 Code 节点代码的独立子进程，与主进程隔离。（第 26 章）
- **全局角色（global role）**：`global:owner`（管理员）/ `global:member`。（第 27 章）
- **共享（sharing）**：把工作流或凭证分享给其他用户（owner / editor / user 角色）。（第 27 章）
- **API Key**：带 scope 的令牌，用于开放 API 的认证；只存哈希。（第 27 章）
- **存活 / 就绪检查（liveness / readiness）**：`/healthz` 表示进程活着；`/healthz/readiness` 表示能收流量。（第 28 章）
- **优雅关闭（graceful shutdown）**：收到 SIGTERM 后停止接活、等正在跑的执行结束再退出。（第 28 章）
