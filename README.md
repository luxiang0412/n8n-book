# 从 n8n 到 Mini-n8n

> 读 n8n 源码，从零写一个能跑的 AI Agent Workflow 平台。
> 配套代码：[github.com/luxiang0412/mini-n8n](https://github.com/luxiang0412/mini-n8n)

读完这本书，你能从零写出一个工作流自动化平台：图模型与执行引擎、服务端与持久化、可视化编辑器、AI Agent（工具调用、RAG、记忆、流式、人工审批），直到队列模式、沙箱、多用户和一键部署。全书对照 n8n 真实源码，每一章都伴随一个能跑、有测试的 `mini-n8n` 版本（`v0.1` → `v1.0`），一个 Part 一个 git tag，`git diff` 即可看到每一步的改动。

## 怎么读

- **按顺序读**：每个 Part 在上一个的基础上加一层能力，配套代码也随之从 `v0.1` 长到 `v1.0`。
- **边读边跑**：每章都有“运行与验证”，命令和真实输出都在书里。切到对应 tag（`git checkout v0.4`）跑 `npm test`，再 `git diff v0.3 v0.4` 看这一版做了什么。
- **先读 mini，再读 n8n**：mini-n8n 是 n8n 的主干。懂了主干，书里的“源码阅读地图”（附录 A）带你回到 n8n 看它多处理了哪些情况。

## 目录

### Part 0 导读
- [第 0 章 本书怎么读](chapters/00-how-to-read.md)

### Part I 全景（浅）
- [第 1 章 从自动化到 AI Agent：Workflow 平台的几种形态](chapters/01-forms.md)
- [第 2 章 n8n 架构鸟瞰：monorepo、包依赖、运行时拓扑](chapters/02-architecture.md)
- [第 3 章 一次执行的完整生命周期 ★](chapters/03-one-execution.md)

### Part II 工作流引擎 → v0.1
- [第 4 章 数据模型：节点、连接与 items ★](chapters/04-data-model.md)
- [第 5 章 节点类型系统：description 驱动一切](chapters/05-node-types.md)
- [第 6 章 表达式引擎：`{{ $json }}`、数据代理与沙箱](chapters/06-expressions.md)
- [第 7 章 执行引擎：执行栈与等待区 ★★](chapters/07-execution-engine.md)
- [第 8 章 健壮性：错误输出、重试、取消、超时、等待](chapters/08-robustness.md)
- [Lab 1：mini-n8n v0.1 —— 用 CLI 跑一个带分支、合并和循环的工作流](chapters/lab-1-engine.md)

### Part III 服务端 → v0.2
- [第 9 章 持久化：工作流、执行记录与运行数据](chapters/09-persistence.md)
- [第 10 章 生命周期钩子与实时推送](chapters/10-hooks-and-push.md)
- [第 11 章 凭证：加密存储与注入](chapters/11-credentials.md)
- [第 12 章 触发器：Webhook、Schedule 与激活](chapters/12-triggers.md)
- [Lab 2：mini-n8n v0.2 —— REST API + Webhook + 定时任务](chapters/lab-2-server.md)

### Part IV 编辑器 → v0.3
- [第 13 章 画布：Vue Flow 与工作流数据的映射](chapters/13-canvas.md)
- [第 14 章 节点详情视图（NDV）：参数渲染与表达式编辑](chapters/14-ndv.md)
- [第 15 章 运行与调试：实时状态、Pin 数据与部分执行](chapters/15-run-and-debug.md)
- [Lab 3：mini-n8n v0.3 —— 可视化编排 + 实时执行](chapters/lab-3-editor.md)

### Part V AI Agent → v0.4 ★
- [第 16 章 AI 连接类型与 Cluster Node：`supplyData` 的设计 ★](chapters/16-cluster-nodes.md)
- [第 17 章 Chat Model 抽象：Mock、Ollama 与流式](chapters/17-chat-models.md)
- [第 18 章 Tools Agent：函数调用循环 ★★](chapters/18-tools-agent.md)
- [第 19 章 EngineRequest：让引擎来调度工具 ★★](chapters/19-engine-request.md)
- [第 20 章 工具体系：节点即工具、`$fromAI`、Workflow Tool、MCP](chapters/20-tools.md)
- [第 21 章 记忆、Chat Trigger 与流式响应](chapters/21-memory-chat-streaming.md)
- [Lab 4：从零搭一个能调工具、有记忆的 AI Agent 工作流](chapters/lab-4-agent.md)

### Part VI 高级 AI → v0.5
- [第 22 章 RAG：Embeddings、向量存储与检索工具](chapters/22-rag.md)
- [第 23 章 多 Agent、人工审批与结构化输出](chapters/23-multi-agent-hitl.md)
- [Lab 5：知识库问答 + 需要人工审批的工具](chapters/lab-5-rag-hitl.md)

### Part VII 平台化（深）→ v1.0
- [第 24 章 子工作流与等待/恢复](chapters/24-subworkflows-waiting.md)
- [第 25 章 队列模式与横向扩展](chapters/25-queue-mode.md)
- [第 26 章 Code 节点的安全：Task Runner](chapters/26-task-runner.md)
- [第 27 章 多用户、权限与开放 API](chapters/27-users-permissions-api.md)
- [第 28 章 部署与可观测](chapters/28-deployment-observability.md)
- [Lab 6：一键部署的 mini-n8n v1.0](chapters/lab-6-deploy.md)

### 附录
- [附录 A 源码阅读地图](appendix/a-source-map.md)
- [附录 B 术语表](appendix/b-glossary.md)
- [附录 C 横向对比：n8n / Dify / LangGraph](appendix/c-comparison.md)
- [附录 D 练习参考答案](appendix/d-answers.md)

## 配套代码 mini-n8n

`code/mini-n8n/` 是一个独立的 git 仓库，一个 Part 一个 tag：

| Tag | 能力 |
|---|---|
| v0.1 | 数据模型、表达式与沙箱、栈式执行引擎、核心节点、CLI |
| v0.2 | SQLite 持久化、REST API、生命周期钩子、SSE 推送、凭证加密、Webhook / Schedule 触发器 |
| v0.3 | Vue 3 + Vue Flow 编辑器：画布、节点面板、NDV、实时执行、pin data、部分执行 |
| v0.4 | AI：Chat Trigger、AI Agent（EngineRequest 循环）、Mock / Ollama / OpenAI 兼容模型、记忆、工具、流式 |
| v0.5 | RAG、结构化输出、Agent as Tool、人工审批 |
| v1.0 | 子工作流与等待/恢复、队列模式 + Worker、Code 节点 Task Runner、多用户 / API Key / 开放 API、指标、Docker 部署 |

```bash
cd code/mini-n8n
npm install
npm test                 # 全部单元测试
npm start                # 构建编辑器并在 http://localhost:5678 启动
npm run test:e2e         # 用无头 Chrome 驱动编辑器（服务器需先启动）
```

## 这本书是怎么验证的

- **单元测试**：`v1.0` 共 82 个测试通过（引擎、表达式、AI、服务端、队列、Task Runner、认证、运维）。
- **浏览器端到端**：5 套、43 项 Playwright 检查，真实驱动编辑器；书里的编辑器截图都来自这些测试。
- **真实模型**：AI 章节用本地 Ollama（qwen2.5 系列、nomic-embed-text）实跑，输出和局限如实记录。
- **真实部署**：`deploy/e2e.sh` 用 Docker Compose 起 Redis + main + 2 worker，建工作流、30 并发、优雅关闭、重启留存，全部验证。

书里“踩坑记录”只写真实遇到的问题；自查发现的问题会标注“自查发现”；所有引用的 `路径:行号` 都用 grep 核对过；所有命令输出都是真实运行的结果。
