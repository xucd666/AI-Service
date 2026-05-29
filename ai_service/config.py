import os

class Config:
    # ========== LLM 大模型配置 ==========
    LLM_MODEL = "deepseek-chat"
    API_KEY = os.getenv("DEEPSEEK_API_KEY")
    BASE_URL = "https://api.deepseek.com"

    # ========== 服务启动配置 ==========
    HOST = "0.0.0.0"
    PORT = 8000

    # ========== Tool 工具配置 ==========
    TOOL_TIMEOUT = 5

    # ========== Redis 会话配置 ==========
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_PASSWORD = None
    REDIS_DB = 3
    # 会话过期时间：30 分钟（单位：秒），超时自动清空对话历史
    SESSION_EXPIRE_SECONDS = 30 * 60
    # Redis Key 前缀，区分不同业务
    SESSION_KEY_PREFIX = "agent:session:"