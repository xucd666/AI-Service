import json
import logging

from langchain_core.messages import SystemMessage, HumanMessage
from agent.langgraph_core.model import chat_model

logger = logging.getLogger("RouterNode")


def safe_parse_router_result(content: str) -> dict:  #安全解析大模型返回带 markdown 代码块包裹的 JSON 字符串
    try:
        content = content.strip() #移除字符串首尾所有空白字符

        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        data = json.loads(content)

        intent = data.get("intent", "unknown")
        order_id = data.get("order_id")
        need_dish_recommendation = data.get("need_dish_recommendation",False)

        if intent not in ["order", "dish", "multi", "unknown"]:
            intent = "unknown"

        return {
            "intent": intent,
            "order_id": order_id,
            "need_dish_recommendation": need_dish_recommendation
        }

    except Exception as e:
        logger.warning(f"Router JSON解析失败: {e}, 原始内容: {content}")

        return {
            "intent": "unknown",
            "order_id": None,
            "need_dish_recommendation": False
        }


def router_node(state):
    user_input = state.get("user_input", "")

    logger.info(f"开始识别用户意图: {user_input}")

    messages = [
        SystemMessage(content="""
        你是一个餐饮系统智能客服的意图识别器。

        你需要识别用户输入属于哪一类：
        
        1. order：用户只想查询订单状态、订单进度、订单是否送达、外卖到哪了
        2. dish：用户只想查询减脂餐、低脂菜、低热量菜品、减肥期间吃什么、推荐菜品
        3. multi：用户同时包含订单查询和菜品推荐两个需求，例如“帮我查订单，如果还没到就推荐一个减脂餐”
        4. unknown：不属于以上业务
        
        同时，如果用户输入中包含订单编号，请提取 order_id。
        订单编号通常是一串数字，例如：1774855083625。
        
        同时判断用户是否需要菜品推荐，返回 need_dish_recommendation。
        
        你必须只返回 JSON，不要返回任何解释，不要使用 markdown。
        
        返回格式如下：
        
        {
          "intent": "multi",
          "order_id": "1774855083625",
          "need_dish_recommendation": true
        }
        
        如果没有订单编号：
        
        {
          "intent": "dish",
          "order_id": null,
          "need_dish_recommendation": true
        }
        """),
        HumanMessage(content=user_input)
    ]

    response = chat_model.invoke(messages)

    result = safe_parse_router_result(response.content)

    state["intent"] = result["intent"]
    state["order_id"] = result["order_id"]
    state["need_dish_recommendation"] = result["need_dish_recommendation"]

    logger.info(
        f"Router识别结果: intent={state.get('intent')}, "
        f"order_id={state.get('order_id')}, "
        f"need_dish_recommendation={state.get('need_dish_recommendation')}"
    )

    return state