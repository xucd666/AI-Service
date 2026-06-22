import logging

from langgraph.graph import StateGraph,START,END

from agent.langgraph_core.nodes.fallback_nodes import fallback_node
from agent.langgraph_core.nodes.router_node import router_node
from agent.langgraph_core.state import AgentState
from agent.langgraph_core.workflows.dish_workflow import build_dish_workflow
from agent.langgraph_core.workflows.order_workflow import build_order_workflow
from agent.langgraph_core.workflows.multi_workflow import build_multi_workflow

logger = logging.getLogger("MainGraph")

order_workflow = build_order_workflow()
dish_workflow = build_dish_workflow()
multi_workflow = build_multi_workflow()

def order_workflow_node(state: AgentState):
    logger.info("进入 OrderWorkflow")
    result = order_workflow.invoke(state)
    logger.info(f"OrderWorkflow执行结束，final_answer={result.get('final_answer')}")
    return result


def dish_workflow_node(state: AgentState):
    logger.info("进入 DishWorkflow")
    result = dish_workflow.invoke(state)
    logger.info(f"DishWorkflow执行结束，final_answer={result.get('final_answer')}")
    return result


def multi_workflow_node(state: AgentState):
    logger.info("进入 MultiWorkflow")
    result = multi_workflow.invoke(state)
    logger.info(f"MultiWorkflow执行结束，final_answer={result.get('final_answer')}")
    return result


def route_by_intent(state):
    intent = state.get("intent")

    logger.info(f"主图根据 intent 路由: intent={intent}")

    if intent == "order":
        return "order_workflow"

    if intent == "dish":
        return "dish_workflow"

    if intent == "multi":
        return "multi_workflow"

    return "fallback"


def build_main_graph():
    builder = StateGraph(AgentState)

    builder.add_node("router",router_node)
    builder.add_node("order_workflow",order_workflow_node)
    builder.add_node("dish_workflow",dish_workflow_node)
    builder.add_node("multi_workflow", multi_workflow_node)
    builder.add_node("fallback",fallback_node)

    builder.add_edge(START,"router")

    builder.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "order_workflow": "order_workflow",
            "dish_workflow": "dish_workflow",
            "multi_workflow": "multi_workflow",
            "fallback": "fallback",
        }
    )
    builder.add_edge("order_workflow",END)
    builder.add_edge("dish_workflow",END)
    builder.add_edge("multi_workflow", END)
    builder.add_edge("fallback",END)

    return builder.compile()
