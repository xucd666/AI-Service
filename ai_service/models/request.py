from typing import Any

from pydantic import BaseModel


# 数据模型定义
# 后端返回给前端的格式（统一格式：code + message + data）
class ApiResponse(BaseModel):
    code:int
    message:str
    data:Any

# 前端传给后端的消息格式
# 聊天请求：新增 session_id 区分用户会话
class ChatRequest(BaseModel):
    session_id: str   # 会话ID，前端生成全局唯一值（如 uuid）
    message: str      # 用户消息