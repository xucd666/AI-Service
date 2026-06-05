from typing import TypedDict,List,Dict,Optional
from langgraph.graph import StateGraph,START,END

from tools.dish_tool import get_low_fat_dishes


#1.定制State
class DishWorkfolwState(TypedDict):
    """
       完整 State 定义
    """
    user_input: str  # 用户原始提问（输入源头，全程携带）
    dishes:Optional[List[Dict]]
    best_dish:Optional[Dict]
    final_answer:Optional[str]

#2.查询减脂餐节点
def query_dishs_node(state:DishWorkfolwState):
    dishes = get_low_fat_dishes()

    state["dishes"] = dishes
    return state

#3.选择最低热量菜品节点
def select_lowest_calorie_node(state:DishWorkfolwState):
    dishes = state("dishes") or []

    if not dishes:
        state["best_dish"] = None
        return state

    best_dish = min(
        dishes,
        key=lambda dish:dish.get("calories",99999)
    )
    state["best_dish"] = best_dish
    return state

#4.生成最终回复
def answer_node(state:DishWorkfolwState):
    best_dish = state("best_dish")

    if not best_dish:
        state["final_answer"] = "当前没有查询到减脂餐，或者减脂餐接口暂时不可用。"
        return state

    name = best_dish.get("name", "未知菜品")
    calories = best_dish.get("calories", "热量未知")

    state["final_answer"] = f"当前热量最低的减脂餐是：{name}，约 {calories} 大卡。"
    return state

# 5. 构建 Graph
def build_dish_workflow_graph():
    graph_builder = StateGraph(DishWorkfolwState)

    graph_builder.add_node("query_dishs_node",query_dishs_node)
    graph_builder.add_node("select_lowest_calorie_node",select_lowest_calorie_node)
    graph_builder.add_node("answer_node",answer_node)

    graph_builder.add_edge(START,"query_dishs_node")
    graph_builder.add_edge("query_dishs_node","select_lowest_calorie_node")
    graph_builder.add_edge("select_lowest_calorie_node","answer_node")
    graph_builder.add_edge("answer_node",END)

    return graph_builder.compile()


# ========================
# 6. 测试运行
# ========================
if __name__ == "__main__":
    graph = build_dish_workflow_graph()

    result = graph.invoke({
        "user_input": "帮我推荐热量最低的减脂餐",
        "dishes": None,
        "best_dish": None,
        "final_answer": None
    })

    print("Workflow Graph 测试结果：")
    print(result)
    print(result["final_answer"])
