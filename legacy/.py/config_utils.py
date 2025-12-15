#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理工具模块

负责加载、解析和管理配置文件
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DirectoryMapper:
    """
    目录映射器，负责处理不同目录结构之间的映射
    """
    
    def __init__(self):
        """
        初始化目录映射器
        """
        self.mapping_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "config", "directory_mapping.json"
        )
        self.mapping_config: Dict[str, Any] = {}
        self.loaded = False
    
    def load_mapping(self) -> bool:
        """
        加载目录映射配置
        
        Returns:
            bool: 加载是否成功
        """
        try:
            if not os.path.exists(self.mapping_file):
                logger.error(f"目录映射配置文件不存在: {self.mapping_file}")
                return False
            
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                self.mapping_config = json.load(f)
            
            logger.info(f"目录映射配置文件加载成功: {self.mapping_file}")
            self.loaded = True
            return True
        except json.JSONDecodeError as e:
            logger.error(f"目录映射配置文件格式错误: {e}")
            return False
        except Exception as e:
            logger.error(f"加载目录映射配置文件失败: {e}")
            return False
    
    def get_source_directory(self, mode: str, source_type: str = "localization_file") -> Optional[str]:
        """
        获取源文件目录
        
        Args:
            mode: 模式类型 (extract/extend)
            source_type: 源类型 (localization_file)
            
        Returns:
            str: 匹配的源文件目录
        """
        if not self.loaded:
            self.load_mapping()
        
        # 获取基础目录配置
        directories = get_all_directories()
        tool_root = directories.get("tool_root")
        mod_root = directories.get("mod_root")
        
        if not tool_root or not mod_root:
            logger.error("缺少工具根目录或mod根目录配置")
            return None
        
        # 获取源映射配置
        source_mappings = self.mapping_config.get("source_mappings", {})
        mode_mappings = source_mappings.get(mode, {})
        
        # 只使用localization_file路径
        source_path = mode_mappings.get("localization_file")
        if source_path:
            source_path = source_path.replace("${tool_root}", tool_root).replace("${mod_root}", mod_root)
            source_path = os.path.normpath(source_path)
            logger.info(f"使用源目录: {source_path}")
            return source_path
        
        logger.error(f"无法获取源目录，模式: {mode}")
        return None
    
    def get_backup_directory(self, mode: str) -> Optional[str]:
        """
        获取备份目录
        
        Args:
            mode: 模式类型 (extract/extend)
            
        Returns:
            str: 备份目录路径
        """
        if not self.loaded:
            self.load_mapping()
        
        # 获取基础目录配置
        directories = get_all_directories()
        tool_root = directories.get("tool_root")
        mod_root = directories.get("mod_root")
        
        if not tool_root or not mod_root:
            logger.error("缺少工具根目录或mod根目录配置")
            return None
        
        # 获取备份映射配置
        backup_mappings = self.mapping_config.get("backup_mappings", {})
        backup_path = backup_mappings.get(mode)
        
        if backup_path:
            backup_path = backup_path.replace("${tool_root}", tool_root).replace("${mod_root}", mod_root)
            backup_path = os.path.normpath(backup_path)
            logger.info(f"获取备份目录: {backup_path}")
            return backup_path
        
        logger.error(f"无法获取备份目录，模式: {mode}")
        return None


