from langgraph.graph import StateGraph, START, END

from agent.langgraph_core.nodes.order_nodes import (
    extract_order_id_node,
    query_order_node,
    answer_order_node
)

from agent.langgraph_core.state import AgentState

def build_order_workflow():
    builder = StateGraph(AgentState)

    builder.add_node("extract_order_id", extract_order_id_node)
    builder.add_node("query_order", query_order_node)
    builder.add_node("answer_order", answer_order_node)

    builder.add_edge(START, "extract_order_id")
    builder.add_edge("extract_order_id", "query_order")
    builder.add_edge("query_order", "answer_order")
    builder.add_edge("answer_order", END)

    return builder.compile()
