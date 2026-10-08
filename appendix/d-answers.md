# 附录 D 练习参考答案

> 巩固题给出完整答案；扩展题给出实现要点或思路；读源码题给出定位和结论。答案不唯一，能讲清“为什么”就行。

## 第 0 章

1. JSON 里只有 `nodes`（节点数组）和 `connections`（按源节点索引的连接），没有坐标以外的布局信息——图就是这两样东西。
2. v0.1 的 `npm test` 跑引擎的核心能力：线性执行、分支、错误、表达式。数一下 `it(...)` 的个数，对照每个测试名里的能力。
3. If 节点最新版类名是 `IfV2`（`packages/nodes-base/nodes/If/V2/IfV2.node.ts`）。

## 第 1 章

1. Workflow 是**确定性**的、步骤固定的流程；Agent 由模型**在运行时决定**调用哪些工具。前者适合“每天同步订单到表格”，后者适合“根据用户问题自己查资料再回答”。
2. 把“判断金额、超过 1000 就走审批、否则直接退款”做成确定性工作流（IF + Human Approval），把“理解用户诉求、决定要不要退款”交给 Agent。关键是**钱的决定不交给模型**。
3. `grep '"tools/' packages/@n8n/nodes-langchain/package.json | wc -l`，数 `n8n.nodes` 里 `dist/nodes/tools/` 开头的条目。

## 第 2 章

1. 依赖方向：`editor-ui → cli → core → nodes-base → workflow`，`workflow` 在最底层，不依赖任何其他包。
2. `n8n-nodes-base` 依赖 `n8n-core` 会造成循环依赖，也会让社区节点被绑死在某个 core 内部实现上；core 一变，所有节点都可能崩。节点只应依赖 `n8n-workflow` 的接口。
3. 有 `executionData` 时走 `processRunExecutionData`（恢复一个已有执行）；没有时走 `run`（全新执行）。

## 第 3 章

1. 六步大致是：REST 控制器 → WorkflowExecutionService → WorkflowRunner → WorkflowExecute（引擎）→ 各节点的 execute → 生命周期钩子（存库 + 推送）。
2. 在 `nodeExecuteBefore` 钩子里 `console.log` 节点名，在 `workflowExecuteBefore` 记开始时间、`workflowExecuteAfter` 打印 `Date.now() - start`。
3. `hookFunctionsSaveProgress` 在 `saveExecutionProgress` 开启时生效，挂在 `nodeExecuteAfter` 上，每个节点执行完就把当前 runData 存库——崩溃后能看到执行到哪一步。

## 第 4 章

1. `connections` 里 Code 连两个 Set（同一个输出接两条边），两个 Set 各连 Merge 的不同输入。`npm run mini-n8n -- execute --file` 跑它。
2. `renameNode` 要改 `nodes` 的键、`connectionsBySourceNode` 和 `connectionsByDestinationNode` 两份索引。进阶：遍历所有节点参数，把 `$('old')` / `$node["old"]` 改成新名，注意别动字符串字面量里的同名文本。
3. n8n 的 `depth` 控制向上追几层。菱形依赖下，去重后两种实现返回的节点集合一致，但顺序可能不同（取决于遍历是深度优先还是广度优先）。

## 第 5 章

1. `Filter` 节点：`execute` 里遍历 items，`evaluateCondition` 为真的保留，输出时 `pairedItem: { item: i }` 指回原下标。
2. 在 `displayParameter` 里，若依赖的参数值是以 `=` 开头的表达式字符串，直接返回 true（显示）。测一个“依赖参数是表达式时字段照常显示”的用例。
3. If 节点有 V1、V2 两个大版本，V2 的条件参数 `type` 是 `filter`。

## 第 6 章

1. 第二个 Set 用 `$('Code').item.json.amount` 把被第一个 Set 丢掉的金额取回来——`$(...)` 能引用任意已执行节点的、与当前条目配对的输出。
2. 在 AST 层把 `x.isEmpty()` 改写成 `__extend(x, 'isEmpty', [])`，`__extend` 里先判断 `x` 是否已有该方法，有就调原方法，没有才用扩展实现，避免误伤。
3. isolate 里用 lazy proxy：表达式访问 `$json.foo` 时，proxy 通过桥接回宿主进程按需取值，而不是一开始就把整个数据复制进 isolate。

