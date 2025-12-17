#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据管理系统

该模块负责集中管理测试数据，包括测试数据的加载、验证和访问接口。
"""

import os
import json
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.common.logger_utils import get_logger

# 初始化日志记录器
logger = get_logger(__name__)


class TestDataManager:
    """
    测试数据管理器类，用于集中管理和访问测试数据
    """

    def __init__(self, test_data_dir: Optional[str] = None):
        """
        初始化测试数据管理器

        Args:
            test_data_dir: str - 测试数据目录路径，默认为项目根目录下的test_data
        """
        self.test_data_dir = test_data_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "test_data"
        )
        self._test_data_cache: Dict[str, Any] = {}
        self._load_all_test_data()

    def _load_all_test_data(self):
        """
        加载所有测试数据到缓存中
        """
        if not os.path.exists(self.test_data_dir):
            logger.warning(f"测试数据目录不存在: {self.test_data_dir}")
            return

        for root, _, files in os.walk(self.test_data_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.test_data_dir)
                try:
                    if file.endswith(".json"):
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                    elif file.endswith(".yaml") or file.endswith(".yml"):
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = yaml.safe_load(f)
                    elif file.endswith(".txt"):
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = f.read()
                    else:
                        continue  # 跳过不支持的文件类型

                    self._test_data_cache[relative_path] = data
                    logger.debug(f"加载测试数据: {relative_path}")
                except Exception as e:
                    logger.error(f"加载测试数据失败: {relative_path} - {str(e)}")

    def get_test_data(self, data_path: str, default: Any = None) -> Any:
        """
        获取指定路径的测试数据

        Args:
            data_path: str - 测试数据相对路径(相对于test_data目录)
            default: Any - 默认值，当数据不存在时返回

        Returns:
            Any - 测试数据
        """
        # 先从缓存中获取数据
        data = self._test_data_cache.get(data_path, default)
        
        # 如果缓存中没有数据，尝试从文件加载
        if data is default:
            file_path = os.path.join(self.test_data_dir, data_path)
            if os.path.exists(file_path):
                try:
                    if data_path.endswith(".json"):
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                    elif data_path.endswith(".yaml") or data_path.endswith(".yml"):
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = yaml.safe_load(f)
                    elif data_path.endswith(".txt"):
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = f.read()
                    
                    # 更新缓存
                    self._test_data_cache[data_path] = data
                    logger.debug(f"从文件加载测试数据: {data_path}")
                except Exception as e:
                    logger.error(f"从文件加载测试数据失败: {data_path} - {str(e)}")
                    data = default
        
        return data

    def save_test_data(self, data_path: str, data: Any) -> bool:
        """
        保存测试数据到指定路径

        Args:
            data_path: str - 测试数据相对路径(相对于test_data目录)
            data: Any - 要保存的测试数据

        Returns:
            bool - 保存是否成功
        """
        file_path = os.path.join(self.test_data_dir, data_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            if data_path.endswith(".json"):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif data_path.endswith(".yaml") or data_path.endswith(".yml"):
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
            elif data_path.endswith(".txt"):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(str(data))
            else:
                logger.error(f"不支持的测试数据文件类型: {data_path}")
                return False

            self._test_data_cache[data_path] = data
            logger.info(f"保存测试数据: {data_path}")
            return True
        except Exception as e:
            logger.error(f"保存测试数据失败: {data_path} - {str(e)}")
            return False

    def list_test_data(self, prefix: str = "") -> List[str]:
        """
        列出所有测试数据路径

        Args:
            prefix: str - 路径前缀，用于过滤

        Returns:
            List[str] - 测试数据路径列表
        """
        return [
            path for path in self._test_data_cache.keys()
            if path.startswith(prefix)
        ]

    def validate_test_data(self, data_path: str, schema: Dict[str, Any]) -> bool:
        """
        验证测试数据是否符合指定的schema

        Args:
            data_path: str - 测试数据相对路径
            schema: Dict[str, Any] - 验证schema

        Returns:
            bool - 验证是否通过
        """
        data = self.get_test_data(data_path)
        if data is None:
            logger.error(f"测试数据不存在: {data_path}")
            return False

        try:
            # 简单的schema验证，检查必填字段
            for key, expected_type in schema.items():
                if key not in data:
                    logger.error(f"测试数据缺少必填字段: {key} in {data_path}")
                    return False
                if not isinstance(data[key], expected_type):
                    logger.error(f"测试数据字段类型错误: {key} 应为 {expected_type.__name__}，实际为 {type(data[key]).__name__} in {data_path}")
                    return False
            return True
        except Exception as e:
            logger.error(f"验证测试数据失败: {data_path} - {str(e)}")
            return False

    def create_test_data_structure(self):
        """
        创建默认的测试数据目录结构
        """
        # 创建基本目录结构
        directories = [
            "code_samples/java",
            "code_samples/python",
            "mapping_rules",
            "test_cases/extract_mode",
            "test_cases/extend_mode",
            "expected_results",
            "configuration"
        ]

        for directory in directories:
            dir_path = os.path.join(self.test_data_dir, directory)
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"创建测试数据目录: {directory}")

        # 创建示例测试数据文件
        sample_data = {
            "description": "示例测试数据",
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "data": {
                "sample_key": "sample_value",
                "sample_list": [1, 2, 3],
                "sample_dict": {
                    "nested_key": "nested_value"
                }
            }
        }

        self.save_test_data("configuration/sample_config.json", sample_data)
        logger.info("创建示例测试数据完成")

    def clear_cache(self):
        """
        清除测试数据缓存
        """
        self._test_data_cache.clear()
        logger.debug("清除测试数据缓存")

    def reload_test_data(self):
        """
        重新加载所有测试数据
        """
        self.clear_cache()
        self._load_all_test_data()
        logger.info("重新加载测试数据完成")


# 单例实例
_test_data_manager_instance: Optional[TestDataManager] = None


def get_test_data_manager() -> TestDataManager:
    """
    获取测试数据管理器的单例实例

    Returns:
        TestDataManager - 测试数据管理器实例
    """
    global _test_data_manager_instance
    if _test_data_manager_instance is None:
        _test_data_manager_instance = TestDataManager()
    return _test_data_manager_instance


def get_test_data(data_path: str, default: Any = None) -> Any:
    """
    便捷函数：获取测试数据

    Args:
        data_path: str - 测试数据相对路径
        default: Any - 默认值

    Returns:
        Any - 测试数据
    """
    return get_test_data_manager().get_test_data(data_path, default)


def save_test_data(data_path: str, data: Any) -> bool:
    """
    便捷函数：保存测试数据

    Args:
        data_path: str - 测试数据相对路径
        data: Any - 测试数据

    Returns:
        bool - 保存是否成功
    """
    return get_test_data_manager().save_test_data(data_path, data)
