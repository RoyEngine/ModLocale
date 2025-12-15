#!/usr/bin/env python3
"""
日志工具模块
实现详细的过程记录与错误追踪
"""

import logging
import os
import traceback
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Dict, Any, Optional


# 错误码定义
class ErrorCode:
    """错误码定义类"""
    # 通用错误
    UNKNOWN_ERROR = "ERR0000"
    FILE_NOT_FOUND = "ERR0001"
    PERMISSION_DENIED = "ERR0002"
    INVALID_INPUT = "ERR0003"
    CONFIG_ERROR = "ERR0004"
    
    # 提取模式错误
    EXTRACT_FAILED = "ERR1000"
    AST_PARSE_ERROR = "ERR1001"
    JAR_DECOMPILE_ERROR = "ERR1002"
    STRING_EXTRACT_ERROR = "ERR1003"
    
    # 扩展模式错误
    EXTEND_FAILED = "ERR2000"
    MAPPING_RULE_ERROR = "ERR2001"
    STRING_MAPPING_ERROR = "ERR2002"
    
    # 文件操作错误
    FILE_READ_ERROR = "ERR3000"
    FILE_WRITE_ERROR = "ERR3001"
    DIRECTORY_OP_ERROR = "ERR3002"
    
    # YAML处理错误
    YAML_PARSE_ERROR = "ERR4000"
    YAML_WRITE_ERROR = "ERR4001"
    YAML_VALIDATION_ERROR = "ERR4002"


class LogLevel:
    """日志级别定义"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class EnhancedRotatingFileHandler(RotatingFileHandler):
    """增强型日志轮转处理器，支持更多配置选项"""
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None,
                 delay=False, errors=None):
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay, errors)


class LogFormatter(logging.Formatter):
    """增强型日志格式化器"""
    def __init__(self, fmt=None, datefmt=None, style='%', validate=True):
        if fmt is None:
            fmt = '%(asctime)s - %(name)s - %(levelname)s - [%(error_code)s] - %(filename)s:%(lineno)d - %(message)s'
        super().__init__(fmt, datefmt, style, validate)
        self.default_error_code = "N/A"

    def format(self, record):
        # 添加默认错误码
        if not hasattr(record, 'error_code'):
            record.error_code = self.default_error_code
        return super().format(record)


class LoggerConfig:
    """日志配置类"""
    def __init__(self):
        self.log_dir = None
        self.level = logging.INFO
        self.max_bytes = 10 * 1024 * 1024  # 10MB
        self.backup_count = 5
        self.use_timed_rotation = False
        self.rotation_when = 'midnight'
        self.rotation_interval = 1


class LoggerManager:
    """日志管理器，统一管理所有日志记录器"""
    _loggers = {}
    _config = LoggerConfig()

    @classmethod
    def set_config(cls, config: LoggerConfig):
        """设置全局日志配置"""
        cls._config = config

    @classmethod
    def get_config(cls) -> LoggerConfig:
        """获取全局日志配置"""
        return cls._config



def setup_logger(name: str, log_dir: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志文件保存目录，默认为项目根目录下的logs文件夹
        level: 日志级别，默认为INFO
        
    Returns:
        配置好的日志记录器
    """
    # 检查日志记录器是否已经初始化
    if name in LoggerManager._loggers:
        return LoggerManager._loggers[name]
    
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        # 日志记录器已经初始化，直接返回
        LoggerManager._loggers[name] = logger
        return logger
    
    # 如果没有指定日志目录，使用项目根目录下的logs文件夹
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)
    
    # 获取全局配置
    config = LoggerManager.get_config()
    
    # 创建日志文件路径
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'{name}_{timestamp}.log')
    
    # 设置日志级别和传播属性
    logger.setLevel(level)
    logger.propagate = False
    
    # 创建日志格式化器
    formatter = LogFormatter()
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 创建文件处理器
    if config.use_timed_rotation:
        # 使用时间轮转
        file_handler = TimedRotatingFileHandler(
            log_file, 
            when=config.rotation_when,
            interval=config.rotation_interval,
            backupCount=config.backup_count,
            encoding='utf-8'
        )
    else:
        # 使用大小轮转
        file_handler = EnhancedRotatingFileHandler(
            log_file, 
            maxBytes=config.max_bytes, 
            backupCount=config.backup_count,
            encoding='utf-8'
        )
    
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 保存到日志管理器
    LoggerManager._loggers[name] = logger
    
    return logger



def get_logger(name: str) -> logging.Logger:
    """
    获取已配置的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器
    """
    if name in LoggerManager._loggers:
        return LoggerManager._loggers[name]
    return logging.getLogger(name)