## 第 7 章

1. v1 深度优先：If 的 true 分支（2 条）先一路走到 Merge，再回头走 false 分支；Merge 等两个输入到齐后执行，最后 Code。用 mini-n8n 打印 `lastNodeExecuted` 序列验证。
2. 让 Merge 的输入 1 连在一个“没有被任何上游触发”的 Set 上：v1 会追祖先、触发那个 Set；v0 不追，Merge 永远等不齐。
3. 部分执行从“脏节点，或缺少运行数据的节点”开始；`findStartNodes` 沿着到目标节点的子图往回找这些起点。

## 第 8 章

1. 改成 `continueRegularOutput` 后，Validate 出错的条目带着原输入继续往下走（而不是进错误分支）。
2. 在重试判断里，若节点返回的条目只有 `error` 字段，视为失败、触发重试。测一个“第一次返回 error、第二次成功”的用例。
3. 如果失败工作流就是它自己，n8n 会跳过（不触发），避免无限递归。

## 第 9 章

1. `runData` 存这次执行的实际数据，`workflowData` 存执行时的工作流快照。改工作流后旧执行的 `workflowData` 不变——执行是历史快照。
2. 启动时和每小时删 `stoppedAt` 早于 N 小时的执行。这正是第 28 章实现的 `ExecutionsPruning`，可对照。
3. 软删除只打标记（`deletedAt`），到硬删除缓冲期后真正删行；二进制数据存在文件系统/对象存储里，不随行删除，要单独清理。

## 第 10 章

1. `EventSource` 建立 SSE 连接后，curl 带 `push-ref: t1` 触发执行，控制台会依次打印 `executionStarted`、各节点的 `nodeExecuteAfter`、`executionFinished`。
2. `nodeExecuteAfter` 只发 `itemCount`，数据单独走 `nodeExecuteAfterData`；超过 1 MB 时不发数据，前端在执行结束后用 `GET /rest/executions/:id` 拉全量。
3. `websocket.push.ts` 用定时 ping，客户端回 pong；连续没收到 pong 就判定连接已死、清理掉。

## 第 11 章

1. 建 `httpBasicAuth` 凭证填 user/pass，HTTP Request 选该凭证，调 httpbin 的 basic-auth 端点返回 200 即通。
2. `POST /rest/credentials/test`：解密凭证 → 跑 `authenticate` → 按凭证类型的 `test` 规则发请求 → 返回 `{ status, message }`。
3. `credential-domain-restrictions.ts` 校验请求目标域名是否在凭证允许的域名列表里，不在就拒绝——防止凭证被节点发往任意地址。

## 第 12 章

1. Webhook（responseNode）→ If（看 `body.vip`）→ 两个 Respond to Webhook，一个返回 200 一个返回 403。
2. `poll()` 支持：激活时按 `pollInterval` 定时调用 `poll()`，用 `getWorkflowStaticData('node')` 存上次游标，返回非空就启动执行。
3. lastNode 模式下，响应哪个节点由 `lastNodeExecuted` 决定，取其最后一次运行、第一个 item；n8n 可通过 Respond When 等参数配置。

## 第 13 章

1. 改连后 `connections` 里 If 的第 2 个输出（index 1）从原目标变成新的 NoOp 节点。
2. 每种操作写成 `{ do(), undo() }` 命令，压入一个栈；Ctrl+Z 弹栈调 `undo()`，重做用另一个栈。
3. `renameNode` 调 `renameNodeInParameterValue` 递归遍历参数，正则匹配 `$('old')`、`$node["old"]` 等形式；要小心字符串里的引号转义，避免破坏用户的字面量。

## 第 14 章

