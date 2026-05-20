# Customer Service Agent 项目上下文

## 项目概述
基于 LangChain 的电商售后客服 Agent，支持命令行交互和 Web API 两种模式，对话历史持久化到 SQLite。

## 技术栈
- Python 3.12+
- LangChain + LangChain-Community + LangChain-OpenAI
- FastAPI + Uvicorn（Web API）
- SQLite（持久化）
- Pydantic（数据验证）
- uv（包管理）

## 项目结构
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

## 核心设计
- Agent 类型：ReAct Agent (create_react_agent)
- Memory：SQLite 持久化 + ConversationBufferMemory
- Tools：order_lookup, refund_policy_check, return_process_guide, human_handoff
- 会话标识：session_id（用户手机号或 UUID）

## 代码规范
- 类型注解必须完整
- 使用 Google 风格 docstring
- 4 空格缩进
- 不使用通配符 import
