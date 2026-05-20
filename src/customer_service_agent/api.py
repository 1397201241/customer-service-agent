"""FastAPI web service for the customer service agent."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from customer_service_agent.agent import chat
from customer_service_agent.models.schemas import ChatRequest, ChatResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield


app = FastAPI(
    title="电商售后客服 Agent API",
    description="基于 LangChain ReAct Agent 的电商售后客服系统",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Status dictionary.
    """
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Process a chat message and return the agent's response.

    Args:
        request: Chat request with session_id and message.

    Returns:
        Chat response with agent's reply.
    """
    result = await chat(
        session_id=request.session_id,
        message=request.message,
    )
    return ChatResponse(
        session_id=request.session_id,
        response=result.get("output", "抱歉，处理请求时出现问题，请稍后重试。"),
    )


@app.get("/chat/{session_id}")
async def get_chat_history(session_id: str) -> JSONResponse:
    """Get chat history for a session.

    Args:
        session_id: Conversation session identifier.

    Returns:
        JSON response with chat messages.
    """
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    from customer_service_agent.memory.sqlite_memory import DEFAULT_DB_PATH

    saver = AsyncSqliteSaver.from_conn_string(str(DEFAULT_DB_PATH))
    config = {"configurable": {"thread_id": session_id}}

    messages = []
    async with saver:
        state = await saver.aget(config)
        if state and "channel_values" in state:
            msgs = state["channel_values"].get("messages", [])
            for msg in msgs:
                messages.append({
                    "type": msg.type if hasattr(msg, "type") else "unknown",
                    "content": msg.content if hasattr(msg, "content") else str(msg),
                })

    return JSONResponse({"session_id": session_id, "messages": messages})
