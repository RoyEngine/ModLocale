#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语言资源管理模块
"""

import os
import json
from typing import Dict, Any

from src.common.language_utils import get_supported_languages, get_language_by_code

# 语言资源目录
LANGUAGE_RESOURCE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "resources", "languages")


class LanguageResourceManager:
    """语言资源管理器"""
    
    def __init__(self):
        """初始化语言资源管理器"""
        self.resource_cache = {}
        self.load_all_resources()
    
    def load_all_resources(self) -> None:
        """加载所有语言资源"""
        try:
            # 确保语言资源目录存在
            os.makedirs(LANGUAGE_RESOURCE_DIR, exist_ok=True)
            
            # 加载每种语言的资源
            for lang in get_supported_languages():
                self.load_resource(lang["code"])
        except Exception as e:
            print(f"[ERROR] 加载语言资源失败: {e}")
    
    def load_resource(self, language_code: str) -> None:
        """加载指定语言的资源"""
        try:
            resource_file = os.path.join(LANGUAGE_RESOURCE_DIR, f"{language_code}.json")
            if os.path.exists(resource_file):
                with open(resource_file, "r", encoding="utf-8") as f:
                    self.resource_cache[language_code] = json.load(f)
                    print(f"[INFO] 加载语言资源: {language_code}")
            else:
                # 如果资源文件不存在，创建默认资源
                self.resource_cache[language_code] = {}
                # 注释掉警告信息，避免过多输出
                # print(f"[WARN] 语言资源文件不存在: {resource_file}")
        except Exception as e:
            print(f"[ERROR] 加载语言资源失败: {language_code} - {e}")
            self.resource_cache[language_code] = {}
    
    def get_resource(self, language_code: str, key: str, default: Any = None) -> Any:
        """获取指定语言的资源"""
        if language_code not in self.resource_cache:
            self.load_resource(language_code)
        
        resource = self.resource_cache.get(language_code, {})
        return resource.get(key, default)
    
    def set_resource(self, language_code: str, key: str, value: Any) -> bool:
        """设置指定语言的资源"""
        try:
            if language_code not in self.resource_cache:
                self.load_resource(language_code)
            
            self.resource_cache[language_code][key] = value
            self.save_resource(language_code)
            return True
        except Exception as e:
            print(f"[ERROR] 设置语言资源失败: {language_code} - {key} - {e}")
            return False
    
    def save_resource(self, language_code: str) -> bool:
        """保存指定语言的资源"""
        try:
            if language_code not in self.resource_cache:
                return False
            
            # 确保资源目录存在
            os.makedirs(LANGUAGE_RESOURCE_DIR, exist_ok=True)
            
            resource_file = os.path.join(LANGUAGE_RESOURCE_DIR, f"{language_code}.json")
            with open(resource_file, "w", encoding="utf-8") as f:
                json.dump(self.resource_cache[language_code], f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ERROR] 保存语言资源失败: {language_code} - {e}")
            return False
    
    def add_language_resource(self, language_code: str, resource: Dict[str, Any]) -> bool:
        """添加新语言的资源"""
        try:
            self.resource_cache[language_code] = resource
            self.save_resource(language_code)
            return True
        except Exception as e:
            print(f"[ERROR] 添加语言资源失败: {language_code} - {e}")
            return False
    
    def remove_language_resource(self, language_code: str) -> bool:
        """移除指定语言的资源"""
        try:
            if language_code not in self.resource_cache:
                return False
            
            # 移除资源缓存
            del self.resource_cache[language_code]
            
            # 删除资源文件
            resource_file = os.path.join(LANGUAGE_RESOURCE_DIR, f"{language_code}.json")
            if os.path.exists(resource_file):
                os.remove(resource_file)
                print(f"[INFO] 删除语言资源文件: {resource_file}")
            
            return True
        except Exception as e:
            print(f"[ERROR] 移除语言资源失败: {language_code} - {e}")
            return False


# 创建全局语言资源管理器实例
language_resource_manager = LanguageResourceManager()

# 导出常用函数
def get_resource(language_code: str, key: str, default: Any = None) -> Any:
    """获取指定语言的资源"""
    return language_resource_manager.get_resource(language_code, key, default)

def set_resource(language_code: str, key: str, value: Any) -> bool:
    """设置指定语言的资源"""
    return language_resource_manager.set_resource(language_code, key, value)

def save_resource(language_code: str) -> bool:
    """保存指定语言的资源"""
    return language_resource_manager.save_resource(language_code)

def add_language_resource(language_code: str, resource: Dict[str, Any]) -> bool:
    """添加新语言的资源"""
    return language_resource_manager.add_language_resource(language_code, resource)

def remove_language_resource(language_code: str) -> bool:
    """移除指定语言的资源"""
    return language_resource_manager.remove_language_resource(language_code)

def load_resource(language_code: str) -> None:
    """加载指定语言的资源"""
    language_resource_manager.load_resource(language_code)

def load_all_resources() -> None:
    """加载所有语言资源"""
    language_resource_manager.load_all_resources()
