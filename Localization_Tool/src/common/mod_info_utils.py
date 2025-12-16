#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mod_info.json 工具模块

该模块提供统一的mod_info.json处理功能，包括读取、写入、验证和更新等。
"""

import os
import json
from typing import Dict, Any, List, Optional


def read_mod_info(mod_path: str) -> Dict[str, Any]:
    """
    读取mod_info.json文件，返回解析后的字典

    支持在mod_path根目录和mod子目录下查找mod_info.json文件

    Args:
        mod_path: mod文件夹路径

    Returns:
        dict: 包含id、name、version等信息的字典，如果没有找到则返回空字典
    """
    try:
        # 检查mod_path是否存在
        if not os.path.exists(mod_path) or not os.path.isdir(mod_path):
            return {}

        # 定义可能的mod_info.json路径
        possible_paths: List[str] = [
            os.path.join(mod_path, "mod_info.json"),  # 根目录
        ]

        # 检查mod子目录
        for item in os.listdir(mod_path):
            item_path = os.path.join(mod_path, item)
            if os.path.isdir(item_path):
                possible_paths.append(os.path.join(item_path, "mod_info.json"))

        # 查找并读取mod_info.json
        mod_info_path: Optional[str] = None
        for path in possible_paths:
            if os.path.exists(path) and os.path.isfile(path):
                mod_info_path = path
                break

        if not mod_info_path:
            return {}

        # 读取并解析mod_info.json
        with open(mod_info_path, "r", encoding="utf-8") as f:
            # 读取文件内容并移除注释
            content = ''
            for line in f:
                # 移除行内注释
                line = line.split('#')[0].strip()
                if line:
                    content += line + ' '
            
            # 修复JSON语法错误：移除尾随逗号
            import re
            content = re.sub(r',\s*\]', r']', content)
            content = re.sub(r',\s*\}', r'}', content)
            content = re.sub(r',\s*\},', r'},', content)
            
            mod_info = json.loads(content)

        return mod_info
    except Exception as e:
        print(f"[WARN]  读取mod_info.json失败: {mod_path} - {str(e)}")
        return {}


def write_mod_info(mod_path: str, mod_info: Dict[str, Any]) -> bool:
    """
    写入mod_info.json文件

    Args:
        mod_path: mod文件夹路径
        mod_info: 要写入的mod_info字典

    Returns:
        bool: 是否成功写入
    """
    try:
        # 确保mod_path存在
        if not os.path.exists(mod_path):
            os.makedirs(mod_path, exist_ok=True)

        # 定义mod_info.json路径
        mod_info_path = os.path.join(mod_path, "mod_info.json")

        # 写入mod_info.json
        with open(mod_info_path, "w", encoding="utf-8") as f:
            json.dump(mod_info, f, ensure_ascii=False, indent=2)

        print(f"[OK] 成功写入mod_info.json: {mod_info_path}")
        return True
    except Exception as e:
        print(f"[ERROR] 写入mod_info.json失败: {mod_path} - {str(e)}")
        return False


def validate_mod_info(mod_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证mod_info.json的完整性，确保包含必要字段

    Args:
        mod_info: mod_info字典

    Returns:
        Dict[str, Any]: 验证结果，包含status和message字段
    """
    # 定义必要字段
    required_fields = ["id", "name", "version"]
    
    # 检查必要字段是否存在
    missing_fields = [field for field in required_fields if field not in mod_info]
    
    if missing_fields:
        return {
            "status": "fail",
            "message": f"缺少必要字段: {', '.join(missing_fields)}",
            "missing_fields": missing_fields
        }
    
    # 检查字段类型
    field_types = {
        "id": str,
        "name": str,
        "version": str
    }
    
    invalid_types = []
    for field, expected_type in field_types.items():
        if field in mod_info and not isinstance(mod_info[field], expected_type):
            invalid_types.append(f"{field} 应为 {expected_type.__name__} 类型")
    
    if invalid_types:
        return {
            "status": "fail",
            "message": f"字段类型错误: {', '.join(invalid_types)}",
            "invalid_types": invalid_types
        }
    
    return {
        "status": "success",
        "message": "mod_info.json验证通过"
    }


def update_mod_info(mod_path: str, updates: Dict[str, Any]) -> bool:
    """
    更新mod_info.json文件中的字段

    Args:
        mod_path: mod文件夹路径
        updates: 要更新的字段字典

    Returns:
        bool: 是否成功更新
    """
    try:
        # 读取现有mod_info
        mod_info = read_mod_info(mod_path)
        
        # 如果mod_info不存在，创建新的
        if not mod_info:
            mod_info = {}
        
        # 更新字段
        mod_info.update(updates)
        
        # 验证更新后的mod_info
        validation_result = validate_mod_info(mod_info)
        if validation_result["status"] != "success":
            print(f"[ERROR] 更新mod_info.json失败: {validation_result['message']}")
            return False
        
        # 写入更新后的mod_info
        return write_mod_info(mod_path, mod_info)
    except Exception as e:
        print(f"[ERROR] 更新mod_info.json失败: {mod_path} - {str(e)}")
        return False


