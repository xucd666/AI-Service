import requests
import time

from config import Config
from logger import get_logger

logger = get_logger("OrderTool")
# 带参数业务 Tool：调用Java
def get_order_status(order_id):
    url = f"http://localhost:8080/order/status/{order_id}"
    logger.info(f"调用订单接口: {url}")
    start_time = time.time()  # 记录起始时间
    try:
        response = requests.get(url,timeout=Config.TOOL_TIMEOUT)
        cost_time = round(time.time() - start_time, 2)  # 计算耗时
        logger.info(f"订单接口响应码: {response.status_code}，执行耗时: {cost_time} s")

        result = response.json()

        return {
            "success": True,
            "data": {
                "order_id": order_id,
                "status": result.get("data")
            },
            "error": None
        }
    except Exception as e:
        cost_time = round(time.time() - start_time, 2)
        logger.error(
            f"订单接口调用失败，执行耗时: {cost_time} s，异常: {str(e)}",
            exc_info=True
        )

        return {
            "success": False,
            "data": None,
            "error": str(e)
        }

# Tool 映射表（企业标准）
tool_map = {
    "get_order_status": get_order_status
}

# 带参数 Tool 定义（给AI看）
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "用户需要查询订单状态时调用，返回订单状态",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "用户提供的订单编号，例如 123456"
                    }
                },
                "required": ["order_id"]
            }
        }
    }
]