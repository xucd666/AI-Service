from fastapi import FastAPI
import uvicorn

import agent
from agent.core import AgentCore
from tools import ALL_TOOL_MAP, ALL_TOOLS
from prompts.customer_prompt import CUSTOMER_SERVICE_PROMPT
from models.request import ChatRequest, ApiResponse
from config import Config
from logger import get_logger
from agent.langgraph_core.service import chat_with_langgraph

logger = get_logger("Main")
#初始化FastAPI
app = FastAPI()

agent = AgentCore(
    tool_map=ALL_TOOL_MAP,
    all_tools=ALL_TOOLS,
    system_prompt=CUSTOMER_SERVICE_PROMPT
)

@app.post("/chat", response_model=ApiResponse)
async def chat(request: ChatRequest):
    """聊天接口，基于session_id隔离会话"""
    logger.info("收到 /chat 接口请求")
    try:
        reply = agent.chat(request.session_id, request.message)
        return ApiResponse(code=1, message="success", data=reply)
    except Exception as e:
        err_msg = f"接口处理异常: {str(e)}"
        logger.error(err_msg, exc_info=True)
        return ApiResponse(code=0, message=str(e), data=None)

@app.post("/session/clear", response_model=ApiResponse)
async def clear_session(session_id: str):
    """清空指定会话历史"""
    logger.info(f"收到清空会话请求: {session_id}")
    try:
        agent.session_memory.clear_history(session_id)
        return ApiResponse(code=1, message="会话历史已清空", data=None)
    except Exception as e:
        err_msg = f"清空会话失败: {str(e)}"
        logger.error(err_msg, exc_info=True)
        return ApiResponse(code=0, message=str(e), data=None)

@app.post("/chat/langgraph", response_model=ApiResponse)
async def chat_langgraph(request: ChatRequest):
    """LangGraph 测试聊天接口"""
    logger.info("收到 /chat/langgraph 接口请求")
    try:
        result = chat_with_langgraph(request.session_id, request.message)

        return ApiResponse(
            code=1,
            message="success",
            data=result["answer"]
        )
    except Exception as e:
        err_msg = f"LangGraph接口处理异常: {str(e)}"
        logger.error(err_msg, exc_info=True)
        return ApiResponse(code=0, message=str(e), data=None)

# 用 config 里的 HOST & PORT 启动！
if __name__ == '__main__':
    logger.info(f"服务启动 | 地址: {Config.HOST}:{Config.PORT}")
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
