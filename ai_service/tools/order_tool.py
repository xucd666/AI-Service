import requests
import time

from config import Config
from logger import get_logger

logger = get_logger("OrderTool")


def get_order_info(order_number):
    # 关键：调用 Java 后端 AI 专用订单详情接口，传入的是订单号，不是数据库 id
    url = f"http://localhost:8080/ai/order/info/{order_number}"
    logger.info(f"调用订单详情接口: {url}")
    start_time = time.time()

    try:
        response = requests.get(url, timeout=Config.TOOL_TIMEOUT)
        cost_time = round(time.time() - start_time, 2)
        logger.info(f"订单详情接口响应码: {response.status_code}，执行耗时: {cost_time}s")

        result = response.json()

        if result.get("code") != 1:
            return {
                "success": False,
                "data": None,
                "error": result.get("msg", "订单查询失败")
            }

        return {
            "success": True,
            "data": result.get("data"),
            "error": None
        }

    except Exception as e:
        cost_time = round(time.time() - start_time, 2)
        logger.error(
            f"订单详情接口调用失败，执行耗时: {cost_time}s，异常: {str(e)}",
            exc_info=True
        )

        return {
            "success": False,
            "data": None,
            "error": str(e)
        }


tool_map = {
    "get_order_info": get_order_info
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_info",
            "description": "用户需要查询订单状态、订单详情、配送进度、订单菜品信息时调用",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_number": {
                        "type": "string",
                        "description": "用户提供的订单号，例如 1774855083625"
                    }
                },
                "required": ["order_number"]
            }
        }
    }
]