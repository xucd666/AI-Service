from langchain.tools import tool

from tools.dish_tool import get_low_fat_dishes
from tools.order_tool import get_order_status


@tool
def lc_get_low_fat_dishes() -> list:
    """用户需要减脂、减肥、低热量饮食推荐时调用，返回菜品名称和热量。"""
    return get_low_fat_dishes()

@tool
def lc_get_order_status(order_id: str) -> dict:
    """
        查询订单状态。

    使用场景：
    当用户询问订单状态、订单进度、订单是否配送、
    订单是否完成等问题时使用。

    参数：
    order_id: 用户订单编号，例如：
    1774855083625

    调用规则：
    1. 用户必须提供订单号。
    2. 如果没有订单号，不要调用工具。
    3. 应先向用户询问订单号。
    4. 不要把手机号、用户名、地址当作订单号。
    """
    if not order_id:
        return {
            "success": False,
            "msg": "订单号不能为空"
        }

    if not order_id.isdigit():
        return {
            "success": False,
            "msg": "订单号格式错误"
        }

    return get_order_status(order_id)

LANGCHAIN_TOOLS = [
    lc_get_low_fat_dishes,
    lc_get_order_status,
]