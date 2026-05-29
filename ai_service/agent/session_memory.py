import json
from idlelib import history

import redis

from typing import List,Dict
from config import Config
from logger import get_logger

logger = get_logger("SessionMemory")

class SessionMemory:
    def __init__(self):
        # 初始化Redis连接
        self.redis_client= redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD,
            db=Config.REDIS_DB,  # 绑定指定 Redis 库
            decode_responses=True  # 自动将 bytes 转为字符串，不用手动解码
        )
        self.key_prefix = Config.SESSION_KEY_PREFIX
        self.expire = Config.SESSION_EXPIRE_SECONDS

    def _get_redis_key(self, session_id: str) -> str:
        """
        生成 Redis Key
        :param session_id: 会话ID
        :return: Redis Key
        """
        return f"{self.key_prefix}:{session_id}"

    def get_history(self, session_id: str) -> List[Dict]:
        """
        获取会话历史
        :param session_id: 会话ID
        :return: 会话历史
        """
        key = self._get_redis_key(session_id)
        try:
            data = self.redis_client.get(key)
            if not data:
                logger.info(f"会话{session_id}暂无历史对话")
                return []
            #JSON字符串转回 Python 列表
            history = json.loads(data)
            logger.info(f"会话 {session_id} 读取到 {len(history)} 条历史消息")
            return history
        except Exception as e:
            logger.error(f"获取会话 {session_id} 历史失败：{str(e)}", exc_info=True)
            return []

    def save_history(self, session_id: str, message: List[Dict]) -> None:
        """
        保存会话历史 到redis 并刷新过期时间
        :param session_id: 会话ID
        :param message: 会话消息
        :return: None
        """
        key = self._get_redis_key(session_id)
        try:
            # Python 列表转为 JSON 字符串存储
            data = json.dumps(message,ensure_ascii=False)
            self.redis_client.setex(key,self.expire,data)
            logger.info(f"会话 {session_id} 历史保存成功，已设置 {self.expire}s 过期")
        except Exception as e:
            logger.error(f"保存会话 {session_id} 历史失败: {str(e)}", exc_info=True)

    def clear_history(self, session_id: str) -> None:
        """清空指定会话的对话历史"""
        key = self._get_redis_key(session_id)
        try:
            self.redis_client.delete(key)
            logger.info(f"会话 {session_id} 历史已清空")
        except Exception as e:
            logger.error(f"清空会话 {session_id} 失败: {str(e)}", exc_info=True)