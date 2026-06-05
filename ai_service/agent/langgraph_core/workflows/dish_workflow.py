from langgraph.graph import StateGraph,START,END

from agent.langgraph_core.state import AgentState
from agent.langgraph_core.nodes.dish_nodes import (
    query_dishes_node,
    select_lowest_calorie_node,
    answer_dish_node
)

def build_dish_workflow():
    builder = StateGraph(AgentState)
    builder.add_node("query_dishes", query_dishes_node)
    builder.add_node("select_lowest_calorie", select_lowest_calorie_node)
    builder.add_node("answer_dish", answer_dish_node)

    builder.add_edge(START, "query_dishes")
    builder.add_edge("query_dishes", "select_lowest_calorie")
    builder.add_edge("select_lowest_calorie", "answer_dish")
    builder.add_edge("answer_dish", END)

    return builder.compile()