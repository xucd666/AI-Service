import re

from tools.order_tool import get_order_status


def extract_order_id_node(state):
    """
    从用户输入中提取订单编号
    """
    user_input = state.get("user_input","")

    # 尝试匹配订单编号
    match = re.search(r'\d+', user_input)

    state["order_id"] = match.group() if match else None

    return state

def query_order_node(state):
    order_id = state.get("order_id")

    if not order_id:
        state["final_answer"] = "请提供订单号，我才能帮您查询订单状态。"
        return state

    order_info = get_order_status(order_id)
    state["order_info"] = order_info

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