
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from redis.commands.search import result

from prompts.customer_prompt import CUSTOMER_SERVICE_PROMPT
from tools.langchain_tools import LANGCHAIN_TOOLS
from config import Config

class LangChainAgentCore:
    def __init__(self):
        self.model = init_chat_model(
            Config.LLM_MODEL,
            model_provider="openai",
            api_key=Config.API_KEY,
            base_url=Config.BASE_URL,
            temperature=0.3
        )

        self.checkpointer = InMemorySaver()

        self.agent = create_agent(
            model=self.model,
            tools=LANGCHAIN_TOOLS,
            system_prompt=CUSTOMER_SERVICE_PROMPT,
            checkpointer=self.checkpointer
        )

    def chat(self, user_input, session_id):
        final_answer = ""

        for chunk in self.agent.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                {"configurable": {"thread_id": session_id}}
        ):
            print(chunk)

            if "model" in chunk:
                messages = chunk["model"].get("messages", [])
                if messages:
                    ai_message = messages[-1]
                    if ai_message.content:
                        final_answer = ai_message.content

        return final_answer
