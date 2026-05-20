"""Pydantic data models for the customer service agent."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    """Order status enumeration."""

    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDING = "refunding"
    REFUNDED = "refunded"


class RefundReason(str, Enum):
    """Refund reason enumeration."""

    QUALITY_ISSUE = "quality_issue"
    WRONG_ITEM = "wrong_item"
    NOT_AS_DESC = "not_as_described"
    DAMAGED = "damaged_in_transit"
    CHANGED_MIND = "changed_mind"
    OTHER = "other"


class OrderItem(BaseModel):
    """Model for an order line item."""

    product_id: str = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    unit_price: float = Field(..., ge=0, description="Price per unit")
    subtotal: float = Field(..., ge=0, description="Line item subtotal")


class Order(BaseModel):
    """Model for an e-commerce order."""

    order_id: str = Field(..., description="Unique order identifier")
    customer_phone: str = Field(..., description="Customer phone number")
    status: OrderStatus = Field(..., description="Current order status")
    items: list[OrderItem] = Field(default_factory=list, description="Order items")
    total_amount: float = Field(..., ge=0, description="Order total amount")
    created_at: datetime = Field(..., description="Order creation time")
    paid_at: datetime | None = Field(None, description="Payment time")
    shipped_at: datetime | None = Field(None, description="Shipment time")
    delivered_at: datetime | None = Field(None, description="Delivery time")
    shipping_address: str = Field(..., description="Shipping address")
    tracking_number: str | None = Field(None, description="Logistics tracking number")


class RefundPolicyResult(BaseModel):
    """Model for refund policy check result."""

    eligible: bool = Field(..., description="Whether refund is eligible")
    max_refund_amount: float = Field(..., ge=0, description="Maximum refundable amount")
    time_limit_days: int = Field(..., description="Refund window in days")
    requires_return: bool = Field(..., description="Whether item return is required")
    policy_notes: str = Field(..., description="Policy explanation")


class ReturnGuideResult(BaseModel):
    """Model for return process guidance."""

    can_return: bool = Field(..., description="Whether return is possible")
    steps: list[str] = Field(default_factory=list, description="Return steps")
    return_address: str | None = Field(None, description="Return shipping address")
    shipping_fee_payer: str = Field("buyer", description="Who pays return shipping")
    estimated_refund_time: str = Field(..., description="Estimated refund processing time")
    notes: str | None = Field(None, description="Additional notes")


class HumanHandoffRequest(BaseModel):
    """Model for human handoff request."""

    session_id: str = Field(..., description="Session identifier")
    reason: str = Field(..., description="Reason for handoff")
    customer_phone: str | None = Field(None, description="Customer phone number")
    context_summary: str = Field(..., description="Conversation context summary")
    priority: str = Field("normal", description="Ticket priority")
    created_at: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Model for chat API request."""

    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., min_length=1, description="User message")
    customer_phone: str | None = Field(None, description="Customer phone number")


class ChatResponse(BaseModel):
    """Model for chat API response."""

    session_id: str = Field(..., description="Session identifier")
    response: str = Field(..., description="Agent response")
    tool_used: str | None = Field(None, description="Tool invoked during processing")
    timestamp: datetime = Field(default_factory=datetime.now)
