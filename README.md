# 电商售后客服 Agent

基于 LangChain + LangGraph 的电商售后客服 Agent，支持命令行交互和 Web API 两种模式，对话历史持久化到 SQLite。

## 功能特性

- **ReAct Agent**: 基于 LangGraph 的 `create_react_agent`，支持多步推理和工具调用
- **4 个核心 Tools**:
  - `order_lookup`: 订单查询（支持订单号/手机号）
  - `refund_policy_check`: 退款政策查询
  - `return_process_guide`: 退货流程指引
  - `human_handoff`: 转人工客服
- **SQLite 持久化**: 对话历史自动保存到 SQLite
- **双模式**: CLI 命令行 + FastAPI Web 服务

## 项目结构

```
customer_service_agent/
├── src/customer_service_agent/
│   ├── agent.py          # ReAct Agent 核心 (LangGraph)
│   ├── cli.py            # 命令行交互入口
│   ├── api.py            # FastAPI Web 服务
│   ├── tools/            # 工具定义
│   ├── memory/           # SQLite 记忆管理
│   └── models/           # Pydantic 数据模型
├── data/                 # SQLite 数据库目录
├── pyproject.toml
└── .env.example
```

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY
```

### 2. 命令行交互

```bash
# 使用 uv 运行
uv run customer-service-agent

# 或指定手机号
uv run customer-service-agent --phone 13800138000

# 指定模型
uv run customer-service-agent --model gpt-4o
```

### 3. Web API 服务

```bash
uv run uvicorn customer_service_agent.api:app --reload
```

API 端点：
- `GET /health` - 健康检查
- `POST /chat` - 发送消息
- `GET /chat/{session_id}` - 查询对话历史

示例请求：
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-001", "message": "查询我的订单"}'
```

## 技术栈

- Python 3.12+
- LangChain + LangGraph
- ChatOpenAI
- FastAPI + Uvicorn
- SQLite (持久化)
- Pydantic
- uv (包管理)
