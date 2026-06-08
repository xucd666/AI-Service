import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from agent.langgraph_core.answer_model import generate_customer_answer
from agent.langgraph_core.answer_prompts import ORDER_ANSWER_SYSTEM_PROMPT
from agent.langgraph_core.model import chat_model
from tools.order_tool import get_order_status



def safe_parse_order_result(content: str) -> dict:
    try:
        content = content.strip()

        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        data = json.loads(content)

        return {
            "order_id": data.get("order_id")
        }

    except Exception:
        return {
            "order_id": None
        }


def extract_order_id_node(state):
    """
    优先使用 Router 已经提取出的 order_id；
    如果没有，再用 LangChain ChatModel 提取；
    如果 LLM 失败，再用正则兜底。
    """

    if state.get("order_id") not in [None, ""]:
        return state

    user_input = state.get("user_input", "")

    messages = [
        SystemMessage(content="""
        你是订单号提取助手。
        
        你的任务：
        从用户输入中提取订单号。
        
        要求：
        1. 只输出 JSON
        2. 不要输出解释
        3. 如果用户没有提供订单号，order_id 返回 null
        
        JSON 格式：
        {
          "order_id": "订单号或null"
        }
    """),
        HumanMessage(content=user_input)
    ]

    response = chat_model.invoke(messages)

    data = safe_parse_order_result(response.content)

    order_id = data.get("order_id")

    if not order_id:
        match = re.search(r"\d+", user_input)
        order_id = match.group() if match else None

    state["order_id"] = order_id

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

    try:
        state["final_answer"] = generate_customer_answer(
            ORDER_ANSWER_SYSTEM_PROMPT,
            state.get("user_input", ""),
            {
                "order_id": order_id,
                "order_info": order_info,
            },
        )
        return state
    except Exception:
        if isinstance(order_info, str):
            state["final_answer"] = f"您的订单 {order_id} 当前状态是：{order_info}"
            return state

        state["final_answer"] = (
            f"您的订单 {order_info.get('order_id', order_id)} 当前状态是："
            f"{order_info.get('status', '未知')}"
        )

    return state
