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

    conversation_messages = state.get("messages",[])

    logger.info(f"开始识别用户意图: {user_input}")

    messages = [
        SystemMessage(content="""
        你是餐饮系统智能客服的意图识别器。
    
        你需要结合【完整对话历史】和【当前用户问题】判断用户意图。
    
        意图类型：
    
        1. order
        用户想查询订单状态、配送状态、订单进度、外卖到哪里了。
        如果当前问题是“它现在是什么状态”“到哪了”“还要多久”，并且历史里最近在聊订单，也判断为 order。
    
        2. dish
        用户想查询减脂餐、低脂菜、低热量菜品、推荐菜品、哪个热量最低、它多少热量。
        如果当前问题是“哪个热量最低”“它的热量是多少”“刚才那个多少大卡”，并且历史里最近在聊菜品，也判断为 dish。
    
        3. multi
        用户同时包含订单查询和菜品推荐两个需求。
    
        4. unknown
        不属于以上业务。
    
        订单号提取规则：
        - 优先从当前用户问题中提取 order_id
        - 如果当前没有订单号，但历史对话中最近出现过订单号，并且当前问题仍然在问订单，则从历史中提取 order_id
        - 订单号通常是 10 到 20 位数字
    
        你必须只返回 JSON，不要解释，不要 markdown。
    
        返回格式：
        {
          "intent": "order",
          "order_id": "1774855083625",
          "need_dish_recommendation": false
        }
    
        如果没有订单号：
        {
          "intent": "dish",
          "order_id": null,
          "need_dish_recommendation": true
        }
        """),
            *conversation_messages,
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