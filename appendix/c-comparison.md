# 附录 C 横向对比：n8n / Dify / LangGraph

> 目的：把本书学到的概念放进更大的版图。各项目都在快速迭代，以下是**架构层面**的比较，具体功能以各自官方文档为准。

## 定位

| | n8n | Dify | LangGraph |
|---|---|---|---|
| 形态 | 开源工作流自动化平台 | 开源 LLM 应用平台（可视化 + API） | 开源**代码库**（Python / JS） |
| 主要用户 | 运营、自动化工程师、开发者 | 产品、业务、开发者 | 开发者 |
| 编排方式 | 画布 DAG，数据沿边传递 | 画布 DAG + 容器节点，共享变量池 | 用代码定义状态图（**允许有环**） |
| LLM 原生程度 | 中：AI 节点是几百种节点中的一类 | 高：模型、提示词、RAG、Agent 都是一等公民 | 高 |
| 节点生态 | 极广：500+ 集成（SaaS、数据库、文件…） | 以 LLM 相关为主 | 靠 LangChain 生态 |

一句话概括三者的性格：**n8n 是“什么都能连的自动化平台，顺手把 AI 做成了节点”**；Dify 是“专门为 LLM 应用设计的平台”；LangGraph 是“给开发者写 Agent 的库”。

## 引擎模型

| 维度 | n8n | Dify（graphon） | LangGraph |
|---|---|---|---|
| 图 | DAG，数据沿边以 **items 数组** 传递 | DAG（循环用容器节点实现） | 有向图，**可以有环**；节点通过共享 State 通信 |
| 数据传递 | 沿边传递：上游输出即下游输入；跨节点引用用 `$('节点名')` 表达式 | 共享变量池 + selector | 共享 State + reducer（定义更新怎样合并） |
| 一个节点处理什么 | 一个 **items 数组**（天然支持“对每条数据做同样的事”） | 一次调用 | 一次状态转换 |
| 分支 | IF / Switch 节点 | 分支节点 + 边状态 + 跳过传播 | 条件边函数返回下一个节点 |
| 暂停 / 恢复 | Wait 节点 + 执行数据序列化 + WaitTracker | 人工输入节点 + 运行时状态序列化 | Checkpointer 每步保存 State，`interrupt()` 支持人在回路，可“时间旅行” |
| 执行顺序 | v1：深度优先（执行栈 unshift） | 就绪即执行 | superstep（Pregel / BSP） |

几点值得注意：

- **n8n 的“items 数组”是它最鲜明的特征**。每个节点天生对一个数组逐条处理，这对 ETL、批量操作特别顺手——“把这 100 行都发一遍邮件”不用写循环。代价是“引用三步之前某一条数据”要靠表达式，没有 Dify 变量池那么直接。
- **LangGraph 允许有环**，所以 Agent 循环（模型 ⇄ 工具）可以直接画成图里的环。n8n 和 Dify 都把 Agent 封装成一个节点，外层保持 DAG。这是**可控性与表达力的不同取舍**：DAG 好懂、好可视化，环更灵活但更难画清楚。
- **三者的“暂停/恢复”深度不同**。LangGraph 每个 superstep 都存 State，所以回放、时间旅行天然支持；n8n 和 Dify 只在需要暂停时才序列化。本书第 7、24 章实现的正是 n8n 这种“按需序列化 + 栈恢复”。

## AI Agent 的实现方式

| | n8n | Dify | LangGraph |
|---|---|---|---|
| Agent 形态 | 一个 Cluster Node：AI Agent + 模型/记忆/工具子节点 | 一个 Agent 节点或 Agent 应用 | 用图直接表达（`create_react_agent` 或自定义图） |
| 工具执行 | **引擎**执行工具节点（EngineRequest/Response，第 19 章） | Agent 节点内部调用 | ToolNode，图里的一个节点 |
| 工具来源 | 专用工具节点、任意节点合成工具、子工作流、MCP | 内置工具、自定义工具、MCP | `@tool` 装饰的函数、LangChain 工具、MCP 适配器 |
| 把 Agent 当工具 | AI Agent Tool（嵌套 EngineRequest，第 23 章） | Agent 作为工具 | 子图作为工具 |
| 结构化输出 | `format_final_json_response` 工具 + Output Parser | 结构化输出功能 | `with_structured_output` / 工具 |

n8n 把“工具执行交给引擎”这一步做得很有特色（第 19 章）：Agent 只是返回“我要调这些工具”，由引擎像执行普通节点一样执行它们，于是工具的运行记录、重试、错误处理全都复用了引擎已有的机制。本书第 19、20、23 章的大部分篇幅就在讲这件事。

## 和本书概念的对应

| 本书概念（n8n） | Dify | LangGraph |
|---|---|---|
| items 沿边传递 | 变量池 VariablePool | 共享 State |
| 节点就绪 = 上游执行完 | 边状态 | superstep |
| 生命周期钩子 | GraphEngineLayer | callbacks / checkpointer |
| EngineRequest（引擎跑工具） | Agent 节点内部 | ToolNode |
| Cluster Node 子节点 | 容器节点 | 子图 |
| Wait + WaitTracker | 人工输入节点 + 序列化 | Checkpointer + interrupt |
| 队列模式 + worker | — | LangGraph Platform |
| 发布为 Webhook / 开放 API | Service API | LangGraph Server |

## 该选哪个？

不是“哪个更好”，而是“哪个更贴你的问题”：

- **要把几十个 SaaS、数据库、文件系统串起来，顺带加点 AI**：n8n。它的节点生态和“items 数组”模型就是为这个生的。
- **要做一个以 LLM 为核心的产品（知识库问答、AI 客服），要开箱即用的 RAG 和提示词管理**：Dify。
- **要完全掌控 Agent 的每一步、要环、要时间旅行、能接受写代码**：LangGraph。

学完本书你会发现，这些平台共享同一批底层概念——图、节点、执行状态、工具、暂停恢复。换一个平台，换的只是这些概念的**包装方式**。这也是本书从零实现 mini-n8n 的意义：看清包装之下的东西，换什么平台都不怕。
