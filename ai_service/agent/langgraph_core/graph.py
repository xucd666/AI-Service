from langgraph.graph import StateGraph,START,END

from agent.langgraph_core.nodes.fallback_nodes import fallback_node
from agent.langgraph_core.nodes.router_node import router_node
from agent.langgraph_core.state import AgentState
from agent.langgraph_core.workflows.dish_workflow import build_dish_workflow
from agent.langgraph_core.workflows.order_workflow import build_order_workflow

order_workflow = build_order_workflow()
dish_workflow = build_dish_workflow()

def order_workflow_node(state:AgentState):
    result = order_workflow.invoke(state)
    return result

def dish_workflow_node(state:AgentState):
    result = dish_workflow.invoke(state)
    return result

def route_by_intent(state):
    intent = state.get("intent")

    if intent == "order":
        return "order_workflow"

    if intent == "dish":
        return "dish_workflow"

    return "fallback"

def build_main_graph():
    builder = StateGraph(AgentState)

    builder.add_node("router",router_node)
    builder.add_node("order_workflow",order_workflow_node)
    builder.add_node("dish_workflow",dish_workflow_node)
    builder.add_node("fallback",fallback_node)

    builder.add_edge(START,"router")
    builder.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "order_workflow": "order_workflow",
            "dish_workflow": "dish_workflow",
            "fallback": "fallback",
        }
    )
    builder.add_edge("order_workflow",END)
    builder.add_edge("dish_workflow",END)
    builder.add_edge("fallback",END)

    return builder.compile()
