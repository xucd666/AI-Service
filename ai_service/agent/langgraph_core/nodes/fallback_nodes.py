def fallback_node(state):
    # Router 无法识别业务意图时，进入兜底节点
    state["final_answer"] = "我暂时只能处理订单查询和减脂餐推荐。"
    return state