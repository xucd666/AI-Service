from typing import TypedDict,Optional,List,Dict,Any

class AgentState(TypedDict):
    """
       完整 State 定义
    """
    user_input: str # 用户原始提问（输入源头，全程携带）

    intent: Optional[str] # 识别出的用户意图，初始None

    order_id: Optional[str] # 提取的订单编号，初始None
    order_info: Optional[Dict[str, Any]] # 后端查到的订单详情字典

    dishes: Optional[List[Dict[str, Any]]] # 后端查到的菜品列表
    best_dish: Optional[Dict[str, Any]] # 后端查到的最合适的菜品

    final_answer: Optional[str] # 最终回复用户