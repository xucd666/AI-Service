import requests
import time

from config import Config
from logger import get_logger

logger = get_logger("DishTool")
# ========================
# 企业标准：Tool 返回 Python 对象（不是字符串）
# ========================
def get_low_fat_dishes():
    url = f"http://localhost:8080/dish/low-fat"
    logger.info(f"调用减脂餐接口: {url}")
    start_time = time.time()
    try:
        response = requests.get(url,timeout=Config.TOOL_TIMEOUT)
        cost_time = round(time.time() - start_time, 2)
        logger.info(f"减脂餐接口响应码: {response.status_code}，执行耗时: {cost_time} s")
        result = response.json()
        return result["data"]
    except Exception as e:
        cost_time = round(time.time() - start_time, 2)
        logger.error(f"减脂餐接口调用失败，执行耗时: {cost_time} s，异常: {str(e)}", exc_info=True)
        return []

# ========================
# Tool 注册映射表
# ========================
tool_map = {
    "get_low_fat_dishes": get_low_fat_dishes
}

# ========================
# Tool 定义（给大模型）
# ========================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_low_fat_dishes",
            "description": "用户需要减脂、减肥、低热量饮食推荐时调用，返回菜品名称和热量",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]