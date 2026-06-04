from agent.langchain_core import LangChainAgentCore

agent = LangChainAgentCore()

while True:
    user_input = input("用户：")

    session_id = input("session_id：")

    answer = agent.chat(
        user_input,
        session_id=session_id
    )

    print("AI：", answer)