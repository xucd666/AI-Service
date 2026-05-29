import json
import time
from logger import get_logger

# 模块独立logger
logger = get_logger("ToolExecutor")

class ToolExecutor:
    def __init__(self, tool_map):
        self.tool_map = tool_map

    def execute(self, tool_name, arguments):
        start_time = time.time()
        logger.info(f"执行工具 | 工具名称:{tool_name} | 原始参数:{arguments}")
        try:
            #1.解析参数
            args = json.loads(arguments) if arguments else {}
            logger.info(f"参数解析完成|解析后参数:{args}")

            #2.检查工具是否存在
            if tool_name not in self.tool_map:
                err_msg = f"工具不存在:{tool_name}"
                logger.error(err_msg)
                cost_time = round(time.time() - start_time, 2)
                logger.info(f"工具执行结束，总耗时: {cost_time} s")
                return {
                    "success" : False,
                    "data": None,
                    "error": f"工具不存在:{tool_name}"
                }

            #3.执行工具
            result = self.tool_map[tool_name](**args)
            cost_time = round(time.time() - start_time, 2)
            logger.info(f"工具执行成功 | 工具名: {tool_name}，总耗时: {cost_time} s")
            return {
                "success" : True,
                "data" : result,
                "error": None
            }
        except Exception as e:
            err_msg = f"工具执行异常: {str(e)}"
            cost_time = round(time.time() - start_time, 2)
            logger.error(err_msg, exc_info=True)
            logger.info(f"工具执行结束，总耗时: {cost_time} s")  # exc_info=True 打印异常堆栈
            return {
                "success" : False,
                "data" : None,
                "error" : str(e)
            }