1. URL 表达式预览会实时显示代入 `$json.id` 后的字符串；Method 切 Expression 后按金额返回 POST/GET。
2. `preview(value, itemIndex)` 多接一个下标，表格行悬停时传入该行下标，预览按该条目求值。
3. 自动补全候选来自上游节点的运行数据和推断出的 schema（字段名、类型）。

## 第 15 章

1. pin 住 Orders 后，即使把它的代码改成抛异常，执行也直接用钉住的数据、不真正运行它，所以不报错——pin data 优先级高于执行。
2. 起始节点在循环体内时，把起点改成 Loop 节点本身（循环入口），否则会从环中间开始、状态不对。参考 `handle-cycles.ts`。
3. 该起始节点被放在它那个有运行数据的父节点的下游位置，作为重建执行栈的起点。

## 第 16 章

1. Session Key 固定成 `"global"` 后，两个会话共享同一段记忆、互相看到对方的消息——会话隔离失效。
2. “Window Buffer Memory (SQLite)”：`supplyData` 返回的记忆对象把消息读写到数据库表（按 session key），重启后仍在。
3. 供应商不返回 token 用量时，`N8nLlmTracing` 用分词器估算 prompt 和 completion 的 token 数。

## 第 17 章

1. Basic LLM Chain + Ollama，执行后模型节点 NDV 能看到发出的 messages（system + user）和响应。
2. `OpenAICompatibleChatModel` 遇 429/5xx 按 1s/2s/4s 退避重试最多 3 次；用本地假服务器先返回 429 再返回 200 来测。
3. 限制响应大小必须在 fetch 层（边读边数字节、超限就中断），否则恶意/异常的大响应在“拿到完整响应再检查”之前就已经把内存吃光了。

## 第 18 章

1. Max Iterations=1 时，第一次模型调用请求工具，但引擎还没来得及给出结果就达到了迭代上限，第二次（本应处理工具结果）之前就报错。
2. 最终输出带 `intermediateSteps`（每步的工具名、输入、输出），编辑器输出面板用表格展示。
3. `saveToMemory()` 把带工具调用的一轮合并保存；`previousCount` 用来跳过已经存过的历史消息，只存新增的。

## 第 19 章

1. `executionOrder` 改成 v0 一般不改变工具的执行结果（工具由 EngineRequest 单独调度），但主流程里多输入节点的顺序可能变。运行验证。
2. 工具节点设了 Timeout 时，引擎用 `Promise.race` 加超时；超时就把 `Error: timed out` 作为该工具的结果交回 Agent，不拖垮整个执行。
3. 有 `parentNodeName`（子 Agent 的工具）时，`parentRunIndex` 取父节点已有的运行次数减一——指向父 Agent 当前这一次运行，让工具的日志挂在正确的父运行下。

## 第 20 章

1. HTTP Request Tool 的 URL 用 `$fromAI('city', ...)`，问天气时模型把 `city` 填成 `Tokyo`，NDV 的输入里能看到它填的参数。
2. MCP Server Trigger：`inputs` 为 `ai_tool` 的 Webhook 触发器，`tools/list` 时用 `getInputConnectionData` 收集连着的工具定义返回，`tools/call` 时执行对应工具节点。
3. `extractFromAICalls()` 用一个能处理嵌套引号和逗号的解析器（不是简单 split），正确切出 `$fromAI('q', 'a "quoted", text')` 的各个参数。

## 第 21 章

1. 带 `-N` 的 curl 会看到回答逐行（逐 token）到达，而不是一次性返回——这就是流式。
2. Simple Memory 记每个 session 的最后访问时间，清理定时器删除超过一小时未访问的；用注入的假时钟推进时间来测。
3. `responseNodes` 模式下，工作流里的多个 Chat/Respond 节点可以分别向聊天窗口发消息，实现“一次执行多次回复”。

## 第 22 章

1. Chunk Size=40 时块数变多，每块更短，`chunkIndex` 增大、`itemIndex` 仍指原条目；检索更精细但可能丢上下文。
2. `update` 模式按 ID 更新向量；元数据过滤在相似度排序前先按 `title` 等字段筛选。写一个“过滤后只返回 Shipping 块”的测试。
3. `retrieve` 输出 `ai_vectorStore` 给 Question and Answer Chain，由 **Chain** 决定何时检索；`retrieve-as-tool` 输出 `ai_tool`，由 **Agent** 决定何时检索。

