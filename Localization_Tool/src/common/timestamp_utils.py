#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间戳工具模块

该模块包含时间戳生成和格式化功能。
"""

import datetime


def get_timestamp() -> str:
    """
    获取当前时间戳，格式为YYYYMMDD_HHMMSS

    Returns:
        str: 格式化的时间戳
    """
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d_%H%M%S")


def get_formatted_timestamp() -> str:
    """
    获取格式化的时间戳，格式为YYYY-MM-DD HH:MM:SS

    Returns:
        str: 格式化的时间戳
    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def get_date() -> str:
    """
    获取当前日期，格式为YYYY-MM-DD

    Returns:
        str: 格式化的日期
    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d")


def get_time() -> str:
    """
    获取当前时间，格式为HH:MM:SS

    Returns:
        str: 格式化的时间
    """
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")
