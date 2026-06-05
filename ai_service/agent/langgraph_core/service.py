from agent.langgraph_core.graph import build_main_graph


graph = build_main_graph()


def chat_with_langgraph(user_input: str):
    init_state = {
        "user_input": user_input,
        "intent": None,
        "order_id": None,
        "order_info": None,
        "dishes": None,
        "best_dish": None,
        "final_answer": None
    }

    result = graph.invoke(init_state)

    return {
        "answer": result.get("final_answer"),
        "state": result
    }