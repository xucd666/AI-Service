import logging

from agent.langgraph_core.answer_model import generate_customer_answer
from agent.langgraph_core.answer_prompts import (
    DISH_BEST_ANSWER_SYSTEM_PROMPT,
    DISH_LIST_ANSWER_SYSTEM_PROMPT,
)
from tools.dish_tool import get_low_fat_dishes

logger = logging.getLogger("DishNodes")

LOWEST_CALORIE_KEYWORDS = (
    "最低",
    "最少",
    "最小",
    "低卡",
    "热量低",
    "热量最低",
    "卡路里最低",
    "卡路里最少",
)


def query_dishes_node(state):
    logger.info("进入 query_dishes_node，开始查询减脂餐")

    result = get_low_fat_dishes()

    if not result.get("success"):
        logger.warning(f"减脂餐查询失败: result={result}")
        state["final_answer"] = "减脂餐查询失败，请稍后再试。"
        state["dishes"] = []
        return state

    state["dishes"] = result.get("data", [])

    logger.info(f"减脂餐查询成功，数量={len(state.get('dishes') or [])}")

    return state


def route_dish_query(state):
    user_input = state.get("user_input", "")

    if any(keyword in user_input for keyword in LOWEST_CALORIE_KEYWORDS):
        logger.info("用户询问最低热量菜品，路由到 select_lowest_calorie")
        return "select_lowest_calorie"

    logger.info("用户询问减脂餐列表，路由到 answer_dish_list")
    return "answer_dish_list"



def select_lowest_calorie_node(state):
    logger.info("进入 select_lowest_calorie_node")

    dishes = state.get("dishes") or []

    if not dishes:
        logger.info("菜品列表为空，无法选择最低热量菜品")
        state["best_dish"] = None
        return state

    best_dish = min(
        dishes,
        key=lambda dish: dish.get("calories", 99999)
    )

    state["best_dish"] = best_dish

    logger.info(f"最低热量菜品选择成功: {best_dish}")

    return state



def answer_dish_list_node(state):
    logger.info("进入 answer_dish_list_node")

    dishes = state.get("dishes") or []

    if state.get("final_answer"):
        logger.info("已有 final_answer，跳过菜品列表回答生成")
        return state

    if not dishes:
        logger.info("菜品列表为空，返回无减脂餐")
        state["final_answer"] = "当前没有查询到减脂餐。"
        return state

    try:
        logger.info("开始调用 LLM 生成减脂餐列表回答")

        state["final_answer"] = generate_customer_answer(
            DISH_LIST_ANSWER_SYSTEM_PROMPT,
            state.get("user_input", ""),
            {
                "dishes": dishes,
            },
            state.get("messages", []),
        )

        logger.info(f"减脂餐列表回答生成成功: {state.get('final_answer')}")
        return state

    except Exception as e:
        logger.warning(f"减脂餐列表回答生成失败，使用兜底回答: {e}")

    lines = []
    for dish in dishes:
        name = dish.get("name", "未知菜品")
        calories = dish.get("calories", "热量未知")
        lines.append(f"- {name}，约 {calories} 大卡")

    state["final_answer"] = "查询到以下减脂餐：\n" + "\n".join(lines)

    logger.info(f"减脂餐列表兜底回答: {state.get('final_answer')}")

    return state

def answer_best_dish_node(state):
    logger.info("进入 answer_best_dish_node")

    best_dish = state.get("best_dish")

    if state.get("final_answer"):
        logger.info("已有 final_answer，跳过最低热量菜品回答生成")
        return state

    if not best_dish:
        logger.info("best_dish 为空，返回无合适减脂餐")
        state["final_answer"] = "当前没有查询到合适的减脂餐。"
        return state

    try:
        logger.info("开始调用 LLM 生成最低热量菜品回答")

        state["final_answer"] = generate_customer_answer(
            DISH_BEST_ANSWER_SYSTEM_PROMPT,
            state.get("user_input", ""),
            {
                "best_dish": best_dish,
            },
            state.get("messages", []),
        )

        logger.info(f"最低热量菜品回答生成成功: {state.get('final_answer')}")
        return state

    except Exception as e:
        logger.warning(f"最低热量菜品回答生成失败，使用兜底回答: {e}")

    name = best_dish.get("name", "未知菜品")
    calories = best_dish.get("calories", "热量未知")

    state["final_answer"] = f"当前热量最低的减脂餐是：{name}，约 {calories} 大卡。"

    logger.info(f"最低热量菜品兜底回答: {state.get('final_answer')}")

    return state
