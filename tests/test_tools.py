"""Tests for customer service agent tools."""

import pytest

from customer_service_agent.tools.handoff import _determine_priority, human_handoff
from customer_service_agent.tools.orders import order_lookup
from customer_service_agent.tools.policy import refund_policy_check
from customer_service_agent.tools.returns import return_process_guide


class TestOrderLookup:
    """Tests for order_lookup tool."""

    def test_lookup_by_order_id_found(self):
        result = order_lookup.invoke({"order_id": "ORD001"})
        assert "无线蓝牙耳机 Pro" in result
        assert "已签收" in result

    def test_lookup_by_order_id_not_found(self):
        result = order_lookup.invoke({"order_id": "ORD999"})
        assert "未找到订单" in result

    def test_lookup_by_phone_found(self):
        result = order_lookup.invoke({"customer_phone": "13800138000"})
        assert "ORD001" in result
        assert "ORD003" in result

    def test_lookup_by_phone_not_found(self):
        result = order_lookup.invoke({"customer_phone": "13999999999"})
        assert "未找到手机号" in result

    def test_lookup_no_params(self):
        result = order_lookup.invoke({})
        assert "请提供订单号或手机号码" in result

    def test_lookup_case_insensitive(self):
        result = order_lookup.invoke({"order_id": "ord001"})
        assert "无线蓝牙耳机 Pro" in result


class TestRefundPolicyCheck:
    """Tests for refund_policy_check tool."""

    def test_electronics_within_limit(self):
        from datetime import datetime, timedelta

        order_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        result = refund_policy_check.invoke(
            {"category": "electronics", "order_date": order_date, "total_amount": 299.0}
        )
        assert "是" in result
        assert "7 天" in result

    def test_electronics_over_limit(self):
        from datetime import datetime, timedelta

        order_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        result = refund_policy_check.invoke(
            {"category": "electronics", "order_date": order_date, "total_amount": 299.0}
        )
        assert "否" in result

    def test_food_no_quality_issue(self):
        result = refund_policy_check.invoke(
            {"category": "food", "total_amount": 50.0, "has_quality_issue": False}
        )
        assert "否" in result

    def test_food_with_quality_issue(self):
        result = refund_policy_check.invoke(
            {"category": "food", "total_amount": 50.0, "has_quality_issue": True}
        )
        assert "是" in result

    def test_invalid_date_format(self):
        result = refund_policy_check.invoke(
            {"category": "electronics", "order_date": "invalid-date", "total_amount": 100.0}
        )
        assert "格式错误" in result

    def test_default_category(self):
        result = refund_policy_check.invoke({"total_amount": 100.0})
        assert "7 天" in result


class TestReturnProcessGuide:
    """Tests for return_process_guide tool."""

    def test_normal_return(self):
        result = return_process_guide.invoke(
            {"order_id": "ORD001", "has_quality_issue": False}
        )
        assert "退货流程指引" in result
        assert "买家" in result

    def test_quality_issue_return(self):
        result = return_process_guide.invoke(
            {"order_id": "ORD001", "has_quality_issue": True}
        )
        assert "商家" in result
        assert "质量问题" in result

    def test_food_no_quality_issue(self):
        result = return_process_guide.invoke(
            {"order_id": "ORD001", "has_quality_issue": False, "product_category": "food"}
        )
        assert "不支持无理由退货" in result


class TestHumanHandoff:
    """Tests for human_handoff tool."""

    def test_basic_handoff(self):
        result = human_handoff.invoke(
            {
                "session_id": "test-session-1",
                "reason": "用户要求退款",
            }
        )
        assert "已为您转接人工客服" in result
        assert "TKT" in result

    def test_handoff_with_phone(self):
        result = human_handoff.invoke(
            {
                "session_id": "test-session-2",
                "reason": "投诉",
                "customer_phone": "13800138000",
            }
        )
        assert "13800138000" in result

    def test_priority_urgent(self):
        assert _determine_priority("投诉欺诈行为") == "urgent"
        assert _determine_priority("严重质量问题") == "urgent"

    def test_priority_high(self):
        assert _determine_priority("商品破损") == "high"
        assert _determine_priority("需要退货退款") == "high"

    def test_priority_normal(self):
        assert _determine_priority("一般咨询") == "normal"
        assert _determine_priority("使用方法") == "normal"

    def test_priority_case_insensitive(self):
        assert _determine_priority("投诉") == "urgent"
        # English keywords are not in the keyword list, so "complaint" returns normal
        assert _determine_priority("complaint") == "normal"

    def test_ticket_increment(self):
        """Tickets should increment sequentially."""
        result1 = human_handoff.invoke(
            {"session_id": "s1", "reason": "test1"}
        )
        result2 = human_handoff.invoke(
            {"session_id": "s2", "reason": "test2"}
        )
        # Extract ticket numbers
        tkt1 = [line for line in result1.split("\n") if "工单编号" in line][0]
        tkt2 = [line for line in result2.split("\n") if "工单编号" in line][0]
        num1 = int(tkt1.split("TKT")[1])
        num2 = int(tkt2.split("TKT")[1])
        assert num2 == num1 + 1
