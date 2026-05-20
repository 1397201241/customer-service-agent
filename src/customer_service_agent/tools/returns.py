"""Return process guidance tool."""

from langchain.tools import tool

from customer_service_agent.models.schemas import ReturnGuideResult


@tool
def return_process_guide(
    order_id: str,
    has_quality_issue: bool = False,
    product_category: str = "default",
) -> str:
    """Provide return process guidance for an order.

    Args:
        order_id: The order identifier.
        has_quality_issue: Whether the return is due to quality issues.
        product_category: Product category for specific instructions.

    Returns:
        Step-by-step return instructions.
    """
    can_return = True
    steps: list[str] = []
    return_address = "上海市嘉定区退货处理中心，XX路99号"
    shipping_fee_payer = "商家" if has_quality_issue else "买家"
    estimated_refund_time = "3-7个工作日"
    notes: str | None = None

    steps = [
        "1. 在APP中提交退货申请，选择退货原因并上传商品照片。",
        "2. 等待商家审核（通常1个工作日内）。",
        "3. 审核通过后，将商品妥善包装并附上订单小票。",
        f"4. 寄回地址: {return_address}",
        f"5. 退货运费由{shipping_fee_payer}承担。",
        "6. 商家收到退货并验收后，将尽快处理退款。",
        f"7. 退款预计到账时间: {estimated_refund_time}。",
    ]

    if has_quality_issue:
        notes = "因质量问题退货，请保留商品照片、视频等凭证。运费由商家承担，退款将包含原订单金额及退货运费。"
    else:
        notes = "无理由退货需保证商品完好、配件齐全、不影响二次销售。退货运费由买家自行承担。"

    if product_category == "food":
        can_return = has_quality_issue
        if not has_quality_issue:
            steps = ["食品类不支持无理由退货。如有质量问题，请联系客服并提供相关凭证。"]
            return_address = None
            notes = None

    result = ReturnGuideResult(
        can_return=can_return,
        steps=steps,
        return_address=return_address,
        shipping_fee_payer=shipping_fee_payer,
        estimated_refund_time=estimated_refund_time,
        notes=notes,
    )

    lines = ["退货流程指引:", f"是否可退货: {'是' if result.can_return else '否'}"]
    lines.extend(result.steps)
    if result.notes:
        lines.append(f"\n备注: {result.notes}")

    return "\n".join(lines)
