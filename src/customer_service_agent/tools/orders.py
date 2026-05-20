"""Order query tool with mock data."""

from datetime import datetime, timedelta

from langchain.tools import tool

from customer_service_agent.models.schemas import Order, OrderItem, OrderStatus


_MOCK_ORDERS: dict[str, Order] = {
    "ORD001": Order(
        order_id="ORD001",
        customer_phone="13800138000",
        status=OrderStatus.DELIVERED,
        items=[
            OrderItem(
                product_id="SKU1001",
                product_name="无线蓝牙耳机 Pro",
                quantity=1,
                unit_price=299.0,
                subtotal=299.0,
            ),
        ],
        total_amount=299.0,
        created_at=datetime.now() - timedelta(days=10),
        paid_at=datetime.now() - timedelta(days=10),
        shipped_at=datetime.now() - timedelta(days=8),
        delivered_at=datetime.now() - timedelta(days=5),
        shipping_address="北京市朝阳区XX街道1号楼",
        tracking_number="SF1234567890",
    ),
    "ORD002": Order(
        order_id="ORD002",
        customer_phone="13800138001",
        status=OrderStatus.SHIPPED,
        items=[
            OrderItem(
                product_id="SKU2001",
                product_name="智能手环 V3",
                quantity=2,
                unit_price=199.0,
                subtotal=398.0,
            ),
            OrderItem(
                product_id="SKU2002",
                product_name="充电底座",
                quantity=1,
                unit_price=49.0,
                subtotal=49.0,
            ),
        ],
        total_amount=447.0,
        created_at=datetime.now() - timedelta(days=5),
        paid_at=datetime.now() - timedelta(days=5),
        shipped_at=datetime.now() - timedelta(days=2),
        delivered_at=None,
        shipping_address="上海市浦东新区XX路2号",
        tracking_number="YT9876543210",
    ),
    "ORD003": Order(
        order_id="ORD003",
        customer_phone="13800138000",
        status=OrderStatus.REFUNDING,
        items=[
            OrderItem(
                product_id="SKU3001",
                product_name="便携充电宝 20000mAh",
                quantity=1,
                unit_price=159.0,
                subtotal=159.0,
            ),
        ],
        total_amount=159.0,
        created_at=datetime.now() - timedelta(days=20),
        paid_at=datetime.now() - timedelta(days=20),
        shipped_at=datetime.now() - timedelta(days=18),
        delivered_at=datetime.now() - timedelta(days=15),
        shipping_address="北京市朝阳区XX街道1号楼",
        tracking_number="JD5555666677",
    ),
    "ORD004": Order(
        order_id="ORD004",
        customer_phone="13800138002",
        status=OrderStatus.CANCELLED,
        items=[
            OrderItem(
                product_id="SKU4001",
                product_name="机械键盘 RGB",
                quantity=1,
                unit_price=499.0,
                subtotal=499.0,
            ),
        ],
        total_amount=499.0,
        created_at=datetime.now() - timedelta(days=30),
        paid_at=None,
        shipped_at=None,
        delivered_at=None,
        shipping_address="广州市天河区XX大道3号",
        tracking_number=None,
    ),
    "ORD005": Order(
        order_id="ORD005",
        customer_phone="13800138003",
        status=OrderStatus.COMPLETED,
        items=[
            OrderItem(
                product_id="SKU5001",
                product_name="4K 显示器 27寸",
                quantity=1,
                unit_price=1999.0,
                subtotal=1999.0,
            ),
        ],
        total_amount=1999.0,
        created_at=datetime.now() - timedelta(days=60),
        paid_at=datetime.now() - timedelta(days=60),
        shipped_at=datetime.now() - timedelta(days=58),
        delivered_at=datetime.now() - timedelta(days=55),
        shipping_address="深圳市南山区XX路4号",
        tracking_number="SF1122334455",
    ),
}

_ORDERS_BY_PHONE: dict[str, list[str]] = {
    "13800138000": ["ORD001", "ORD003"],
    "13800138001": ["ORD002"],
    "13800138002": ["ORD004"],
    "13800138003": ["ORD005"],
}


@tool
def order_lookup(order_id: str | None = None, customer_phone: str | None = None) -> str:
    """Query order information by order ID or customer phone number.

    Look up order details including status, items, amounts, and logistics.
    Provide at least one of order_id or customer_phone.

    Args:
        order_id: The unique order identifier (e.g., ORD001).
        customer_phone: The customer's registered phone number.

    Returns:
        Formatted order information or error message.
    """
    if not order_id and not customer_phone:
        return "请提供订单号或手机号码进行查询。"

    if order_id:
        order = _MOCK_ORDERS.get(order_id.upper())
        if order:
            return _format_order(order)
        if not customer_phone:
            return f"未找到订单 {order_id}，请确认订单号是否正确。"

    if customer_phone:
        order_ids = _ORDERS_BY_PHONE.get(customer_phone, [])
        if not order_ids:
            return f"未找到手机号 {customer_phone} 的订单记录。"

        results = []
        for oid in order_ids:
            order = _MOCK_ORDERS.get(oid)
            if order:
                results.append(_format_order(order))
        return "\n---\n".join(results) if results else "未找到相关订单。"

    return "查询失败，请稍后重试。"


def _format_order(order: Order) -> str:
    """Format an Order into a human-readable string.

    Args:
        order: Order instance.

    Returns:
        Formatted order string.
    """
    lines = [
        f"订单号: {order.order_id}",
        f"状态: {_status_label(order.status)}",
        f"金额: ¥{order.total_amount:.2f}",
        f"下单时间: {order.created_at.strftime('%Y-%m-%d %H:%M')}",
        f"收货地址: {order.shipping_address}",
        "商品列表:",
    ]
    for item in order.items:
        lines.append(
            f"  - {item.product_name} x{item.quantity} = ¥{item.subtotal:.2f}"
        )
    if order.paid_at:
        lines.append(f"付款时间: {order.paid_at.strftime('%Y-%m-%d %H:%M')}")
    if order.shipped_at:
        lines.append(f"发货时间: {order.shipped_at.strftime('%Y-%m-%d %H:%M')}")
    if order.delivered_at:
        lines.append(f"签收时间: {order.delivered_at.strftime('%Y-%m-%d %H:%M')}")
    if order.tracking_number:
        lines.append(f"物流单号: {order.tracking_number}")
    return "\n".join(lines)


def _status_label(status: OrderStatus) -> str:
    """Get Chinese label for order status.

    Args:
        status: OrderStatus enum value.

    Returns:
        Chinese status label.
    """
    labels = {
        OrderStatus.PENDING: "待付款",
        OrderStatus.PAID: "已付款",
        OrderStatus.SHIPPED: "已发货",
        OrderStatus.DELIVERED: "已签收",
        OrderStatus.COMPLETED: "已完成",
        OrderStatus.CANCELLED: "已取消",
        OrderStatus.REFUNDING: "退款中",
        OrderStatus.REFUNDED: "已退款",
    }
    return labels.get(status, status.value)
