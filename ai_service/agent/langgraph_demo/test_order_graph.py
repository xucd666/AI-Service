import sys
import os

# 把 ai_service 目录加入 Python 搜索路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agent.langgraph_demo.router_graph import router_graph


def build_init_state(user_input: str) -> dict:
    """
    构造 LangGraph 的初始 State。
    每次 invoke 都需要传入一份完整初始状态。
    """
    return {
        "user_input": user_input,
        "intent": None,
        "order_id": None,
        "order_info": None,
        "dish_info": None,
        "final_answer": None
    }


# 测试1：订单查询
result1 = router_graph.invoke(build_init_state("帮我查询订单1774855083625"))

print("订单测试结果：")
print(result1)
print(result1["final_answer"])

print("-" * 50)


# 测试2：减脂餐推荐
result2 = router_graph.invoke(build_init_state("我想吃减脂餐"))

print("减脂餐测试结果：")
print(result2)
print(result2["final_answer"])

print("-" * 50)


# 测试3：无法识别的问题
result3 = router_graph.invoke(build_init_state("今天天气怎么样"))

print("兜底测试结果：")
print(result3)
print(result3["final_answer"])