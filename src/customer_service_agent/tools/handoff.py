"""Human handoff tool for escalating to human agents."""

from datetime import datetime

from langchain.tools import tool

from customer_service_agent.models.schemas import HumanHandoffRequest


_HANDOFF_TICKETS: list[HumanHandoffRequest] = []


@tool
def human_handoff(
    session_id: str,
    reason: str,
    customer_phone: str | None = None,
    context_summary: str = "",
) -> str:
    """Escalate the current conversation to a human customer service agent.

    Use this when the user's issue cannot be resolved by the AI agent,
    or when the user explicitly requests to speak with a human.

    Args:
        session_id: Current conversation session identifier.
        reason: Reason for escalation.
        customer_phone: Customer's phone number if available.
        context_summary: Summary of the conversation context.

    Returns:
        Confirmation message with ticket information.
    """
    ticket = HumanHandoffRequest(
        session_id=session_id,
        reason=reason,
        customer_phone=customer_phone,
        context_summary=context_summary or f"用户请求人工客服: {reason}",
        priority=_determine_priority(reason),
    )
    _HANDOFF_TICKETS.append(ticket)
    ticket_number = f"TKT{len(_HANDOFF_TICKETS):04d}"

    lines = [
        "已为您转接人工客服。",
        f"工单编号: {ticket_number}",
        f"会话ID: {ticket.session_id}",
        f"转接原因: {ticket.reason}",
    ]
    if ticket.customer_phone:
        lines.append(f"联系电话: {ticket.customer_phone}")
    lines.append(f"提交时间: {ticket.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("人工客服将在工作时间内尽快与您联系，请保持电话畅通。")

    return "\n".join(lines)


def _determine_priority(reason: str) -> str:
    """Determine ticket priority based on reason keywords.

    Args:
        reason: Handoff reason text.

    Returns:
        Priority level string.
    """
    urgent_keywords = ["投诉", " urgent", "严重", "欺诈", "诈骗", "人身安全"]
    high_keywords = ["质量问题", "损坏", "破损", "漏发", "错发", "退货", "退款"]

    lower = reason.lower()
    for kw in urgent_keywords:
        if kw in lower or kw in reason:
            return "urgent"
    for kw in high_keywords:
        if kw in lower or kw in reason:
            return "high"
    return "normal"
