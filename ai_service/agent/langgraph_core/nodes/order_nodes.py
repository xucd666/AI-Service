import json
import re
import logging

from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage

from agent.langgraph_core.answer_model import generate_customer_answer
from agent.langgraph_core.answer_prompts import ORDER_ANSWER_SYSTEM_PROMPT
from agent.langgraph_core.model import chat_model
from tools.order_tool import get_order_info

logger = logging.getLogger("OrderNodes")

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

    except Exception as e:
        logger.warning(f"订单号 JSON解析失败: {e}, 原始内容: {content}")
        return {
            "order_id": None
        }

ORDER_ID_PATTERN = re.compile(r"\b\d{10,20}\b")

def extract_order_id_from_text(text:str) -> str | None:
    match = ORDER_ID_PATTERN.search(text or "")
    if match:
        return match.group()
    return None

def extract_order_id_from_messages(messages:list[BaseMessage]) -> str | None:
    for messages in reversed(messages):
        content = str(messages.content)
        order_id = extract_order_id_from_text(content)
        if order_id:
            return order_id

    return None


def extract_order_id_node(state):
    logger.info("进入 extract_order_id_node")
    order_id = state.get("order_id")

    if order_id not in [None, ""]:
        logger.info(f"使用 Router 已提取的订单号: {order_id}")
        return state

    user_input = state.get("user_input", "")
    order_id = extract_order_id_from_text(user_input)

    if order_id:
        state["order_id"] = order_id
        logger.info(f"从用户输入中提取到订单号: {order_id}")
        return state

    conversation_messages = state.get("messages", [])
    order_id = extract_order_id_from_messages(conversation_messages)
    if order_id:
        state["order_id"] = order_id
        logger.info(f"从会话消息中提取到订单号: {order_id}")
        return state

    logger.info("当前输入和历史消息中都没有提取到订单号")
    state["order_id"] = None
    return state

def query_order_node(state):
    logger.info("进入 query_order_node")

    order_id = state.get("order_id")

    if not order_id:
        logger.info("订单号缺失，终止订单查询")
        state["final_answer"] = "请提供订单号，我才能帮您查询订单状态。"
        return state

    logger.info(f"开始查询订单状态: order_id={order_id}")

    # 关键：order_id 变量里保存的是用户输入的订单号，本质上是 order_number
    result = get_order_info(order_id)

    if not result.get("success"):
        logger.warning(f"订单查询失败: order_id={order_id}, result={result}")
        state["final_answer"] = "订单查询失败，请稍后再试。"
        return state

    state["order_info"] = result.get("data")

    logger.info(f"调用订单接口成功 order_id={order_id}")

    return state


def answer_order_node(state):
    logger.info("进入 answer_order_node")

    if state.get("final_answer"):
        logger.info("已有 final_answer，跳过订单回答生成")
        return state

    order_info = state.get("order_info")
    order_id = state.get("order_id")

    if not order_info:
        logger.info("order_info 为空，返回未查询到订单信息")
        state["final_answer"] = "没有查询到该订单信息。"
        return state

    try:
        logger.info("开始调用 LLM 生成订单回答")

        state["final_answer"] = generate_customer_answer(
            ORDER_ANSWER_SYSTEM_PROMPT,
            state.get("user_input", ""),
            {
                "order_id": order_id,
                "order_info": order_info,
            },
            state.get("messages", []),
        )

        logger.info(f"订单回答生成成功: {state.get('final_answer')}")
        return state

    except Exception as e:
        logger.warning(f"订单回答生成失败，使用兜底回答: {e}")

        if isinstance(order_info, str):
            state["final_answer"] = f"您的订单 {order_id} 当前状态是：{order_info}"
            return state

        state["final_answer"] = (
            f"您的订单 {order_info.get('order_id', order_id)} 当前状态是："
            f"{order_info.get('status', '未知')}"
        )

    logger.info(f"订单兜底回答: {state.get('final_answer')}")

    return state
