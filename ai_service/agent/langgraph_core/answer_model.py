import json

from langchain_core.messages import HumanMessage, SystemMessage

from agent.langgraph_core.model import chat_model


def generate_customer_answer(system_prompt: str, user_input: str, context: dict) -> str:
    context_payload = json.dumps(context, ensure_ascii=False, default=str)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""
        用户问题：
        {user_input}
        
        业务数据：
        {context_payload}
        """)
    ]

    response = chat_model.invoke(messages)
    return response.content.strip()
