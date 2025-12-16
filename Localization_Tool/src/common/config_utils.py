#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理工具模块

负责加载、解析和管理配置文件
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List, Tuple

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
        self.mapping_config: Dict[str, Any] = {
            "source_mappings": {
                "extract": {
                    "localization_file": "${mod_root}/source"
                },
                "extend": {
                    "localization_file": "${mod_root}/source"
                }
            },
            "backup_mappings": {
                "extract": "${mod_root}/source_backup",
                "extend": "${mod_root}/source_backup"
            }
        }
        self.loaded = False
    
    def load_mapping(self) -> bool:
        """
        加载目录映射配置
        
        Returns:
            bool: 加载是否成功
        """
        try:
            if not os.path.exists(self.mapping_file):
                logger.warning(f"目录映射配置文件不存在，将使用默认配置: {self.mapping_file}")
                # 创建默认配置文件
                self.save_mapping()
                return True
            
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                self.mapping_config = json.load(f)
            
            logger.info(f"目录映射配置文件加载成功: {self.mapping_file}")
            self.loaded = True
            return True
        except json.JSONDecodeError as e:
            logger.error(f"目录映射配置文件格式错误: {e}")
            logger.info("使用默认目录映射配置")
            self.save_mapping()
            return True
        except Exception as e:
            logger.error(f"加载目录映射配置文件失败: {e}")
            logger.info("使用默认目录映射配置")
            self.save_mapping()
            return True
    
    def save_mapping(self) -> bool:
        """
        保存目录映射配置
        
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保配置目录存在
            config_dir = os.path.dirname(self.mapping_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                logger.info(f"创建配置目录: {config_dir}")
            
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.mapping_config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"目录映射配置文件保存成功: {self.mapping_file}")
            return True
        except Exception as e:
            logger.error(f"保存目录映射配置文件失败: {e}")
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
        
        if not tool_root:
            logger.error("缺少工具根目录配置")
            return None
        
        if not mod_root:
            logger.error("缺少mod根目录配置")
            return None
        
        # 验证模式是否有效
        valid_modes = ["extract", "extend"]
        if mode not in valid_modes:
            logger.error(f"无效的模式: {mode}，支持的模式: {', '.join(valid_modes)}")
            return None
        
        # 获取源映射配置
        source_mappings = self.mapping_config.get("source_mappings", {})
        mode_mappings = source_mappings.get(mode, {})
        
        # 只使用localization_file路径
        source_path = mode_mappings.get("localization_file")
        if source_path:
            try:
                # 替换占位符
                source_path = source_path.replace("${tool_root}", tool_root).replace("${mod_root}", mod_root)
                source_path = os.path.normpath(source_path)
                logger.info(f"使用源目录: {source_path}")
                return source_path
            except Exception as e:
                logger.error(f"处理源目录路径时发生异常: {e}")
                return None
        
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
        
        if not tool_root:
            logger.error("缺少工具根目录配置")
            return None
        
        if not mod_root:
            logger.error("缺少mod根目录配置")
            return None
        
        # 验证模式是否有效
        valid_modes = ["extract", "extend"]
        if mode not in valid_modes:
            logger.error(f"无效的模式: {mode}，支持的模式: {', '.join(valid_modes)}")
            return None
        
        # 获取备份映射配置
        backup_mappings = self.mapping_config.get("backup_mappings", {})
        
        backup_path = backup_mappings.get(mode)
        if backup_path:
            try:
                # 替换占位符
                backup_path = backup_path.replace("${tool_root}", tool_root).replace("${mod_root}", mod_root)
                backup_path = os.path.normpath(backup_path)
                logger.info(f"获取备份目录: {backup_path}")
                return backup_path
            except Exception as e:
                logger.error(f"处理备份目录路径时发生异常: {e}")
                return None
        
        logger.error(f"无法获取备份目录，模式: {mode}")
        return None
    
    def get_output_directory(self, mode: str, language: str = "English") -> Optional[str]:
        """
        获取输出目录
        
        Args:
            mode: 模式类型 (extract/extend)
            language: 语言类型 (English/Chinese)
            
        Returns:
            str: 输出目录路径
        """
        if not self.loaded:
            self.load_mapping()
        
        # 获取基础目录配置
        directories = get_all_directories()
        output_root = directories.get("output")
        
        if not output_root:
            logger.error("缺少output根目录配置")
            return None
        
        # 根据模式和语言构建输出目录
        if mode == "extract":
            output_path = os.path.join(output_root, f"Extract_{language}")
        elif mode == "extend":
            mapping_direction = "zh2en" if language == "Chinese" else "en2zh"
            output_path = os.path.join(output_root, f"Extend_{mapping_direction}")
        else:
            output_path = os.path.join(output_root, mode.capitalize())
        
        try:
            output_path = os.path.normpath(output_path)
            logger.info(f"获取输出目录: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"处理输出目录路径时发生异常: {e}")
            return None


class ConfigManager:
    """
    配置管理器，负责加载和管理配置文件
    """
    # 类级缓存，避免重复加载配置
    _cache: Dict[str, Any] = {
        "config": None,
        "settings": None,
        "loaded_time": None,
        "config_mtime": 0,
        "settings_mtime": 0
    }
    
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
        self.config: Dict[str, Any] = {
            "version": "1.0.0",
            "directories": {
                "tool_root": "${current_dir}",
                "mod_root": "${current_dir}/File",
                "source_backup": "${mod_root}/source_backup",                
                "source": "${mod_root}/source",            
                "output": "${mod_root}/output",
                "rules": "${mod_root}/rule",
                "logs": "${tool_root}/logs"
            }
        }
        self.settings: Dict[str, Any] = {
            "advanced_mode_enabled": False,
            "main_language": "全部",
            "process_granularity_enabled": True,
            "precheck_mechanism_enabled": True,
            "show_welcome_guide": True,
            "auto_open_output_folder": True
        }
        self.loaded = False
        # 使用缓存数据（如果有）
        self._use_cache()
    
    def _use_cache(self) -> None:
        """
        使用缓存的配置数据
        """
        if self._cache["config"] and self._cache["settings"]:
            self.config = self._cache["config"]
            self.settings = self._cache["settings"]
            self.loaded = True
            logger.debug("使用缓存的配置数据")
    
    def _update_cache(self) -> None:
        """
        更新配置缓存，确保缓存数据与当前配置一致
        """
        config_mtime = os.path.getmtime(self.config_file) if os.path.exists(self.config_file) else 0
        settings_mtime = os.path.getmtime(self.settings_file) if os.path.exists(self.settings_file) else 0
        
        self._cache["config"] = self.config.copy()
        self._cache["settings"] = self.settings.copy()
        self._cache["loaded_time"] = time.time()
        self._cache["config_mtime"] = config_mtime
        self._cache["settings_mtime"] = settings_mtime
        logger.debug("配置缓存已更新")
    
    def load_config(self) -> bool:
        """
        加载配置文件，实现智能缓存机制
        
        Returns:
            bool: 加载是否成功
        """
        try:
            # 检查配置文件是否存在
            if not os.path.exists(self.config_file):
                logger.warning(f"配置文件不存在，将创建默认配置: {self.config_file}")
                # 创建默认配置文件
                self.save_config()
                # 重新加载刚创建的配置文件，确保目录解析正确
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # 解析目录配置
                self._resolve_directory_config()
                # 加载设置文件
                self._load_settings()
                # 更新缓存
                self._update_cache()
                self.loaded = True
                return True
            
            # 检查配置文件的修改时间
            config_mtime = os.path.getmtime(self.config_file)
            settings_mtime = os.path.getmtime(self.settings_file) if os.path.exists(self.settings_file) else 0
            
            # 如果文件没有变化且已有缓存，直接使用缓存
            if (self._cache["config"] and 
                self._cache["settings"] and 
                config_mtime == self._cache["config_mtime"] and 
                settings_mtime == self._cache["settings_mtime"]):
                logger.debug("配置文件未变化，使用缓存数据")
                self.config = self._cache["config"]
                self.settings = self._cache["settings"]
                self.loaded = True
                return True
            
            # 文件有变化，重新加载
            logger.debug("配置文件已更新，重新加载")
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # 解析目录配置
            self._resolve_directory_config()
            
            logger.info(f"配置文件加载成功: {self.config_file}")
            
            # 加载设置文件
            self._load_settings()
            
            # 更新缓存
            self._update_cache()
            
            self.loaded = True
            return True
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            logger.info("使用默认配置")
            self.save_config()
            # 重新加载修复后的配置
            return self.load_config()
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            logger.info("使用默认配置")
            self.save_config()
            # 重新加载修复后的配置
            return self.load_config()
    
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
            logger.info("使用默认设置")
            self.save_settings()
        except Exception as e:
            logger.error(f"加载设置文件失败: {e}")
            logger.info("使用默认设置")
            self.save_settings()
    
    def save_config(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保配置目录存在
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置文件保存成功: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            return False
    
    def save_settings(self) -> bool:
        """
        保存设置到文件，并更新缓存
        
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
            logger.info(f"设置文件保存成功: {self.settings_file}")
            
            # 更新缓存
            if self._cache["config"] is not None:
                self._cache["settings"] = self.settings.copy()
                self._cache["settings_mtime"] = os.path.getmtime(self.settings_file)
                logger.debug("设置缓存已更新")
            
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
            # 创建默认的directories配置
            self.config["directories"] = {
                "tool_root": "${current_dir}",
                "mod_root": "${current_dir}/File",
                "source": "${mod_root}/source",
                "output": "${mod_root}/output",
                "logs": "${tool_root}/logs",
                "rules": "${mod_root}/rule"
            }
            logger.info("已创建默认的directories配置")
        
        directories = self.config["directories"].copy()
        
        # 获取当前脚本目录作为基准
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logger.debug(f"当前脚本目录: {script_dir}")
        
        # 第一步：预替换所有${current_dir}占位符，避免os.path.expandvars报错
        logger.debug("开始预替换所有${current_dir}占位符")
        for key in list(directories.keys()):
            if isinstance(directories[key], str) and "${current_dir}" in directories[key]:
                directories[key] = directories[key].replace("${current_dir}", script_dir)
                logger.debug(f"预替换 {key} 中的${{current_dir}}: {directories[key]}")
        
        # 计算 tool_root 的绝对路径
        tool_root = directories.get("tool_root")
        if tool_root:
            if not os.path.isabs(tool_root):
                # 如果是相对路径，基于当前脚本目录计算绝对路径
                tool_root = os.path.normpath(os.path.join(script_dir, tool_root))
                logger.debug(f"相对路径转换后 tool_root: {tool_root}")
        else:
            # 如果没有配置 tool_root，使用当前脚本的上级目录作为默认值
            tool_root = script_dir
            logger.debug(f"使用默认值 tool_root: {tool_root}")
        directories["tool_root"] = tool_root
        
        # 替换占位符
        for key, path in directories.items():
            if isinstance(path, str):
                original_path = path
                logger.debug(f"开始处理 {key} 的路径: {path}")
                # 再次检查并替换${current_dir}，确保所有占位符都已被替换
                if "${current_dir}" in path:
                    path = path.replace("${current_dir}", script_dir)
                    logger.debug(f"再次替换 ${current_dir} 后 {key}: {path}")
                # 替换其他占位符，特别是tool_root和mod_root
                for placeholder, value in directories.items():
                    if isinstance(value, str):
                        placeholder_str = f"${{{placeholder}}}"
                        if placeholder_str in path:
                            path = path.replace(placeholder_str, value)
                            logger.debug(f"替换 {placeholder_str} 后 {key}: {path}")
                # 替换环境变量，使用try-except捕获异常
                try:
                    expanded_path = os.path.expandvars(path)
                    if expanded_path != path:
                        path = expanded_path
                        logger.debug(f"替换环境变量后 {key}: {path}")
                except NameError as e:
                    logger.warning(f"替换环境变量时发生错误: {e}，将使用原始路径")
                    # 手动处理${}格式的占位符，避免os.path.expandvars报错
                    import re
                    path = re.sub(r'\$\{[^}]+\}', '', path)
                    logger.debug(f"手动处理后 {key}: {path}")
                # 规范化路径
                path = os.path.normpath(path)
                if path != original_path:
                    logger.debug(f"规范化后 {key}: {path} (原路径: {original_path})")
                # 更新配置
                directories[key] = path
                self.config["directories"][key] = path
        
        # 专门处理mod_root，确保它正确指向Localization_File目录
        mod_root = directories.get("mod_root")
        if mod_root:
            # 确保mod_root是绝对路径
            if not os.path.isabs(mod_root):
                mod_root = os.path.normpath(os.path.join(script_dir, mod_root))
                directories["mod_root"] = mod_root
                self.config["directories"]["mod_root"] = mod_root
                logger.debug(f"mod_root 转换为绝对路径: {mod_root}")
        
        logger.debug(f"解析后的目录配置: {self.config['directories']}")
        
        # 验证mod_root路径是否包含File
        final_mod_root = self.config["directories"].get("mod_root", "")
        if "File" not in final_mod_root:
            logger.warning(f"mod_root 路径可能不正确，不包含 File: {final_mod_root}")
        else:
            logger.debug(f"mod_root 路径正确，包含 File: {final_mod_root}")
    
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
        
        if "directories" not in self.config:
            logger.error(f"配置中缺少directories，无法获取目录: {directory_name}")
            return default
        
        directory_path = self.config["directories"].get(directory_name)
        if directory_path is None:
            logger.warning(f"配置中未找到目录: {directory_name}，使用默认值")
            return default
        
        # 验证路径是否为字符串类型
        if not isinstance(directory_path, str):
            logger.error(f"目录 {directory_name} 的配置值不是字符串类型: {type(directory_path)}")
            return default
        
        # 验证路径是否有效
        try:
            # 确保路径已规范化
            normalized_path = os.path.normpath(directory_path)
            logger.debug(f"获取目录 {directory_name} 的路径: {normalized_path}")
            return normalized_path
        except Exception as e:
            logger.error(f"处理目录 {directory_name} 路径时发生异常: {e}")
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
    
    def set_directory(self, directory_name: str, directory_path: str) -> bool:
        """
        设置目录路径
        
        Args:
            directory_name: 目录名称
            directory_path: 目录路径
            
        Returns:
            bool: 设置是否成功
        """
        if not self.loaded:
            self.load_config()
        
        if "directories" not in self.config:
            self.config["directories"] = {}
        
        self.config["directories"][directory_name] = directory_path
        logger.info(f"设置目录 {directory_name}: {directory_path}")
        return self.save_config()
    
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
    
    def set_config(self, key: str, value: Any) -> bool:
        """
        设置配置项
        
        Args:
            key: 配置项键名
            value: 配置项值
            
        Returns:
            bool: 设置是否成功
        """
        if not self.loaded:
            self.load_config()
        
        self.config[key] = value
        logger.info(f"设置配置项 {key}: {value}")
        return self.save_config()
    
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
            logger.info(f"设置设置项 {key}: {value}")
            return self.save_settings()
        logger.warning(f"设置项 {key} 不存在")
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
        
        # 先验证并创建mod_root目录（如果需要）
        mod_root = directories.get("mod_root")
        if mod_root:
            # 验证mod_root路径是否包含File
            if "File" not in mod_root:
                logger.error(f"mod_root 路径不正确，不包含 File: {mod_root}")
                # 尝试从配置中重新构建正确的mod_root路径
                tool_root = directories.get("tool_root")
                if tool_root:
                    correct_mod_root = os.path.normpath(os.path.join(tool_root, "File"))
                    logger.info(f"正在修复mod_root路径，将使用正确路径: {correct_mod_root}")
                    # 更新配置
                    self.set_directory("mod_root", correct_mod_root)
                    mod_root = correct_mod_root
                else:
                    all_exist = False
            
            # 检查mod_root目录是否存在，不存在则创建
            if not os.path.exists(mod_root):
                try:
                    os.makedirs(mod_root, exist_ok=True)
                    logger.info(f"创建mod_root目录: {mod_root}")
                except Exception as e:
                    logger.error(f"创建mod_root目录失败: {mod_root}, 错误: {e}")
                    all_exist = False
        else:
            logger.error("mod_root 配置不存在")
            all_exist = False
        
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
    
    def export_config(self, export_path: str) -> bool:
        """
        导出配置到文件
        
        Args:
            export_path: 导出路径
            
        Returns:
            bool: 导出是否成功
        """
        try:
            if not self.loaded:
                self.load_config()
            
            export_data = {
                "config": self.config,
                "settings": self.settings,
                "export_time": time.time()
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置导出成功: {export_path}")
            return True
        except Exception as e:
            logger.error(f"配置导出失败: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        从文件导入配置
        
        Args:
            import_path: 导入路径
            
        Returns:
            bool: 导入是否成功
        """
        try:
            if not os.path.exists(import_path):
                logger.error(f"导入配置文件不存在: {import_path}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if "config" in import_data:
                self.config = import_data["config"]
                logger.info("导入配置成功")
            
            if "settings" in import_data:
                self.settings = import_data["settings"]
                logger.info("导入设置成功")
            
            # 保存导入的配置
            self.save_config()
            self.save_settings()
            
            # 清除缓存
            self._cache = {
                "config": None,
                "settings": None,
                "loaded_time": None,
                "config_mtime": 0,
                "settings_mtime": 0
            }
            
            logger.info(f"配置导入完成: {import_path}")
            return True
        except json.JSONDecodeError as e:
            logger.error(f"导入配置文件格式错误: {e}")
            return False
        except Exception as e:
            logger.error(f"配置导入失败: {e}")
            return False
    
    def reset_config(self) -> bool:
        """
        重置配置为默认值
        
        Returns:
            bool: 重置是否成功
        """
        try:
            # 重置配置
            self.config = {
                "version": "1.0.0",
                "directories": {
                    "tool_root": "${current_dir}",
                    "mod_root": "${current_dir}/File",
                    "source": "${mod_root}/source",
                    "output": "${mod_root}/output",
                    "logs": "${tool_root}/logs",
                    "rules": "${mod_root}/rule"
                }
            }
            
            # 重置设置
            self.settings = {
                "advanced_mode_enabled": False,
                "main_language": "全部",
                "process_granularity_enabled": True,
                "precheck_mechanism_enabled": True,
                "show_welcome_guide": True,
                "auto_open_output_folder": True
            }
            
            # 保存重置后的配置
            self.save_config()
            self.save_settings()
            
            # 清除缓存
            self._cache = {
                "config": None,
                "settings": None,
                "loaded_time": None,
                "config_mtime": 0,
                "settings_mtime": 0
            }
            
            self.loaded = False
            logger.info("配置已重置为默认值")
            return True
        except Exception as e:
            logger.error(f"配置重置失败: {e}")
            return False


# 创建全局配置管理器实例
config_manager = ConfigManager()

# 创建全局目录映射器实例
directory_mapper = DirectoryMapper()


# 便捷函数
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


def set_directory(directory_name: str, directory_path: str) -> bool:
    """
    设置目录路径的便捷函数
    
    Args:
        directory_name: 目录名称
        directory_path: 目录路径
        
    Returns:
        bool: 设置是否成功
    """
    return config_manager.set_directory(directory_name, directory_path)


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


def set_config(key: str, value: Any) -> bool:
    """
    设置配置项的便捷函数
    
    Args:
        key: 配置项键名
        value: 配置项值
        
    Returns:
        bool: 设置是否成功
    """
    return config_manager.set_config(key, value)


def get_source_directory(mode: str, source_type: str = "auto") -> Optional[str]:
    """
    获取源文件目录的便捷函数
    
    Args:
        mode: 模式类型 (extract/extend)
        source_type: 源类型 (auto/project/file)
        
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


def get_output_directory(mode: str, language: str = "English") -> Optional[str]:
    """
    获取输出目录的便捷函数
    
    Args:
        mode: 模式类型 (extract/extend)
        language: 语言类型 (English/Chinese)
        
    Returns:
        str: 输出目录路径
    """
    return directory_mapper.get_output_directory(mode, language)


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


def export_config(export_path: str) -> bool:
    """
    导出配置的便捷函数
    
    Args:
        export_path: 导出路径
        
    Returns:
        bool: 导出是否成功
    """
    return config_manager.export_config(export_path)


def import_config(import_path: str) -> bool:
    """
    导入配置的便捷函数
    
    Args:
        import_path: 导入路径
        
    Returns:
        bool: 导入是否成功
    """
    return config_manager.import_config(import_path)


def reset_config() -> bool:
    """
    重置配置的便捷函数
    
    Returns:
        bool: 重置是否成功
    """
    return config_manager.reset_config()