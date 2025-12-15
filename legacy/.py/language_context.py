#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语言上下文管理模块
"""

from typing import Any

from src.common.language_utils import get_default_language, get_language_by_code


class LanguageContext:
    """语言上下文管理器"""
    
    def __init__(self):
        """初始化语言上下文"""
        self.current_language = get_default_language()
    
    def get_current_language(self) -> str:
        """获取当前语言代码"""
        return self.current_language["code"]
    
    def get_current_language_info(self) -> dict:
        """获取当前语言信息"""
        return self.current_language
    
    def set_language(self, language_code: str) -> bool:
        """设置当前语言"""
        try:
            language = get_language_by_code(language_code)
            if language:
                self.current_language = language
                print(f"[INFO] 切换语言到: {language_code}")
                return True
            return False
        except Exception as e:
            print(f"[ERROR] 切换语言失败: {language_code} - {e}")
            return False
    
    def reset_to_default(self) -> bool:
        """重置为默认语言"""
        try:
            self.current_language = get_default_language()
            print(f"[INFO] 重置语言为默认语言: {self.current_language['code']}")
            return True
        except Exception as e:
            print(f"[ERROR] 重置语言失败: {e}")
            return False


# 创建全局语言上下文实例
language_context = LanguageContext()

# 导出常用函数
def get_current_language() -> str:
    """获取当前语言代码"""
    return language_context.get_current_language()

def get_current_language_info() -> dict:
    """获取当前语言信息"""
    return language_context.get_current_language_info()

def set_language(language_code: str) -> bool:
    """设置当前语言"""
    return language_context.set_language(language_code)

def reset_to_default_language() -> bool:
    """重置为默认语言"""
    return language_context.reset_to_default()