class ConfigManager:
    """
    配置管理器，负责加载和管理配置文件
    """
    
    def __init__(self, config_file: str = None, settings_file: str = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，默认为 config/directory_config.json
            settings_file: 设置文件路径，默认为 config/settings.json
        """
        self.config_file = config_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "config", "directory_config.json"
        )
        self.settings_file = settings_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "config", "settings.json"
        )
        self.config: Dict[str, Any] = {}
        self.settings: Dict[str, Any] = {
            "advanced_mode_enabled": False,
            "main_language": "全部",
            "process_granularity_enabled": True,
            "precheck_mechanism_enabled": True,
            "show_welcome_guide": True,
            "auto_open_output_folder": True
        }
        self.loaded = False
    
    def load_config(self) -> bool:
        """
        加载配置文件
        
        Returns:
            bool: 加载是否成功
        """
        try:
            if not os.path.exists(self.config_file):
                logger.error(f"配置文件不存在: {self.config_file}")
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # 解析目录配置
            self._resolve_directory_config()
            
            logger.info(f"配置文件加载成功: {self.config_file}")
            
            # 加载设置文件
            self._load_settings()
            
            self.loaded = True
            return True
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            return False
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return False
    
    def _load_settings(self) -> None:
        """
        加载设置文件
        """
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                # 更新设置，只覆盖已有的键
                for key, value in loaded_settings.items():
                    if key in self.settings:
                        self.settings[key] = value
                logger.info(f"设置文件加载成功: {self.settings_file}")
            else:
                # 如果设置文件不存在，创建默认设置文件
                self.save_settings()
        except json.JSONDecodeError as e:
            logger.error(f"设置文件格式错误: {e}")
        except Exception as e:
            logger.error(f"加载设置文件失败: {e}")
    
    def save_settings(self) -> bool:
        """
        保存设置到文件
        
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保配置目录存在
            config_dir = os.path.dirname(self.settings_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            logger.info(f"设置保存成功: {self.settings_file}")
            return True
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            return False
    
    def _resolve_directory_config(self) -> None:
        """
        解析目录配置，替换占位符
        """
        if "directories" not in self.config:
            logger.warning("配置文件中缺少directories配置")
            return
        
        directories = self.config["directories"].copy()
        
        # 获取当前脚本目录作为基准
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 计算 tool_root 的绝对路径
        tool_root = directories.get("tool_root")
        if tool_root:
            # 替换 ${current_dir} 占位符为脚本目录
            if "${current_dir}" in tool_root:
                tool_root = tool_root.replace("${current_dir}", script_dir)
            elif not os.path.isabs(tool_root):
                # 如果是相对路径，基于当前脚本目录计算绝对路径
                tool_root = os.path.normpath(os.path.join(script_dir, tool_root))
        else:
            # 如果没有配置 tool_root，使用当前脚本的上级目录作为默认值
            tool_root = script_dir
        directories["tool_root"] = tool_root
        
        # 自动计算 mod_root(Localization_File)路径，位于 tool_root 的上级目录
        # 直接使用外部的Localization_File目录，不创建内部目录
        mod_root = os.path.join(os.path.dirname(tool_root), "Localization_File")
        directories["mod_root"] = mod_root
        
        # 替换占位符
        for key, path in directories.items():
            if isinstance(path, str):
                # 先替换 ${current_dir} 为脚本目录
                if "${current_dir}" in path:
                    path = path.replace("${current_dir}", script_dir)
                # 替换其他占位符
                for placeholder, value in directories.items():
                    if isinstance(value, str):
                        path = path.replace(f"${{{placeholder}}}", value)
                # 替换环境变量
                path = os.path.expandvars(path)
                # 规范化路径
                path = os.path.normpath(path)
                # 更新配置
                self.config["directories"][key] = path
        
        logger.debug(f"解析后的目录配置: {self.config['directories']}")
    
    def get_directory(self, directory_name: str, default: str = None) -> Optional[str]:
        """
        获取目录路径
        
        Args:
            directory_name: 目录名称
            default: 默认值
            
        Returns:
            str: 目录路径，若不存在则返回默认值
        """
        if not self.loaded:
            self.load_config()
        
        if "directories" in self.config:
            return self.config["directories"].get(directory_name, default)
        return default
    
    def get_all_directories(self) -> Dict[str, str]:
        """
        获取所有目录配置
        
        Returns:
            Dict[str, str]: 所有目录配置
        """
        if not self.loaded:
            self.load_config()
        
        return self.config.get("directories", {})
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置项键名
            default: 默认值
            
        Returns:
            Any: 配置项值，若不存在则返回默认值
        """
        if not self.loaded:
            self.load_config()
        
        return self.config.get(key, default)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        获取设置项
        
        Args:
            key: 设置项键名
            default: 默认值
            
        Returns:
            Any: 设置项值，若不存在则返回默认值
        """
        if not self.loaded:
            self.load_config()
        
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        设置设置项
        
        Args:
            key: 设置项键名
            value: 设置项值
            
        Returns:
            bool: 设置是否成功
        """
        if key in self.settings:
            self.settings[key] = value
            return self.save_settings()
        return False
    
    def get_version(self) -> str:
        """
        获取配置文件版本
        
        Returns:
            str: 配置文件版本
        """
        return self.get_config("version", "1.0.0")
    
    def validate_directories(self) -> bool:
        """
        验证目录是否存在
        
        Returns:
            bool: 所有目录是否存在
        """
        all_exist = True
        directories = self.get_all_directories()
        
        for name, path in directories.items():
            if name != "tool_root" and name != "mod_root":
                # 检查目录是否存在，不存在则创建
                if not os.path.exists(path):
                    try:
                        os.makedirs(path, exist_ok=True)
                        logger.info(f"创建目录: {path}")
                    except Exception as e:
                        logger.error(f"创建目录失败: {path}, 错误: {e}")
                        all_exist = False
        
        return all_exist


# 创建全局配置管理器实例
config_manager = ConfigManager()

# 创建全局目录映射器实例
directory_mapper = DirectoryMapper()


def get_directory(directory_name: str, default: str = None) -> Optional[str]:
    """
    获取目录路径的便捷函数
    
    Args:
        directory_name: 目录名称
        default: 默认值
        
    Returns:
        str: 目录路径，若不存在则返回默认值
    """
    return config_manager.get_directory(directory_name, default)


def get_all_directories() -> Dict[str, str]:
    """
    获取所有目录配置的便捷函数
    
    Returns:
        Dict[str, str]: 所有目录配置
    """
    return config_manager.get_all_directories()


def validate_directories() -> bool:
    """
    验证目录是否存在的便捷函数
    
    Returns:
        bool: 所有目录是否存在
    """
    return config_manager.validate_directories()


def load_config() -> bool:
    """
    加载配置文件的便捷函数
    
    Returns:
        bool: 加载是否成功
    """
    return config_manager.load_config()


def get_config(key: str, default: Any = None) -> Any:
    """
    获取配置项的便捷函数
    
    Args:
        key: 配置项键名
        default: 默认值
        
    Returns:
        Any: 配置项值，若不存在则返回默认值
    """
    return config_manager.get_config(key, default)


def get_source_directory(mode: str, source_type: str = "auto") -> Optional[str]:
    """
    获取源文件目录的便捷函数
    
    Args:
        mode: 模式类型 (extract/extend)
        source_type: 源类型 (auto/project/localization_file)
        
    Returns:
        str: 匹配的源文件目录
    """
    return directory_mapper.get_source_directory(mode, source_type)


def get_backup_directory(mode: str) -> Optional[str]:
    """
    获取备份目录的便捷函数
    
    Args:
        mode: 模式类型 (extract/extend)
        
    Returns:
        str: 备份目录路径
    """
    return directory_mapper.get_backup_directory(mode)


def get_setting(key: str, default: Any = None) -> Any:
    """
    获取设置项的便捷函数
    
    Args:
        key: 设置项键名
        default: 默认值
        
    Returns:
        Any: 设置项值，若不存在则返回默认值
    """
    return config_manager.get_setting(key, default)


def set_setting(key: str, value: Any) -> bool:
    """
    设置设置项的便捷函数
    
    Args:
        key: 设置项键名
        value: 设置项值
        
    Returns:
        bool: 设置是否成功
    """
    return config_manager.set_setting(key, value)
