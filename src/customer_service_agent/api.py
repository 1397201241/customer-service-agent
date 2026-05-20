"""FastAPI web service for the customer service agent."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from customer_service_agent.agent import chat
from customer_service_agent.memory.checkpointer import get_checkpointer
from customer_service_agent.models.schemas import ChatRequest, ChatResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield


app = FastAPI(
    title="电商售后客服 Agent API",
    description="基于 LangGraph ReAct Agent 的电商售后客服系统",
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
    result = await asyncio.to_thread(
        chat,
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
    checkpointer = get_checkpointer()
    config = {"configurable": {"thread_id": session_id}}
    state = await asyncio.to_thread(checkpointer.get, config)

    messages: list[dict[str, str]] = []
    if state and "channel_values" in state:
        for msg in state["channel_values"].get("messages", []):
            messages.append(
                {
                    "type": getattr(msg, "type", "unknown"),
                    "content": _stringify(getattr(msg, "content", msg)),
                }
            )

    return JSONResponse({"session_id": session_id, "messages": messages})


def _stringify(content: object) -> str:
    """Render message content as a plain string for JSON responses."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        ]
        return "\n".join(p for p in parts if p) or str(content)
    return str(content)
