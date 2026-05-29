import json
from openai import OpenAI
from config import Config
from agent.tool_executor import ToolExecutor
from agent.session_memory import SessionMemory
from logger import get_logger

logger = get_logger("AgentCore")

class AgentCore:
    def __init__(self,tool_map,all_tools,system_prompt):
        self.client = OpenAI(
            base_url=Config.BASE_URL,
            api_key=Config.API_KEY,
        )
        self.tool_executor = ToolExecutor(tool_map)
        self.tools = all_tools
        self.system_prompt = system_prompt
        # 初始化会话记忆实例
        self.session_memory = SessionMemory()
        logger.info("AgentCore 初始化完成（已接入Redis会话记忆）")

    # 【新增】工具调用对象转纯字典，解决序列化问题
    def _convert_tool_calls(self, tool_calls):
        if not tool_calls:
            return None
        call_list = []
        for call in tool_calls:
            call_list.append({
                "id": call.id,
                "type": call.type,
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments
                }
            })
        return call_list
    def chat(self, session_id: str, user_message: str):
        """
            对话入口
            :param session_id: 会话唯一标识，区分不同用户
            :param user_message: 用户当前提问
            :return: AI 最终回复
        """
        logger.info(f"收到会话 {session_id} 提问: {user_message}")
        #1.读取该会话的历史对话
        history = self.session_memory.get_history(session_id)
        # 拼接完整上下文：系统提示词 + 历史对话 + 当前用户消息
        messages = [{"role": "system", "content": self.system_prompt}]+ history
        messages.append({"role": "user", "content": user_message})


        # ========== 自动多轮 Tool 调用 ==========
        while True:
            logger.info(f"会话 {session_id} 发起 LLM 调用，判断是否需要调用工具")
            #1. AI思考
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,
                tools=self.tools
            )
            assistant_msg = response.choices[0].message

            # 【关键修复】把 tool_calls 对象转为纯字典
            tool_calls_dict = self._convert_tool_calls(assistant_msg.tool_calls)
            #消息标准化
            messages.append({
                "role": "assistant",
                "content": assistant_msg.content,
                "tool_calls": tool_calls_dict
            })

            # 没有工具需要调用 → 结束循环
            if not assistant_msg.tool_calls:
                logger.info("LLM 无需调用工具，推理流程结束")
                break

            logger.info(f"会话 {session_id} 检测到 {len(assistant_msg.tool_calls)} 个待执行工具")
            #2.执行所有的工具
            for tool_call in assistant_msg.tool_calls:
                tool_name = tool_call.function.name
                args = tool_call.function.arguments

                #统一执行
                tool_result = self.tool_executor.execute(tool_name,args)

                messages.append({
                    "role": "tool",
                    "content": str(tool_result),
                    "tool_call_id": tool_call.id
                })
        #3.剔除系统提示词，只保留[用户/助手/工具] 消息存入历史
        save_messages = messages[1:]
        self.session_memory.save_history(session_id, save_messages)
        logger.info(f"会话 {session_id} 生成最终回复: {assistant_msg.content}")
        # 最终回答
        return assistant_msg.content