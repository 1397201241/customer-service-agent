"""ReAct Agent core for the customer service agent using LangGraph."""

import os
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import create_react_agent

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


def create_agent(
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.3,
) -> ChatOpenAI:
    """Create the LLM for the agent.

    Args:
        model_name: OpenAI model name to use.
        temperature: Sampling temperature for the LLM.

    Returns:
        Configured ChatOpenAI instance.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
    )


async def chat(
    session_id: str,
    message: str,
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.3,
) -> dict[str, Any]:
    """Process a single chat message through the agent.

    Args:
        session_id: Unique session identifier.
        message: User message text.
        model_name: OpenAI model name to use.
        temperature: Sampling temperature for the LLM.

    Returns:
        Agent execution result dictionary with 'output' key.
    """
    llm = create_agent(model_name=model_name, temperature=temperature)
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
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.3,
) -> dict[str, Any]:
    """Synchronous wrapper for chat().

    Args:
        session_id: Unique session identifier.
        message: User message text.
        model_name: OpenAI model name to use.
        temperature: Sampling temperature for the LLM.

    Returns:
        Agent execution result dictionary with 'output' key.
    """
    import asyncio
    return asyncio.run(chat(
        session_id=session_id,
        message=message,
        model_name=model_name,
        temperature=temperature,
    ))
