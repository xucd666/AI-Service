import logging
import sys
from config import Config

#1. 配置日志格式：时间 | 日志级别 | 模块 | 内容
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

#2.根日志配置
logging.basicConfig(
    level=logging.INFO, # 全局日志级别：INFO 及以上都会打印
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    stream=sys.stdout  # 输出到控制台，后期可扩展写入日志文件
)

#对外获取logger实例
def get_logger(name : str) -> logging.Logger:
    return logging.getLogger(name)