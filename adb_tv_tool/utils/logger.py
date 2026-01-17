# -*- coding: utf-8 -*-
"""
日志配置工具
提供统一的日志记录功能
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        """格式化日志记录"""
        # 保存原始levelname和msg
        original_levelname = record.levelname
        original_msg = record.msg
        
        # 添加颜色到levelname
        if original_levelname in self.COLORS:
            colored_levelname = f"{self.COLORS[original_levelname]}{original_levelname}{self.COLORS['RESET']}"
            colored_msg = f"{self.COLORS[original_levelname]}{original_msg}{self.COLORS['RESET']}"
            
            # 创建副本避免修改原始记录
            record = logging.makeLogRecord(record.__dict__)
            record.levelname = colored_levelname
            record.msg = colored_msg
        
        return super().format(record)


def setup_logging(log_level=logging.INFO, log_file=None):
    """
    配置日志系统
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径，如果为None则不写入文件
    """
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    if log_file is None:
        log_file = log_dir / f"adb_tv_tool_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # 配置根日志记录器
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # 清除已有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # 文件记录更详细的日志
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    colored_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(colored_formatter)
    file_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # 记录启动信息
    logger.info(f"ADB TV Tool 日志系统已初始化，日志文件: {log_file}")
    
    return logger


def get_logger(name):
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)


# 预定义的日志记录器
UI_LOGGER = get_logger("ui")
ADB_LOGGER = get_logger("adb")
SCREEN_LOGGER = get_logger("screen")
APP_LOGGER = get_logger("app")


if __name__ == "__main__":
    # 测试日志系统
    setup_logging(logging.DEBUG)
    
    logger = get_logger("test")
    logger.debug("调试信息")
    logger.info("普通信息")
    logger.warning("警告信息")
    logger.error("错误信息")
    logger.critical("严重错误")