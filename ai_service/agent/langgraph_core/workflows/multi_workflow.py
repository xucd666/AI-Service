from langgraph.graph import StateGraph, START, END

from agent.langgraph_core.state import AgentState
from agent.langgraph_core.nodes.order_nodes import (
    extract_order_id_node,
    query_order_node,
)
from agent.langgraph_core.nodes.dish_nodes import select_lowest_calorie_node
from agent.langgraph_core.nodes.multi_nodes import (
    route_after_order_query,
    query_dishes_for_multi_node,
    answer_multi_node,
)

def build_multi_workflow():
    builder = StateGraph(AgentState)

    builder.add_node("extract_order_id", extract_order_id_node)
    builder.add_node("query_order", query_order_node)
    builder.add_node("route_after_order_query", route_after_order_query)
    builder.add_node("query_dishes_for_multi", query_dishes_for_multi_node)
    builder.add_node("select_lowest_calorie", select_lowest_calorie_node)
    builder.add_node("answer_multi", answer_multi_node)

    builder.add_edge(START, "extract_order_id")
    builder.add_edge("extract_order_id", "query_order")

    builder.add_conditional_edges(
        "query_order",
        route_after_order_query,
        {
            "query_dishes_for_multi":"query_dishes_for_multi",
            "end":END,
        },
    )

    builder.add_edge("query_dishes_for_multi","select_lowest_calorie")
    builder.add_edge("select_lowest_calorie", "answer_multi")
    builder.add_edge("answer_multi", END)

    return builder.compile()