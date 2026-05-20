# 电商售后客服 Agent 设计文档

## 1. 项目概述

基于 LangGraph 的电商售后客服 Agent，支持命令行交互和 Web API 两种模式，对话历史持久化到内存（当前），可扩展至 SQLite。

**核心变更（vs 旧版设计）**：
- 旧版基于 `langchain.agents.AgentExecutor`（已废弃）
- 新版基于 `langgraph.prebuilt.create_react_agent`（LangChain 团队推荐标准）
- Memory 从 `SQLChatMessageHistory` 改为 LangGraph Checkpoint 机制

## 2. Agent 类型选择

**选用 LangGraph ReAct Agent (`create_react_agent`)**

理由：
- LangChain 1.3+ 已移除 `AgentExecutor` 和 `create_react_agent`
- `langgraph.prebuilt.create_react_agent` 是官方替代方案，支持多步推理和工具调用
- 内置 Checkpoint 机制，天然支持对话历史持久化
- 支持同步和异步两种调用模式

## 3. Tools 定义

| Tool | 功能 | 输入 | 输出 | 实现方式 |
|------|------|------|------|----------|
| `order_lookup` | 查询订单信息 | 订单号/手机号 | 订单详情、物流状态 | 内存模拟数据（5 条） |
| `refund_policy_check` | 查询退款政策 | 商品类目、购买时间 | 是否符合退款条件、退款比例 | 规则判断 |
| `return_process_guide` | 退货流程指引 | 商品类型、退货原因 | 退货步骤、地址、注意事项 | 固定流程模板 |
| `human_handoff` | 转人工客服 | 转接原因 | 确认信息、排队状态、优先级 | 自动判断优先级 |

## 4. Memory 设计

**当前：InMemorySaver（内存持久化）**

- 使用 LangGraph Checkpoint 机制保存对话状态
- 会话标识：`thread_id`（用户手机号或 UUID）
- 进程重启后历史丢失

**未来扩展：SQLite 持久化**

- 方案 A：`SqliteSaver`（同步，需处理连接生命周期）
- 方案 B：`AsyncSqliteSaver`（异步，需 `aiosqlite`）
- 当前阻塞问题：`from_conn_string()` 返回上下文管理器，与 `create_react_agent` 的 checkpointer 参数不兼容

## 5. LLM 提供商配置

| 提供商 | 类 | API 格式 | Base URL | 默认模型 |
|--------|-----|----------|----------|----------|
| OpenAI | `ChatOpenAI` | OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| MiniMax-CN | `ChatAnthropic` | Anthropic 兼容 | `https://api.minimaxi.com/anthropic` | `MiniMax-M2.7` |

**注意**：MiniMax-CN 使用 Anthropic 兼容 API（非 OpenAI 兼容），通过 `langchain-anthropic` 的 `ChatAnthropic` 类调用。

## 6. 对话流程

```
用户输入
  → Agent 分析意图（ReAct Loop）
    → 需要查询？调用 order_lookup / refund_policy_check / return_process_guide
    → 无法处理？调用 human_handoff
  → 生成回复（MiniMax 输出含 thinking + text，提取 text 部分）
  → 保存到 Checkpoint Memory
  → 返回给用户
```

## 7. 项目结构

```
customer_service_agent/
├── pyproject.toml          # uv 项目配置、入口点
├── README.md               # 使用说明
├── .env.example            # 环境变量模板
├── docs/
│   └── design.md           # 本设计文档
├── src/
│   └── customer_service_agent/
│       ├── __init__.py
│       ├── agent.py         # ReAct Agent 核心（create_react_agent）
│       ├── api.py           # FastAPI Web 服务
│       ├── cli.py           # 命令行交互入口
│       ├── config.py        # 配置管理（Pydantic Settings）
│       ├── tools/
│       │   ├── __init__.py  # ALL_TOOLS 列表
│       │   ├── orders.py    # 订单查询工具
│       │   ├── policy.py    # 退款政策工具
│       │   ├── returns.py   # 退货流程工具
│       │   └── handoff.py   # 转人工工具
│       ├── memory/
│       │   ├── __init__.py
│       │   └── sqlite_memory.py  # Checkpoint 管理（当前 InMemorySaver）
│       └── models/
│           ├── __init__.py
│           └── schemas.py   # Pydantic 数据模型
├── data/                    # SQLite 数据目录（.gitignore）
└── tests/                   # 测试目录（待补充）
```

## 8. 技术栈

- Python 3.12+
- LangGraph + LangChain Core
- ChatOpenAI / ChatAnthropic（LLM）
- FastAPI + Uvicorn（Web API）
- InMemorySaver / SqliteSaver（持久化）
- Pydantic Settings（配置管理）
- uv（包管理）

## 9. 运行方式

```bash
# 命令行
uv run customer-service-agent --provider minimax-cn

# Web API
uv run uvicorn customer_service_agent.api:app --reload

# 环境变量
export LLM_PROVIDER=minimax-cn
export MINIMAX_CN_API_KEY=sk-...
export MINIMAX_CN_BASE_URL=https://api.minimaxi.com/anthropic
export MINIMAX_CN_MODEL=MiniMax-M2.7
```

## 10. 已知问题

1. **SQLite 持久化未完成**：`SqliteSaver` / `AsyncSqliteSaver` 的连接生命周期与 `create_react_agent` 集成有问题，当前使用 `InMemorySaver`
2. **MiniMax 输出格式**：M2.7 返回 `[{"type": "thinking", ...}, {"type": "text", ...}]`，已在 `agent.py` 中提取 `text` 部分
3. **测试覆盖不足**：无单元测试和集成测试
