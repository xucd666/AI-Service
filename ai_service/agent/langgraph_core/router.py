def router_node(state):
    user_input = state.get("user_input","")

    if "订单" in user_input:
        state["intent"] = "order"
    elif "减脂" in user_input or "低热量" in user_input or "减肥" in user_input:
        state["intent"] = "dish"
    else:
        state["intent"] = "unknown"

    return state

def route_by_intent(state):
    """
          条件路由函数：
          LangGraph 会根据这个函数的返回值，
          决定 router_node 后面进入哪个节点。
    """
    intent = state.get("intent","")

    if intent == "order":
        return "order"

    if intent == "dish":
        return "dish"

    return "unknown"