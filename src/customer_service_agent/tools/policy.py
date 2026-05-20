"""Refund policy check tool."""

from datetime import datetime, timedelta

from langchain.tools import tool

from customer_service_agent.models.schemas import RefundPolicyResult


_REFUND_POLICIES: dict[str, dict] = {
    "electronics": {
        "time_limit_days": 7,
        "requires_return": True,
        "max_rate": 1.0,
        "notes": "电子产品支持7天无理由退货，需保证商品完好、配件齐全、不影响二次销售。",
    },
    "clothing": {
        "time_limit_days": 15,
        "requires_return": True,
        "max_rate": 1.0,
        "notes": "服装类支持15天无理由退货，需保留吊牌、未穿着、未洗涤。",
    },
    "food": {
        "time_limit_days": 0,
        "requires_return": False,
        "max_rate": 0.0,
        "notes": "食品类不支持无理由退货。若存在质量问题，可联系客服协商。",
    },
    "default": {
        "time_limit_days": 7,
        "requires_return": True,
        "max_rate": 1.0,
        "notes": "支持7天无理由退货，需保证商品完好、配件齐全、不影响二次销售。",
    },
}


@tool
def refund_policy_check(
    category: str = "default",
    order_date: str | None = None,
    total_amount: float = 0.0,
    has_quality_issue: bool = False,
) -> str:
    """Check refund policy eligibility for a product or order.

    Args:
        category: Product category (electronics, clothing, food, default).
        order_date: Order date in YYYY-MM-DD format.
        total_amount: Total order amount.
        has_quality_issue: Whether there is a confirmed quality issue.

    Returns:
        Formatted refund policy result.
    """
    policy = _REFUND_POLICIES.get(category, _REFUND_POLICIES["default"])
    time_limit = policy["time_limit_days"]
    requires_return = policy["requires_return"]
    max_rate = policy["max_rate"]
    notes = policy["notes"]

    eligible = True
    extra_notes = ""

    if order_date:
        try:
            order_dt = datetime.strptime(order_date, "%Y-%m-%d")
            days_elapsed = (datetime.now() - order_dt).days
            if days_elapsed > time_limit and not has_quality_issue:
                eligible = False
                extra_notes = f"订单已超{time_limit}天退货期限，无理由退货不再支持。如确有质量问题，请提供相关凭证。"
            else:
                remaining = max(0, time_limit - days_elapsed)
                extra_notes = f"距离退货期限还有 {remaining} 天。"
        except ValueError:
            extra_notes = "订单日期格式错误，无法判断时效。"

    if has_quality_issue:
        eligible = True
        requires_return = True
        extra_notes = "确认存在质量问题，可申请退货退款，运费由商家承担。"

    if category == "food":
        eligible = has_quality_issue

    max_refund = total_amount * max_rate

    result = RefundPolicyResult(
        eligible=eligible,
        max_refund_amount=max_refund,
        time_limit_days=time_limit,
        requires_return=requires_return,
        policy_notes=f"{notes} {extra_notes}".strip(),
    )

    lines = [
        "退款政策查询结果:",
        f"是否可退: {'是' if result.eligible else '否'}",
        f"最高退款金额: ¥{result.max_refund_amount:.2f}",
        f"退货期限: {result.time_limit_days} 天",
        f"是否需要退货: {'是' if result.requires_return else '否'}",
        f"政策说明: {result.policy_notes}",
    ]
    return "\n".join(lines)