## 第 23 章

1. 点 Reject 后 Agent 回复“人类拒绝了调用”，Refund 不运行；再次打开同一链接返回 409（执行已不是 waiting）。
2. 把 Human Approval 放子 Agent 下——mini-n8n 支持（嵌套 EngineRequest），n8n 不支持。等待时执行栈有外层 Agent、子 Agent、审批节点等多层。
3. 审批人填反馈时，`getChatInput()` 取到反馈文本，`getDenialMessage()` 生成带反馈的消息给 Agent（而非简单“已拒绝”）。我们的实现要在等待 Webhook 里接收文本、存进节点状态、拒绝分支里带上。

## 第 24 章

1. 父执行显示 `waiting`（等子工作流），子执行也 `waiting`（Wait 节点）；两分钟后 WaitTracker 恢复子执行，父执行随之 `success`。
2. `resumeParentsOfFinishedSubExecutions()`：扫描“栈顶 metadata 有 `waitingChildExecutionIds` 且那些子执行已结束”的父执行，打补丁并恢复。测“子执行先结束、父执行后置 waiting”的竞态。
3. 等待 Webhook 恢复子执行后，在 `resumeParentExecution` 里给父执行打补丁并认领恢复——和 WaitTracker 用同一套逻辑。

## 第 25 章

1. `--concurrency 1` 时两个 worker 共 2 个并发槽，20 个各 0.2 秒的请求约需 2 秒（原来 10 槽约 0.5 秒）——并发槽变少，吞吐下降。
2. worker 每 10 秒给正在处理的任务续 Redis 锁（带过期）；main 扫 “active” 列表，锁过期的任务放回 “waiting”。`kill -9` 一个 worker，它的任务锁到期后被另一个 worker 接走。
3. `job-outcome-tracker.ts` 在错过 `job-finished` 消息时，回查数据库里该执行的最终状态来“结案”，避免因消息丢失而永远等待。

## 第 26 章

1. 超时 2 秒的 `while(true){}`：约 2 秒后报 `Task execution timed out after 2 seconds`，runner 被重启，执行状态为 `error`。
2. 给 runner 加并发：主进程用信号量限制同时在跑的任务数，超出的排队；或让一个 runner 进程并行处理多个任务。
3. built-ins-parser 用 acorn 静态分析代码，找出它真正引用了哪些变量（`$json`、`$('X')`…），只把这些数据发给 runner——大执行时能省下大量序列化和传输。

## 第 27 章

1. setup 拿 cookie → 建 key → 用 `X-N8N-API-KEY` 调 `GET /api/v1/workflows`。只有 `workflow:read` 的 key 去 `POST` 建工作流，返回 403（缺 `workflow:create` scope）。
2. 所有权转移：把该工作流的 `workflow:owner` 从当前用户改成目标用户。转移前确认操作者本就是 owner，别把自己变成无权访问。
3. `global:member` 只有自己资源的 scope；在团队项目里，工作流是按项目分享的，成员看到的是“所在项目的工作流”，个人项目里则只有自己创建的。

## 第 28 章

1. `/metrics` 看指标；激活工作流后 `active_workflow_count` 加一；`MINI_N8N_LOG_FORMAT=json` 后日志变成每行一个 JSON。
2. 给执行计数加 `workflowId` 标签；告警规则思路：`rate(失败数[5m]) / rate(总数[5m]) > 0.5`。
3. n8n 的 `stopProcess` 还会关闭外部 secret 轮询、刷新未落盘的 binary data、释放 license 等——我们都省了。

## 实验室

- **Lab 1–6** 的检查清单本身就是答案：每一项都能用对应的 `npm test` / `npm run test:e2e` / 示例脚本验证。卡住时，先 `git checkout vX.Y` 跑通参考实现，再 `git diff` 看它比你多做了什么。
