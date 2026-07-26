import json

from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage,BaseMessage

from agent.langgraph_core.model import chat_model


def generate_customer_answer(system_prompt: str, user_input: str, context: dict,history_messages: Optional[list[BaseMessage]] = None) -> str:
    context_payload = json.dumps(context, ensure_ascii=False, default=str)

    messages = [
        SystemMessage(content=system_prompt)
    ]

    if history_messages:
        #最后一条通常是当前用户输入，这里先去掉，避免重复
        messages.extend(history_messages[:-1])

    messages.append(
        HumanMessage(content=f"""
    用户当前问题：
    {user_input}
    业务数据：
    {context_payload}
    """)
    )

    response = chat_model.invoke(messages)
    return response.content.strip()
