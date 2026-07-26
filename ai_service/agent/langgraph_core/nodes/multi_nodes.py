import logging

from agent.langgraph_core.answer_model import generate_customer_answer
from agent.langgraph_core.answer_prompts import MULTI_ANSWER_SYSTEM_PROMPT
from tools.dish_tool import get_low_fat_dishes


logger = logging.getLogger("MultiNodes")


def route_after_order_query(state):
    """
    订单查询之后的路由判断。

    如果订单号缺失、订单查询失败，query_order_node 会提前写入 final_answer。
    这时 multi_workflow 不应该继续查菜品，直接结束即可。
    """

    if state.get("final_answer"):
        logger.info("订单阶段已生成 final_answer，MultiWorkflow 直接结束，不继续查询菜品")
        return "end"

    logger.info("订单查询成功，继续进入减脂餐查询")
    return "query_dishes_for_multi"


def query_dishes_for_multi_node(state):
    """
    多 Tool 场景下查询减脂餐。
    """

    logger.info("进入 query_dishes_for_multi_node，开始查询减脂餐")

    result = get_low_fat_dishes()

    if not result.get("success"):
        logger.warning(f"MultiWorkflow 减脂餐查询失败: result={result}")
        state["dishes"] = []
        state["best_dish"] = None
        state["dish_query_error"] = "减脂餐查询失败"
        return state

    state["dishes"] = result.get("data", [])

    logger.info(f"MultiWorkflow 减脂餐查询成功，数量={len(state.get('dishes') or [])}")

    return state


def answer_multi_node(state):
    """
    综合回答节点：
    同时使用订单信息 + 菜品推荐信息，生成最终回复。
    """

    logger.info("进入 answer_multi_node")

    if state.get("final_answer"):
        logger.info("已有 final_answer，跳过综合回答生成")
        return state

    order_id = state.get("order_id")
    order_info = state.get("order_info")
    best_dish = state.get("best_dish")
    dishes = state.get("dishes") or []

    if not order_info:
        logger.info("order_info 为空，无法生成综合回答")
        state["final_answer"] = "没有查询到该订单信息。"
        return state

    try:
        logger.info("开始调用 LLM 生成多 Tool 综合回答")

        state["final_answer"] = generate_customer_answer(
            MULTI_ANSWER_SYSTEM_PROMPT,
            state.get("user_input", ""),
            {
                "order_id": order_id,
                "order_info": order_info,
                "best_dish": best_dish,
                "dishes": dishes,
            },
            state.get("messages", []),
        )

        logger.info(f"多 Tool 综合回答生成成功: {state.get('final_answer')}")
        return state

    except Exception as e:
        logger.warning(f"多 Tool 综合回答生成失败，使用兜底回答: {e}")

    order_status = "未知"

    if isinstance(order_info, str):
        order_status = order_info
    elif isinstance(order_info, dict):
        order_status = order_info.get("status", "未知")

    if best_dish:
        name = best_dish.get("name", "未知菜品")
        calories = best_dish.get("calories", "热量未知")

        state["final_answer"] = (
            f"您的订单 {order_id} 当前状态是：{order_status}。\n"
            f"另外为您推荐当前热量较低的减脂餐：{name}，约 {calories} 大卡。"
        )
    else:
        state["final_answer"] = (
            f"您的订单 {order_id} 当前状态是：{order_status}。\n"
            f"不过当前没有查询到合适的减脂餐推荐。"
        )

    logger.info(f"多 Tool 综合兜底回答: {state.get('final_answer')}")

    return state