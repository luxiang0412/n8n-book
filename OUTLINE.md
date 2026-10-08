# 《从 n8n 到 Mini-n8n：从零构建 AI Agent Workflow 平台》大纲

> 参照仓库：`n8n-io/n8n` @ `60ad29f242`（`packages/cli` 版本 2.43.0）
> 读者目标：读完后，能从零写出一个前后端都能运行、支持 AI Agent 的 Workflow 自动化平台。
> 写作方式：每章先讲概念，再读 n8n 源码（`路径:行号`），再在 mini-n8n 里实现，最后给出真实运行结果。

## 贯穿全书的项目：mini-n8n

| 版本 | 能力 | 章节 |
|---|---|---|
| v0.1 | 数据模型、表达式与沙箱、栈式执行引擎、12 个核心节点、CLI | Part II（4–8 章、Lab 1） |
| v0.2 | SQLite 持久化、REST API、生命周期钩子、SSE 推送、凭证加密、Webhook / Schedule 触发器 | Part III（9–12 章、Lab 2） |
| v0.3 | Vue 3 + Vue Flow 画布、参数面板（NDV）、表达式预览、运行与调试 | Part IV（13–15 章、Lab 3） |
| v0.4 | AI 连接类型、Chat Model（Mock / Ollama / OpenAI 兼容）、Tools Agent、EngineRequest、工具、记忆、Chat Trigger、流式 | Part V（16–21 章、Lab 4） |
| v0.5 | RAG（Embeddings、向量存储、检索工具）、Agent as Tool、人工审批（HITL）、结构化输出 | Part VI（22–23 章、Lab 5） |
| v1.0 | 子工作流、等待与恢复、队列模式 + Worker、Code 节点 Task Runner、多用户与 API Key、Docker 部署 | Part VII（24–28 章、Lab 6） |

默认技术栈：TypeScript monorepo（npm workspaces）、`tsx`、Vitest、Fastify、`node:sqlite`、Vue 3 + Pinia + Vue Flow。所有 AI 功能都能用离线的 Mock 模型运行，也用本地 Ollama（`qwen2.5:0.5b`）验证过。

## Part 0 导读
- 第 0 章 本书怎么读：环境、目录、如何读 n8n 源码

## Part I 全景（浅）
- 第 1 章 从自动化到 AI Agent：Workflow 平台的几种形态
- 第 2 章 n8n 架构鸟瞰：monorepo、包依赖、运行时拓扑
- 第 3 章 一次执行的完整生命周期 ★：从点击按钮到画布变绿

## Part II 工作流引擎 → v0.1
- 第 4 章 数据模型：节点、连接与 items ★
- 第 5 章 节点类型系统：description 驱动一切
- 第 6 章 表达式引擎：`{{ $json }}`、数据代理与沙箱
- 第 7 章 执行引擎：执行栈与等待区 ★★
- 第 8 章 健壮性：错误输出、重试、取消、超时、等待
- Lab 1：mini-n8n v0.1 —— 用 CLI 跑一个带分支、合并和循环的工作流

## Part III 服务端 → v0.2
- 第 9 章 持久化：工作流、执行记录与运行数据
- 第 10 章 生命周期钩子与实时推送
- 第 11 章 凭证：加密存储与注入
- 第 12 章 触发器：Webhook、Schedule 与激活
- Lab 2：REST API + Webhook + 定时任务

## Part IV 编辑器 → v0.3
- 第 13 章 画布：Vue Flow 与工作流数据的映射
- 第 14 章 节点详情视图（NDV）：参数渲染与表达式编辑
- 第 15 章 运行与调试：实时状态、Pin 数据与部分执行
- Lab 3：可视化编排 + 实时执行

## Part V AI Agent → v0.4 ★
- 第 16 章 AI 连接类型与 Cluster Node：`supplyData` 的设计 ★
- 第 17 章 Chat Model 抽象：Mock、Ollama 与流式
- 第 18 章 Tools Agent：函数调用循环 ★★
- 第 19 章 EngineRequest：让引擎来调度工具 ★★
- 第 20 章 工具体系：节点即工具、`$fromAI`、Workflow Tool、MCP
- 第 21 章 记忆、Chat Trigger 与流式响应
- Lab 4：从零搭一个能调工具、有记忆的 AI Agent 工作流

## Part VI 高级 AI → v0.5
- 第 22 章 RAG：Embeddings、向量存储与检索工具
- 第 23 章 多 Agent、人工审批与结构化输出
- Lab 5：知识库问答 + 需人工审批的工具

## Part VII 平台化（深）→ v1.0
- 第 24 章 子工作流与等待/恢复
- 第 25 章 队列模式与横向扩展
- 第 26 章 Code 节点的安全：Task Runner
- 第 27 章 多用户、权限与开放 API
- 第 28 章 部署与可观测
- Lab 6：一键部署的 mini-n8n v1.0

## 附录
- A 源码阅读地图（概念 → n8n 路径 → mini-n8n 路径）
- B 术语表
- C 横向对比：n8n / Dify / LangGraph
- D 练习参考答案
