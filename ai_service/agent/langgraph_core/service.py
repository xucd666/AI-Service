import logging
logger = logging.getLogger("LangGraphService")

from langchain_core.messages import HumanMessage,AIMessage,BaseMessage

from agent.langgraph_core.graph import build_main_graph
from agent.session_memory import SessionMemory
from config import Config

graph = build_main_graph()

langgraph_memory = SessionMemory(
    key_prefix=Config.LANGGRAPH_SESSION_KEY_PREFIX
)

def _dicts_to_messages(history: list[dict]) -> list[BaseMessage]:
    messages = []
    for item in history:
        role = item.get("role")
        content = item.get("content","")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    return messages

def _messages_to_dicts(messages:list[BaseMessage]) -> list[dict]:
    result = []
    for message in messages:
        if isinstance(message, HumanMessage):
            result.append({"role": "user", "content": message.content})
        elif isinstance(message, AIMessage):
            result.append({"role": "assistant", "content": message.content})
    return result

def chat_with_langgraph(session_id:str,user_input: str):
    #Redis读取历史对话
    history = langgraph_memory.get_history(session_id)

    logger.info(f"加载历史消息成功 session_id={session_id} count={len(history)}")

    history_messages = _dicts_to_messages(history)

    #历史 + 当前用户提问，组装送入Graph的初始消息列表
    current_messages = history_messages + [
        HumanMessage(content=user_input)
    ]

    #构造初始状态，启动LangGraph
    init_state = {
        "session_id": session_id,
        "user_input": user_input,
        "messages": current_messages,
        "intent": None,
        "order_id": None,
        "order_info": None,
        "dishes": None,
        "best_dish": None,
        "final_answer": None,
        "need_dish_recommendation": None,
    }

    #执行整个智能体流程图，获取最终状态
    result = graph.invoke(init_state)

    #取出最终恢复兜底
    answer = result.get("final_answer") or "抱歉，我暂时没有生成有效回复。"

    #拼接本轮AI回答，形成完整的对话记录
    new_messages = current_messages + [
        AIMessage(content=answer)
    ]

    #消息阶段，控制上下文长度，防止token爆炸
    max_messages = Config.LANGGRAPH_HISTORY_MAX_MESSAGES
    save_messages = _messages_to_dicts(new_messages[-max_messages:])
    langgraph_memory.save_history(session_id, save_messages)
    logger.info(
        f"保存会话历史成功 session_id={session_id} "
        f"message_count={len(save_messages)}"
    )
    #返回对话接口数据
    return {
        "answer": answer,
        "state": result
    }

def clear_langgraph_history(session_id: str):
    langgraph_memory.clear_history(session_id)
    logger.info(f"清除会话历史成功 session_id={session_id}")
