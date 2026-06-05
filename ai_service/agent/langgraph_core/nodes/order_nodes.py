import re

from tools.order_tool import get_order_status


def extract_order_id_node(state):
    """
    优先使用 Router 已经提取出的 order_id；
    如果 Router 没提取到，再从用户输入中兜底正则提取。
    """
    if state.get("order_id"):
        return state

    user_input = state.get("user_input", "")
    match = re.search(r'\d+', user_input)

    state["order_id"] = match.group() if match else None

    return state

def query_order_node(state):
    order_id = state.get("order_id")

    if not order_id:
        state["final_answer"] = "请提供订单号，我才能帮您查询订单状态。"
        return state

    result = get_order_status(order_id)

    if not result.get("success"):
        state["final_answer"] = "订单查询失败，请稍后再试。"
        return state

    state["order_info"] = result.get("data")

    return state

def answer_order_node(state):
    if state.get("final_answer"):
        return state

    order_info = state.get("order_info")
    order_id = state.get("order_id")

    if not order_info:
        state["final_answer"] = "没有查询到该订单信息。"
        return state

    if isinstance(order_info, str):
        state["final_answer"] = f"您的订单 {order_id} 当前状态是：{order_info}"
        return state

    state["final_answer"] = (
        f"您的订单 {order_info.get('order_id', order_id)} 当前状态是："
        f"{order_info.get('status', '未知')}"
    )

    return state