def log_exception(logger: logging.Logger, message: str, exception: Exception, 
                  error_code: str = ErrorCode.UNKNOWN_ERROR, 
                  context: Optional[Dict[str, Any]] = None) -> None:
    """
    记录异常信息
    
    Args:
        logger: 日志记录器
        message: 异常描述信息
        exception: 异常对象
        error_code: 错误码
        context: 上下文信息
    """
    # 构建完整的异常信息
    exception_info = {
        "message": message,
        "error_code": error_code,
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        "stack_trace": traceback.format_exc(),
        "context": context or {}
    }
    
    # 记录详细异常信息到调试日志
    logger.debug(f"异常详情: {exception_info}")
    
    # 记录简洁异常信息到错误日志
    log_message = f"{message} [错误码: {error_code}] - {type(exception).__name__}: {str(exception)}"
    logger.error(log_message, exc_info=True)



def log_error(logger: logging.Logger, message: str, 
              error_code: str = ErrorCode.UNKNOWN_ERROR, 
              context: Optional[Dict[str, Any]] = None) -> None:
    """
    记录错误信息
    
    Args:
        logger: 日志记录器
        message: 错误描述信息
        error_code: 错误码
        context: 上下文信息
    """
    # 构建完整的错误信息
    error_info = {
        "message": message,
        "error_code": error_code,
        "context": context or {}
    }
    
    # 记录详细错误信息到调试日志
    logger.debug(f"错误详情: {error_info}")
    
    # 记录简洁错误信息到错误日志
    log_message = f"{message} [错误码: {error_code}]"
    if context:
        log_message += f" - 上下文: {context}"
    
    logger.error(log_message, extra={"error_code": error_code})



def log_warning(logger: logging.Logger, message: str, 
                context: Optional[Dict[str, Any]] = None) -> None:
    """
    记录警告信息
    
    Args:
        logger: 日志记录器
        message: 警告描述信息
        context: 上下文信息
    """
    log_message = message
    if context:
        log_message += f" - 上下文: {context}"
    
    logger.warning(log_message)



def log_info(logger: logging.Logger, message: str, 
             context: Optional[Dict[str, Any]] = None) -> None:
    """
    记录信息日志
    
    Args:
        logger: 日志记录器
        message: 信息描述
        context: 上下文信息
    """
    log_message = message
    if context:
        log_message += f" - 上下文: {context}"
    
    logger.info(log_message)



def log_debug(logger: logging.Logger, message: str, 
              context: Optional[Dict[str, Any]] = None) -> None:
    """
    记录调试信息
    
    Args:
        logger: 日志记录器
        message: 调试描述信息
        context: 上下文信息
    """
    log_message = message
    if context:
        log_message += f" - 上下文: {context}"
    
    logger.debug(log_message)



def log_progress(logger: logging.Logger, current: int, total: int, task: str) -> None:
    """
    记录进度信息
    
    Args:
        logger: 日志记录器
        current: 当前进度
        total: 总进度
        task: 任务描述
    """
    progress = (current / total) * 100
    logger.info(f"{task} - 进度: {current}/{total} ({progress:.2f}%)")



def log_result(logger: logging.Logger, result: dict, task: str) -> None:
    """
    记录结果信息
    
    Args:
        logger: 日志记录器
        result: 结果字典
        task: 任务描述
    """
    logger.info(f"{task} - 结果: {result}")



def set_log_level(logger: logging.Logger, level: int) -> None:
    """
    动态调整日志级别
    
    Args:
        logger: 日志记录器
        level: 新的日志级别
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
    
    logger.info(f"日志级别已调整为: {logging.getLevelName(level)}")



def get_error_code(exception: Exception) -> str:
    """
    根据异常类型获取对应的错误码
    
    Args:
        exception: 异常对象
    
    Returns:
        错误码
    """
    error_code_map = {
        FileNotFoundError: ErrorCode.FILE_NOT_FOUND,
        PermissionError: ErrorCode.PERMISSION_DENIED,
        ValueError: ErrorCode.INVALID_INPUT,
        KeyError: ErrorCode.INVALID_INPUT,
        TypeError: ErrorCode.INVALID_INPUT,
    }
    
    return error_code_map.get(type(exception), ErrorCode.UNKNOWN_ERROR)



def log_entry_exit(logger: logging.Logger, func):
    """
    装饰器：记录函数的进入和退出
    
    Args:
        logger: 日志记录器
        func: 被装饰的函数
    """
    def wrapper(*args, **kwargs):
        # 记录函数进入
        logger.debug(f"进入函数: {func.__name__}")
        logger.debug(f"参数: args={args}, kwargs={kwargs}")
        
        try:
            # 执行函数
            result = func(*args, **kwargs)
            
            # 记录函数退出
            logger.debug(f"退出函数: {func.__name__}")
            logger.debug(f"返回值: {result}")
            
            return result
        except Exception as e:
            # 记录异常
            log_exception(logger, f"函数执行失败: {func.__name__}", e)
            raise
    
    return wrapper



def setup_global_logging():
    """
    设置全局日志配置
    """
    # 设置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(LogFormatter())
    root_logger.addHandler(console_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger('yaml').setLevel(logging.WARNING)
    logging.getLogger('tree_sitter').setLevel(logging.WARNING)
