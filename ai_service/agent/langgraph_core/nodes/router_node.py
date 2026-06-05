import json
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config import Config


llm = ChatOpenAI(
    model=Config.LLM_MODEL,
    api_key=Config.API_KEY,
    base_url=Config.BASE_URL,
    temperature=0
)


def safe_parse_router_result(content: str) -> dict:
    try:
        content = content.strip()

        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        data = json.loads(content)

        intent = data.get("intent", "unknown")
        order_id = data.get("order_id")

        if intent not in ["order", "dish", "unknown"]:
            intent = "unknown"

        return {
            "intent": intent,
            "order_id": order_id
        }

    except Exception:
        return {
            "intent": "unknown",
            "order_id": None
        }


def router_node(state):
    user_input = state.get("user_input", "")

    messages = [
        SystemMessage(content="""
        你是一个餐饮系统智能客服的意图识别器。
        
        你需要识别用户输入属于哪一类：
        
        1. order：用户想查询订单状态、订单进度、订单是否送达、外卖到哪了
        2. dish：用户想查询减脂餐、低脂菜、低热量菜品、减肥期间吃什么、推荐菜品
        3. unknown：不属于以上业务
        
        同时，如果用户输入中包含订单编号，请提取 order_id。
        订单编号通常是一串数字，例如：1774855083625。
        
        你必须只返回 JSON，不要返回任何解释，不要使用 markdown。
        
        返回格式如下：
        
        {
          "intent": "order",
          "order_id": "1774855083625"
        }
        
        如果没有订单编号：
        
        {
          "intent": "dish",
          "order_id": null
        }
        """),
        HumanMessage(content=user_input)
    ]

    response = llm.invoke(messages)

    result = safe_parse_router_result(response.content)

    state["intent"] = result["intent"]
    state["order_id"] = result["order_id"]

    return state