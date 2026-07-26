from typing import TypedDict,Optional,List,Dict,Any,Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
       完整 State 定义
    """
    session_id: str # 会话ID，前端生成全局唯一值（如 uuid）
    user_input: str # 用户原始提问（输入源头，全程携带）

    messages:Annotated[List[BaseMessage], add_messages] #LangGraph 会话上下文消息

    intent: Optional[str] # 识别出的用户意图，初始None

    order_id: Optional[str] # 提取的订单编号，初始None
    order_info: Optional[Dict[str, Any]] # 后端查到的订单详情字典

    dishes: Optional[List[Dict[str, Any]]] # 后端查到的菜品列表
    best_dish: Optional[Dict[str, Any]] # 后端查到的最合适的菜品

    final_answer: Optional[str] # 最终回复用户

    need_dish_recommendation:Optional[bool] #用户是不是希望顺便推荐菜品
