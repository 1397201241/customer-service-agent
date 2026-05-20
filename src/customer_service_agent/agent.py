"""ReAct Agent core for the customer service agent using LangGraph."""

from typing import Any

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import create_react_agent

from customer_service_agent.config import settings
from customer_service_agent.memory.sqlite_memory import get_checkpointer
from customer_service_agent.tools import ALL_TOOLS


SYSTEM_PROMPT = """你是一个专业的电商售后客服助手，名叫"售后小助手"。你的职责是帮助用户解决订单查询、退款政策咨询、退货流程指引等问题。

重要提示：
- 如果用户要查询订单，使用 order_lookup 工具
- 如果用户要咨询退款政策，使用 refund_policy_check 工具
- 如果用户要办理退货，使用 return_process_guide 工具
- 如果用户坚持要转人工或问题无法解决，使用 human_handoff 工具
- 回复用户时请使用中文，保持礼貌和专业
- 如果用户没有提供订单号或手机号，请礼貌地询问"""


def create_llm(
    model_name: str | None = None,
    temperature: float | None = None,
) -> ChatOpenAI:
    """Create the LLM based on configured provider.

    Supports OpenAI and MiniMax via OpenAI-compatible API.

    Args:
        model_name: Override model name. Defaults to provider's default model.
        temperature: Override temperature. Defaults to config value.

    Returns:
        Configured ChatOpenAI instance.
    """
    provider = settings.llm_provider.lower()
    temp = temperature if temperature is not None else settings.temperature

    if provider == "minimax":
        api_key = settings.minimax_api_key
        base_url = settings.minimax_base_url
        model = model_name or settings.minimax_model
        if not api_key:
            raise ValueError(
                "MiniMax API key not set. Please set MINIMAX_API_KEY in .env"
            )
    else:
        api_key = settings.openai_api_key
        base_url = settings.openai_base_url
        model = model_name or settings.openai_model
        if not api_key:
            raise ValueError(
                "OpenAI API key not set. Please set OPENAI_API_KEY in .env"
            )

    return ChatOpenAI(
        model=model,
        temperature=temp,
        api_key=api_key,
        base_url=base_url,
    )


async def chat(
    session_id: str,
    message: str,
    model_name: str | None = None,
    temperature: float | None = None,
) -> dict[str, Any]:
    """Process a single chat message through the agent.

    Args:
        session_id: Unique session identifier.
        message: User message text.
        model_name: Override model name.
        temperature: Override temperature.

    Returns:
        Agent execution result dictionary with 'output' key.
    """
    llm = create_llm(model_name=model_name, temperature=temperature)
    checkpointer = await get_checkpointer()

    graph = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        state_modifier=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )

    config = {"configurable": {"thread_id": session_id}}
    result = await graph.ainvoke(
        {"messages": [HumanMessage(content=message)]},
        config=config,
    )

    last_message = result["messages"][-1]
    return {"output": last_message.content}


def chat_sync(
    session_id: str,
    message: str,
    model_name: str | None = None,
    temperature: float | None = None,
) -> dict[str, Any]:
    """Synchronous wrapper for chat().

    Args:
        session_id: Unique session identifier.
        message: User message text.
        model_name: Override model name.
        temperature: Override temperature.

    Returns:
        Agent execution result dictionary with 'output' key.
    """
    import asyncio

    return asyncio.run(
        chat(
            session_id=session_id,
            message=message,
            model_name=model_name,
            temperature=temperature,
        )
    )
