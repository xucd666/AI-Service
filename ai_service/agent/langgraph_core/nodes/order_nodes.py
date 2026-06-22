import json
import re
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from agent.langgraph_core.answer_model import generate_customer_answer
from agent.langgraph_core.answer_prompts import ORDER_ANSWER_SYSTEM_PROMPT
from agent.langgraph_core.model import chat_model
from tools.order_tool import get_order_status

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


def extract_order_id_node(state):
    """
    优先使用 Router 已经提取出的 order_id；
    如果没有，再用 LangChain ChatModel 提取；
    如果 LLM 失败，再用正则兜底。
    """
    logger.info("进入 extract_order_id_node")

    if state.get("order_id") not in [None, ""]:
        logger.info(f"使用 Router 已提取的订单号: {state.get('order_id')}")
        return state

    user_input = state.get("user_input", "")

    logger.info("Router 未提取到订单号，开始调用 LLM 提取订单号")
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
        logger.info("LLM 未提取到订单号，开始使用正则兜底")
        match = re.search(r"\d+", user_input)
        order_id = match.group() if match else None

    state["order_id"] = order_id

    logger.info(f"最终提取到的订单号: {order_id}")

    return state

def query_order_node(state):
    logger.info("进入 query_order_node")

    order_id = state.get("order_id")

    if not order_id:
        logger.info("订单号缺失，终止订单查询")
        state["final_answer"] = "请提供订单号，我才能帮您查询订单状态。"
        return state

    logger.info(f"开始查询订单状态: order_id={order_id}")

    result = get_order_status(order_id)

    if not result.get("success"):
        logger.warning(f"订单查询失败: order_id={order_id}, result={result}")
        state["final_answer"] = "订单查询失败，请稍后再试。"
        return state

    state["order_info"] = result.get("data")

    logger.info(f"订单查询成功: order_id={order_id}, order_info={state.get('order_info')}")

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
