# tools/__init__.py

# 在这里导入你所有的 tool 文件
from . import dish_tool
from . import order_tool

# 自动合并所有工具（永远不用改 main.py）
ALL_TOOLS = []
ALL_TOOL_MAP = {}

# 自动加载
for module in [dish_tool, order_tool]:
    if hasattr(module, "tools"):
        ALL_TOOLS += module.tools
    if hasattr(module, "tool_map"):
        ALL_TOOL_MAP.update(module.tool_map)