def get_mod_id(mod_path: str) -> str:
    """
    从mod_info.json获取mod_id

    Args:
        mod_path: mod文件夹路径

    Returns:
        str: mod_id，如果没有找到则返回空字符串
    """
    mod_info = read_mod_info(mod_path)
    return mod_info.get("id", "")


def get_mod_name(mod_path: str) -> str:
    """
    从mod_info.json获取mod_name

    Args:
        mod_path: mod文件夹路径

    Returns:
        str: mod_name，如果没有找到则返回空字符串
    """
    mod_info = read_mod_info(mod_path)
    return mod_info.get("name", "")


def get_mod_version(mod_path: str) -> str:
    """
    从mod_info.json获取mod_version

    Args:
        mod_path: mod文件夹路径

    Returns:
        str: mod_version，如果没有找到则返回空字符串
    """
    mod_info = read_mod_info(mod_path)
    return mod_info.get("version", "")


def generate_mod_info(mod_id: str, mod_name: str, version: str, **kwargs) -> Dict[str, Any]:
    """
    生成标准的mod_info.json字典

    Args:
        mod_id: mod_id
        mod_name: mod_name
        version: mod_version
        **kwargs: 其他可选字段

    Returns:
        Dict[str, Any]: 标准的mod_info字典
    """
    mod_info = {
        "id": mod_id,
        "name": mod_name,
        "version": version
    }
    
    # 添加其他可选字段
    mod_info.update(kwargs)
    
    return mod_info


def find_mods_with_mod_info(directory: str) -> List[Dict[str, Any]]:
    """
    查找目录下所有包含有效mod_info.json的mod文件夹

    Args:
        directory: 要搜索的目录

    Returns:
        List[Dict[str, Any]]: 包含mod_path和mod_info的字典列表
    """
    mods = []
    
    try:
        # 遍历目录
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file == "mod_info.json":
                    mod_path = root
                    mod_info = read_mod_info(mod_path)
                    if mod_info:
                        # 验证mod_info
                        validation_result = validate_mod_info(mod_info)
                        if validation_result["status"] == "success":
                            mods.append({
                                "mod_path": mod_path,
                                "mod_info": mod_info
                            })
        
        return mods
    except Exception as e:
        print(f"[ERROR] 查找mods失败: {directory} - {str(e)}")
        return []


def batch_update_mod_info(mods: List[Dict[str, Any]], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    批量更新多个mod的mod_info.json

    Args:
        mods: 包含mod_path和mod_info的字典列表
        updates: 要更新的字段字典

    Returns:
        Dict[str, Any]: 更新结果，包含成功数和失败数
    """
    success_count = 0
    fail_count = 0
    fail_reasons = []
    
    for mod in mods:
        mod_path = mod["mod_path"]
        if update_mod_info(mod_path, updates):
            success_count += 1
        else:
            fail_count += 1
            fail_reasons.append(mod_path)
    
    return {
        "success_count": success_count,
        "fail_count": fail_count,
        "fail_reasons": fail_reasons
    }


def merge_mod_info(base_mod_info: Dict[str, Any], update_mod_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并两个mod_info字典，保留base_mod_info的字段，仅更新update_mod_info中存在的字段

    Args:
        base_mod_info: 基础mod_info字典
        update_mod_info: 要合并的mod_info字典

    Returns:
        Dict[str, Any]: 合并后的mod_info字典
    """
    merged = base_mod_info.copy()
    merged.update(update_mod_info)
    return merged


def check_mod_info_exists(mod_path: str) -> bool:
    """
    检查mod_info.json是否存在

    Args:
        mod_path: mod文件夹路径

    Returns:
        bool: 是否存在
    """
    mod_info_path = os.path.join(mod_path, "mod_info.json")
    return os.path.exists(mod_info_path)


def copy_mod_info(source_mod_path: str, target_mod_path: str) -> bool:
    """
    复制mod_info.json从源mod到目标mod

    Args:
        source_mod_path: 源mod路径
        target_mod_path: 目标mod路径

    Returns:
        bool: 是否成功复制
    """
    try:
        # 读取源mod_info
        source_mod_info = read_mod_info(source_mod_path)
        if not source_mod_info:
            print(f"[ERROR] 源mod_info.json不存在或无效: {source_mod_path}")
            return False
        
        # 写入目标mod_info
        return write_mod_info(target_mod_path, source_mod_info)
    except Exception as e:
        print(f"[ERROR] 复制mod_info.json失败: {source_mod_path} -> {target_mod_path} - {str(e)}")
        return False