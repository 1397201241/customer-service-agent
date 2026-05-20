# 电商售后客服 Agent 设计文档

## 1. 项目概述

基于 LangChain 的电商售后客服 Agent，支持命令行交互和 Web API 两种模式，对话历史持久化到 SQLite。

## 2. Agent 类型选择

**选用 ReAct Agent (langchain.agents.create_react_agent)**

理由：
- 电商售后场景需要多步推理（理解问题→查询订单→判断政策→生成回复）
- ReAct 的 Thought-Action-Observation 循环适合处理需要工具调用的复杂流程
- 相比 OpenAI Functions Agent，ReAct 更通用，不绑定特定模型

## 3. Tools 定义

| Tool | 功能 | 输入 | 输出 |
|------|------|------|------|
| `order_lookup` | 查询订单信息 | 订单号/手机号 | 订单详情、物流状态 |
| `refund_policy_check` | 查询退款政策 | 商品类目、购买时间 | 是否符合退款条件、退款比例 |
| `return_process_guide` | 退货流程指引 | 商品类型、退货原因 | 退货步骤、地址、注意事项 |
| `human_handoff` | 转人工客服 | 转接原因 | 确认信息、排队状态 |

## 4. Memory 设计

**SQLite 持久化方案**

- 使用 `SQLChatMessageHistory` 保存每条对话的完整历史
- 使用 `ConversationBufferMemory` 作为 Agent 的短期记忆（带窗口限制）
- 会话标识：`session_id`（用户手机号或 UUID）
- 数据库表：`message_store`（id, session_id, message, type, timestamp）

## 5. 对话流程

```
用户输入
  → Agent 分析意图（ReAct Loop）
    → 需要查询？调用 order_lookup / refund_policy_check / return_process_guide
    → 无法处理？调用 human_handoff
  → 生成回复
  → 保存到 SQLite Memory
  → 返回给用户
```

## 6. 项目结构

```
customer_service_agent/
├── pyproject.toml
├── README.md
├── .env.example
├── src/
│   └── customer_service_agent/
│       ├── __init__.py
│       ├── agent.py          # ReAct Agent 核心
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── orders.py     # 订单查询工具
│       │   ├── policy.py     # 退款政策工具
│       │   ├── returns.py    # 退货流程工具
│       │   └── handoff.py    # 转人工工具
│       ├── memory/
│       │   ├── __init__.py
│       │   └── sqlite_memory.py  # SQLite 记忆管理
│       ├── models/
│       │   ├── __init__.py
│       │   └── schemas.py    # Pydantic 数据模型
│       ├── cli.py            # 命令行交互入口
│       └── api.py            # FastAPI Web 服务
├── data/
│   └── .gitkeep
└── tests/
    └── .gitkeep
```

## 7. 技术栈

- Python 3.12+
- LangChain + LangChain-Community
- ChatOpenAI / ChatOllama（支持本地模型）
- FastAPI + Uvicorn（Web API）
- SQLite（持久化）
- Pydantic（数据验证）
- uv（包管理）

## 8. 运行方式

```bash
# 命令行
uv run python -m customer_service_agent.cli

# Web API
uv run uvicorn customer_service_agent.api:app --reload
```
