from langchain_openai import ChatOpenAI
from config import Config

chat_model = ChatOpenAI(
    model=Config.LLM_MODEL,
    api_key=Config.API_KEY,
    base_url=Config.BASE_URL,
    temperature=0
)