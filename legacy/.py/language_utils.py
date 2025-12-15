#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语言配置管理模块
"""

import os
import json
from typing import List, Dict, Any

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 语言配置文件路径
LANGUAGE_CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "language_config.json")


class LanguageConfig:
    """语言配置管理类"""
    
    def __init__(self):
        """初始化语言配置"""
        self.config = self.load_config()
        self.supported_languages = self.config.get("supported_languages", [])
        self.main_directories = self.config.get("main_directories", ["File", "File_backup"])
    
    def load_config(self) -> Dict[str, Any]:
        """加载语言配置文件"""
        try:
            with open(LANGUAGE_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，返回默认配置
            return self._get_default_config()
        except Exception as e:
            print(f"[ERROR] 加载语言配置文件失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "supported_languages": [
                {
                    "code": "zh",
                    "name": "Chinese",
                    "folder_name": "Chinese",
                    "display_name": "中文",
                    "default": True
                },
                {
                    "code": "en",
                    "name": "English",
                    "folder_name": "English",
                    "display_name": "English",
                    "default": False
                }
            ],
            "main_directories": ["File", "File_backup"]
        }
    
    def get_supported_languages(self) -> List[Dict[str, Any]]:
        """获取支持的语言列表"""
        return self.supported_languages
    
    def get_language_by_code(self, code: str) -> Dict[str, Any]:
        """根据语言代码获取语言信息"""
        for lang in self.supported_languages:
            if lang["code"] == code:
                return lang
        return self.get_default_language()
    
    def get_language_by_name(self, name: str) -> Dict[str, Any]:
        """根据语言名称获取语言信息"""
        for lang in self.supported_languages:
            if lang["name"] == name:
                return lang
        return self.get_default_language()
    
    def get_language_by_folder_name(self, folder_name: str) -> Dict[str, Any]:
        """根据文件夹名称获取语言信息"""
        for lang in self.supported_languages:
            if lang["folder_name"] == folder_name:
                return lang
        return self.get_default_language()
    
    def get_default_language(self) -> Dict[str, Any]:
        """获取默认语言"""
        for lang in self.supported_languages:
            if lang["default"]:
                return lang
        return self.supported_languages[0] if self.supported_languages else {}
    
    def get_language_folders(self) -> List[str]:
        """获取语言文件夹列表"""
        return [lang["folder_name"] for lang in self.supported_languages]
    
    def get_main_directories(self) -> List[str]:
        """获取主目录列表"""
        return self.main_directories
    
    def is_supported_language(self, language: str) -> bool:
        """检查语言是否被支持"""
        for lang in self.supported_languages:
            if lang["name"] == language or lang["code"] == language or lang["folder_name"] == language:
                return True
        return False
    
    def add_language(self, language_info: Dict[str, Any]) -> bool:
        """添加新语言"""
        try:
            # 检查语言是否已存在
            if self.is_supported_language(language_info.get("name", "")):
                return False
            
            # 添加新语言
            self.supported_languages.append(language_info)
            
            # 保存配置
            self.save_config()
            return True
        except Exception as e:
            print(f"[ERROR] 添加新语言失败: {e}")
            return False
    
    def remove_language(self, language_code: str) -> bool:
        """移除语言"""
        try:
            # 检查语言是否存在
            if not self.is_supported_language(language_code):
                return False
            
            # 移除语言
            self.supported_languages = [lang for lang in self.supported_languages if lang["code"] != language_code]
            
            # 保存配置
            self.save_config()
            return True
        except Exception as e:
            print(f"[ERROR] 移除语言失败: {e}")
            return False
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(LANGUAGE_CONFIG_PATH), exist_ok=True)
            
            # 保存配置
            with open(LANGUAGE_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ERROR] 保存语言配置文件失败: {e}")
            return False


# 创建全局语言配置实例
language_config = LanguageConfig()

# 导出常用函数
def get_supported_languages() -> List[Dict[str, Any]]:
    """获取支持的语言列表"""
    return language_config.get_supported_languages()

def get_language_by_code(code: str) -> Dict[str, Any]:
    """根据语言代码获取语言信息"""
    return language_config.get_language_by_code(code)

def get_language_by_name(name: str) -> Dict[str, Any]:
    """根据语言名称获取语言信息"""
    return language_config.get_language_by_name(name)

def get_language_by_folder_name(folder_name: str) -> Dict[str, Any]:
    """根据文件夹名称获取语言信息"""
    return language_config.get_language_by_folder_name(folder_name)

def get_default_language() -> Dict[str, Any]:
    """获取默认语言"""
    return language_config.get_default_language()

def get_language_folders() -> List[str]:
    """获取语言文件夹列表"""
    return language_config.get_language_folders()

def get_main_directories() -> List[str]:
    """获取主目录列表"""
    return language_config.get_main_directories()

def is_supported_language(language: str) -> bool:
    """检查语言是否被支持"""
    return language_config.is_supported_language(language)

def add_language(language_info: Dict[str, Any]) -> bool:
    """添加新语言"""
    return language_config.add_language(language_info)

def remove_language(language_code: str) -> bool:
    """移除语言"""
    return language_config.remove_language(language_code)

def save_language_config() -> bool:
    """保存语言配置"""
    return language_config.save_config()
