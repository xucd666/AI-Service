from typing import TypedDict,Optional,Dict,Any
from langgraph.graph import StateGraph,START,END

from tools.dish_tool import get_low_fat_dishes
from tools.order_tool import get_order_status



# 1. 定义全局 State
class AgentState(TypedDict):
    """
       整个 Agent 工作流共享的状态对象
    """
    user_input: str  # 用户原始提问（输入源头，全程携带）
    intent: Optional[str]  # 识别出的用户意图，初始None

    order_id: Optional[str]  # 提取的订单编号，初始None
    order_info: Optional[Dict[str, Any]]  # 后端查到的订单详情字典

    dish_info: Optional[Dict[str, Any]]

    final_answer: Optional[str]  # 最终回复用户的话术

# 2. Router 节点
def router_node(state: AgentState) -> dict:
    """
    路由节点：
    根据用户输入判断用户想做什么。

    目前先用规则判断：
    - 包含“订单”或数字：走订单查询
    - 包含“减脂 / 低脂 / 菜”：走菜品推荐
    - 其他：走兜底节点

    后面可以把这里升级成 LLM 判断。
    """

    user_input = state["user_input"]

    if "订单" in user_input or any(c.isdigit() for c in user_input):
        intent = "order"
    elif "减脂" in user_input or "低脂" in user_input or "菜" in user_input:
        intent = "dish"
    else:
        intent = "unknown"

    return {
        "intent": intent
    }

# 3. 条件路由函数
def route_by_intent(state: AgentState) -> str:
    """
       条件路由函数：
       LangGraph 会根据这个函数的返回值，
       决定 router_node 后面进入哪个节点。
    """
    intent = state["intent"]

    if intent == "order":
        return "order"

    if intent == "dish":
        return "dish"

    return "unknown"

# 4. 订单处理节点
def order_node(state: AgentState) -> dict:
    """
        订单处理节点：
        1. 从用户输入中提取订单号
        2. 调用真实 Java 后端订单接口
        3. 把结果写回 State
    """
    user_input = state["user_input"]

    # 简单提取订单号：把用户输入中的数字拼接起来
    # 后面可以升级成 LLM 参数提取
    order_id = "".join([c for c in user_input if c.isdigit()])

    # 调用项目里已有的订单查询 Tool
    raw_result = get_order_status(order_id)

    # 这里先不强行解析后端业务字段
    # 因为你当前返回类似：“订单状态：6”
    order_info = {
        "order_id": order_id,
        "status": raw_result
    }
    return {
        "order_id": order_id,
        "order_info": order_info,
        "final_answer": f"您的订单 {order_id} 当前状态是：{raw_result}"
    }

def dish_node(state: AgentState) -> dict:
    """
        菜品推荐节点：
        这里先用模拟数据。
        下一步可以替换成你项目里的真实减脂餐 Tool。
        """

    dishes = get_low_fat_dishes()

    state["dish_info"] = dishes
    if not dishes:
        state["final_answer"] = "当前没有查询到减脂餐，或者减脂餐接口暂时不可用。"
        return state

    lines = []
    for dish in dishes:
        name = dish.get("name", "未知菜品")
        calories = dish.get("calories", "热量未知")
        lines.append(f"{name}，约 {calories}大卡")

    state["final_answer"] = "为您推荐以下减脂餐：\n" + "\n".join(lines)

    return state

# 6. 兜底节点

def unknown_node(state: AgentState) -> dict:
    """
    兜底节点：
    当 Router 无法识别用户意图时进入这里。
    """

    return {
        "final_answer": "我暂时只能处理订单查询和减脂餐推荐。"
    }

# 7. 构建 LangGraph
def build_router_graph():
    """
       构建 Router Graph。

       流程：
       START
         ↓
       router_node
         ↓
       根据 intent 条件分流
         ↓
       order_node / dish_node / unknown_node
         ↓
       END
       """

    graph = StateGraph(AgentState)

    # 注册节点
    graph.add_node("router_node", router_node)
    graph.add_node("order_node", order_node)
    graph.add_node("dish_node", dish_node)
    graph.add_node("unknown_node", unknown_node)

    # 起点进入 Router
    graph.add_edge(START, "router_node")

    #根据router_node 写入的 intent 进行条件路由
    graph.add_conditional_edges(
        "router_node",
        route_by_intent,
        {
            "order": "order_node",
            "dish": "dish_node",
            "unknown": "unknown_node"
        }
    )
    # 三个分支处理完后都结束
    graph.add_edge("order_node", END)
    graph.add_edge("dish_node", END)
    graph.add_edge("unknown_node", END)

    # 编译成可运行对象
    return graph.compile()

# 对外暴露 graph 实例
router_graph = build_router_graph()

