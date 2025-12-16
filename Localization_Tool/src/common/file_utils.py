#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件工具模块

该模块包含文件夹创建、重命名、移动、备份等文件操作功能。
"""

import os
import shutil
import json
import re
import time
import gc
import platform
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

# 常量定义
BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LANGUAGE_FOLDERS = ["Chinese", "English"]
MAIN_DIRECTORIES = ["source", "source_backup"]

# 定义支持的本地化模式
LOCALIZATION_MODES = ["extend", "translate"]


def ensure_directory_exists(directory: str) -> bool:
    """
    确保目录存在，如果不存在则创建

    Args:
        directory: 目录路径

    Returns:
        bool: 是否成功创建或目录已存在
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"[ERROR] 创建目录失败: {directory} - {e}")
        return False


def create_folders(base_path: str, mode: str) -> bool:
    """
    根据模式创建必要的文件夹

    Args:
        base_path: 基础路径
        mode: 模式(Extract或Extend)

    Returns:
        bool: 是否成功创建
    """
    try:
        # 只创建必要的文件夹，根据用户要求，不再创建多余的文件夹
        # 所有必要的文件夹已在main.py中创建
        return True
    except Exception as e:
        print(f"[ERROR] 创建文件夹失败: {e}")
        return False


def rename_mod_folders(file_path: str) -> bool:
    """
    根据mod_info.json重命名模组文件夹

    Args:
        file_path: 文件路径

    Returns:
        bool: 是否成功重命名
    """
    print(f"\n===== 开始重命名 {os.path.basename(file_path)} 下的模组文件夹 =====")
    
    try:
        # 检查目录是否存在
        if not os.path.exists(file_path) or not os.path.isdir(file_path):
            print(f"[ERROR] 目录不存在: {file_path}")
            return False
        
        # 收集当前目录下的mod_info信息，按mod_id分组
        mod_info_dict: Dict[str, List[Dict[str, Any]]] = {}
        folders_info: List[Dict[str, Any]] = []
        
        # 直接处理当前目录下的mod文件夹
        items = os.listdir(file_path)
        for item_name in items:
            item_path = os.path.join(file_path, item_name)
            if os.path.isdir(item_path):
                # 跳过固定目录结构
                fixed_dirs = ["src", "jars", "Chinese", "English"]
                if item_name in fixed_dirs:
                    print(f"[INFO] 跳过固定目录: {item_path}")
                    continue
                
                # 读取mod_info.json
                mod_info = read_mod_info(item_path)
                if mod_info:
                    # 获取mod_id
                    mod_id = mod_info.get("id", "")
                    if not mod_id:
                        # 尝试使用文件夹名作为mod_id
                        mod_id = item_name
                        print(f"[WARN]  模组文件夹 {item_name} 缺少id信息，使用文件夹名作为mod_id")
                    
                    # 记录文件夹信息
                    folders_info.append({
                        "folder_name": item_name,
                        "folder_path": item_path,
                        "mod_info": mod_info,
                        "mod_id": mod_id,
                        "parent_dir": os.path.basename(file_path)
                    })
                    
                    # 按mod_id分组
                    if mod_id not in mod_info_dict:
                        mod_info_dict[mod_id] = []
                    mod_info_dict[mod_id].append({
                        "folder_name": item_name,
                        "folder_path": item_path,
                        "mod_info": mod_info,
                        "parent_dir": os.path.basename(file_path)
                    })
                else:
                    print(f"[WARN]  未能读取 {item_name} 的mod_info.json")
        
        print(f"[INFO] 共收集到 {len(folders_info)} 个模组文件夹信息，按 {len(mod_info_dict)} 个mod_id分组")
        
        # 如果没有收集到任何文件夹信息，直接返回
        if not folders_info:
            print(f"[INFO] 未在 {file_path} 下找到需要重命名的模组文件夹")
            return True
        
        # 定义获取新文件夹名称的辅助函数
        def get_new_folder_name(folder_info: Dict[str, Any], mod_info_dict: Dict[str, List[Dict[str, Any]]]) -> str:
            """根据文件夹信息获取新的文件夹名称"""
            mod_info = folder_info["mod_info"]
            mod_id = folder_info["mod_id"]
            
            # 使用name + 空格 + version格式构建新的文件夹名称
            if mod_info.get("name") and mod_info.get("version"):
                new_folder_name = f"{mod_info['name']} {mod_info['version']}"
            elif mod_info.get("name"):
                new_folder_name = mod_info["name"]
            elif mod_info.get("version"):
                new_folder_name = f"{mod_id if mod_id else folder_info['folder_name']} {mod_info['version']}"
            else:
                # 回退到使用mod_id格式
                new_folder_name = mod_id.lower().replace(" ", "_").replace("-", "_")
            return new_folder_name
        
        # 定义重命名单个文件夹的辅助函数
        def rename_single_folder(folder_path: str, old_name: str, new_name: str) -> bool:
            """重命名单个文件夹，实现重试机制"""
            new_folder_path = os.path.join(os.path.dirname(folder_path), new_name)
            
            # 如果新路径已经存在，跳过
            if os.path.exists(new_folder_path):
                print(f"[WARN]  文件夹已存在: {new_folder_path}")
                return True
            
            # 执行重命名，实现重试机制
            max_retries = 5
            retry_count = 0
            renamed = False
            
            while retry_count < max_retries and not renamed:
                try:
                    # 尝试释放资源
                    gc.collect()
                    time.sleep(0.5)  # 每次重试前等待0.5秒
                    
                    os.rename(folder_path, new_folder_path)
                    print(f"[OK] 成功重命名文件夹: {old_name} -> {new_name}")
                    renamed = True
                except PermissionError as e:
                    retry_count += 1
                    wait_time = 2 ** retry_count  # 指数退避策略
                    if retry_count < max_retries:
                        print(f"[WARN]  重命名 {old_name} 时遇到权限问题，{wait_time}秒后重试...")
                        time.sleep(wait_time)
                    else:
                        print(f"[ERROR] 重命名 {old_name} 失败，已重试 {max_retries} 次: {e}")
                        return False
                except Exception as e:
                    print(f"[ERROR] 重命名文件夹失败: {old_name} - {e}")
                    return False
            
            return renamed
        
        # 第二次遍历：根据mod_info_dict重命名文件夹
        success_count = 0
        skip_count = 0
        fail_count = 0
        
        for folder_info in folders_info:
            folder_name = folder_info["folder_name"]
            folder_path = folder_info["folder_path"]
            
            # 检查当前文件夹是否在要处理的file_path下
            if not folder_path.startswith(file_path):
                continue
            
            # 跳过src目录下的文件夹，保持固定的目录结构
            parent_dir_name = os.path.basename(os.path.dirname(folder_path))
            if parent_dir_name == "src":
                print(f"[INFO] 跳过src目录下的文件夹 {folder_name}，保持固定的目录结构")
                skip_count += 1
                continue
            
            # 跳过jar目录下的文件夹，保持固定的目录结构
            if parent_dir_name == "jar":
                print(f"[INFO] 跳过jar目录下的文件夹 {folder_name}，保持固定的目录结构")
                skip_count += 1
                continue
            
            # 获取新的文件夹名称
            new_folder_name = get_new_folder_name(folder_info, mod_info_dict)
            
            # 如果没有id或name，跳过
            if not new_folder_name:
                print(f"[WARN]  无法生成新的文件夹名称: {folder_path}")
                skip_count += 1
                continue
            
            # 如果新名称与原名称相同，跳过
            if new_folder_name == folder_name:
                print(f"[INFO] 文件夹 {folder_name} 名称已正确，无需重命名")
                skip_count += 1
                continue
            
            # 执行重命名
            if rename_single_folder(folder_path, folder_name, new_folder_name):
                success_count += 1
            else:
                fail_count += 1
        
        # 输出重命名结果统计
        print(f"\n===== 重命名完成 =====")
        print(f"[INFO] 总文件夹数: {len(folders_info)}")
        print(f"[INFO] 成功重命名: {success_count}")
        print(f"[INFO] 跳过重命名: {skip_count}")
        print(f"[INFO] 重命名失败: {fail_count}")
        
        # 如果有失败的情况，返回False
        return fail_count == 0
    
    except Exception as e:
        print(f"[ERROR] 重命名模组文件夹失败: {e}")
        return False


def extract_pure_mod_name(folder_name: str) -> str:
    """
    从文件夹名中提取纯净的模组名称(去掉末尾可能的版本号)
    
    Args:
        folder_name: 文件夹名
        
    Returns:
        str: 纯净的模组名称
    """
    # 匹配更复杂的版本号格式，包括：
    # - 简单版本号：1.0, 1.2.3
    # - 带字母的版本号：1.0a, 2.0.0b
    # - 带预发布标签的版本号：1.0.0-alpha, 2.0.0-beta.1
    # - 带构建元数据的版本号：1.0.0+build.1
    # 注意：只匹配至少包含一个点号的版本号，避免匹配文件名末尾的单个数字
    version_pattern = r"\s+([0-9]+\.[0-9]+(?:\.[0-9]+)*[a-zA-Z]*(?:-[0-9A-Za-z.]+)*(?:\+[0-9A-Za-z.]+)*)\s*$"
    pure_name = folder_name
    
    match = re.search(version_pattern, folder_name)
    if match:
        # 提取纯净的模组名称(去掉末尾的版本号)
        pure_name = folder_name[:match.start()]
    
    return pure_name


def find_folder_by_mod_id(directory: str, mod_id: str, language: Optional[str] = None) -> Dict[str, Any]:
    """
    根据 mod_id 查找对应的文件夹信息
    
    Args:
        directory: 要搜索的目录
        mod_id: 模组 ID
        language: 语言类型(可选，如 "Chinese" 或 "English")
        
    Returns:
        dict: 包含文件夹路径、名称、mod_info等信息的字典，如果未找到则返回空字典
    """
    print(f"\n===== 根据 mod_id 查找文件夹: {mod_id} =====")
    print(f"[INFO] 搜索目录: {directory}")
    print(f"[INFO] 语言过滤: {language if language else '所有语言'}")
    
    # 存储匹配的文件夹信息
    matching_folders: List[Dict[str, Any]] = []
    
    # 递归搜索函数
    def search_folder(current_dir: str) -> None:
        """递归搜索当前目录下的所有文件夹"""
        try:
            items = os.listdir(current_dir)
        except Exception as e:
            print(f"[ERROR] 读取目录内容失败: {current_dir} - {e}")
            return
        
        for item_name in items:
            item_path = os.path.join(current_dir, item_name)
            if os.path.isdir(item_path):
                # 获取当前目录的语言类型
                current_dir_name = os.path.basename(current_dir)
                folder_language: Optional[str] = None
                
                # 检查当前目录是否为语言文件夹
                if current_dir_name in LANGUAGE_FOLDERS:
                    folder_language = current_dir_name
                
                # 检查是否为mod文件夹(包含mod_info.json)
                mod_info = read_mod_info(item_path)
                if mod_info:
                    # 获取mod_id
                    current_mod_id = mod_info.get("id", "")
                    if not current_mod_id:
                        # 尝试使用文件夹名作为mod_id
                        current_mod_id = item_name
                    
                    # 检查mod_id是否匹配
                    if current_mod_id == mod_id:
                        # 检查语言是否匹配
                        if not language or folder_language == language:
                            # 记录匹配的文件夹信息
                            matching_folders.append({
                                "folder_name": item_name,
                                "folder_path": item_path,
                                "mod_info": mod_info,
                                "mod_id": current_mod_id,
                                "language": folder_language,
                                "parent_dir": current_dir_name
                            })
                            print(f"[OK] 找到匹配的文件夹: {item_path} (语言: {folder_language})")
                
                # 递归搜索子目录
                search_folder(item_path)
    
    # 开始搜索
    search_folder(directory)
    
    print(f"[INFO] 共找到 {len(matching_folders)} 个匹配的文件夹")
    
    # 如果找到多个匹配的文件夹，返回第一个
    if matching_folders:
        return matching_folders[0]
    
    return {}


def collect_mods(directory: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    递归收集目录下所有mod文件夹的mod_id映射
    
    Args:
        directory: 要收集的目录
        
    Returns:
        dict: mod_id到文件夹信息列表的映射
    """
    print(f"\n===== 收集 {os.path.basename(directory)} 下的mod文件夹信息 =====")
    
    mods: Dict[str, List[Dict[str, Any]]] = {}
    
    # 递归搜索函数
    def search_folder(current_dir: str) -> None:
        """递归搜索当前目录下的所有mod文件夹"""
        try:
            items = os.listdir(current_dir)
        except Exception as e:
            print(f"[ERROR] 读取目录内容失败: {current_dir} - {e}")
            return
        
        for item_name in items:
            item_path = os.path.join(current_dir, item_name)
            if os.path.isdir(item_path):
                # 检查是否为语言文件夹或主目录
                if item_name in LANGUAGE_FOLDERS or item_name in MAIN_DIRECTORIES:
                    # 递归搜索子目录
                    search_folder(item_path)
                else:
                    # 检查是否为mod文件夹(包含mod_info.json)
                    mod_info = read_mod_info(item_path)
                    mod_id = mod_info.get("id", "")
                    if mod_id:
                        # 获取文件夹语言
                        folder_language: Optional[str] = None
                        parent_dir = os.path.basename(os.path.dirname(item_path))
                        for lang in LANGUAGE_FOLDERS:
                            if lang in parent_dir:
                                folder_language = lang
                                break
                        
                        # 记录文件夹信息
                        folder_info = {
                            "folder_name": item_name,
                            "path": item_path,
                            "language": folder_language,
                            "mod_info": mod_info
                        }
                        
                        # 将文件夹信息添加到mods字典
                        if mod_id not in mods:
                            mods[mod_id] = []
                        mods[mod_id].append(folder_info)
                        print(f"[INFO] 收集到mod: {item_name} (id: {mod_id}, language: {folder_language})")
                    
                    # 递归搜索子目录
                    search_folder(item_path)
    
    # 开始搜索
    search_folder(directory)
    
    print(f"[INFO] 共收集到 {len(mods)} 个mod_id，对应 {sum(len(folders) for folders in mods.values())} 个文件夹")
    
    return mods


# 保留原函数名作为别名，确保向后兼容
_collect_mods = collect_mods

def get_folder_by_mod_id(base_path: str, mod_id: str, language: Optional[str] = None, mode: Optional[str] = None) -> Dict[str, Any]:
    """
    根据 mod_id 获取对应的文件夹信息
    
    作为公共接口，方便其他模块使用。支持指定语言和模式(Extract 或 Extend)。
    
    Args:
        base_path: 基础路径(项目根目录)
        mod_id: 模组 ID
        language: 语言类型(可选，如 "Chinese" 或 "English")
        mode: 模式(可选，如 "Extract" 或 "Extend")
        
    Returns:
        dict: 包含文件夹路径、名称、mod_info等信息的字典，如果未找到则返回空字典
    """
    print(f"\n===== 根据 mod_id 获取文件夹信息: {mod_id} =====")
    print(f"[INFO] 基础路径: {base_path}")
    print(f"[INFO] 语言: {language if language else '所有语言'}")
    print(f"[INFO] 模式: {mode if mode else '所有模式'}")
    
    # 构建搜索目录
    search_dir = base_path
    if mode:
        from src.common.config_utils import get_directory
        search_dir = get_directory("output")
    
    # 使用find_folder_by_mod_id函数查找文件夹
    return find_folder_by_mod_id(search_dir, mod_id, language)


def restore_backup(backup_path: str, target_path: str) -> bool:
    """
    从备份恢复文件夹

    Args:
        backup_path: 备份路径
        target_path: 目标路径

    Returns:
        bool: 是否成功恢复
    """
    print("\n===== 清理并从备份恢复文件夹 =====")
    
    try:
        # 检查备份路径是否存在
        if not os.path.exists(backup_path):
            print(f"[ERROR] 备份路径不存在: {backup_path}")
            return False
        
        # 1. 检查target_path是否存在
        if not os.path.exists(target_path):
            os.makedirs(target_path, exist_ok=True)
        
        # 2. 递归收集目标路径下所有mod文件夹的mod_id映射
        target_mods = collect_mods(target_path)
        print(f"[LIST] 收集到目标文件夹 {len(target_mods)} 个mod_id")
        
        # 3. 递归收集备份路径下所有mod文件夹的mod_id映射
        backup_mods = collect_mods(backup_path)
        print(f"[LIST] 收集到备份文件夹 {len(backup_mods)} 个mod_id")
        
        # 4. 基于mod_id匹配，恢复备份
        for mod_id, target_mod_list in target_mods.items():
            if mod_id in backup_mods:
                # 处理所有匹配的文件夹
                backup_mod_list = backup_mods[mod_id]
                
                # 匹配目标文件夹和备份文件夹
                for target_mod in target_mod_list:
                    # 查找相同语言的备份文件夹
                    matching_backup_mod: Optional[Dict[str, Any]] = None
                    for backup_mod in backup_mod_list:
                        if target_mod["language"] == backup_mod["language"]:
                            matching_backup_mod = backup_mod
                            break
                    
                    if not matching_backup_mod:
                        # 如果没有找到相同语言的备份文件夹，使用第一个备份文件夹
                        matching_backup_mod = backup_mod_list[0]
                        print(f"[WARN]  未找到相同语言的备份文件夹，使用第一个备份文件夹")
                    
                    mod_target_path = target_mod["path"]
                    mod_backup_path = matching_backup_mod["path"]
                    
                    print(f"[LINK] 匹配到mod_id: {mod_id}")
                    print(f"   目标文件夹: {os.path.basename(mod_target_path)} (语言: {target_mod['language']})")
                    print(f"   备份文件夹: {os.path.basename(mod_backup_path)} (语言: {matching_backup_mod['language']})")
                    
                    # 5. 直接使用备份路径和目标路径，不再添加src子文件夹
                    # 因为collect_mods函数已经返回了完整的mod文件夹路径
                    
                    # 6. 如果目标路径存在，先删除
                    if os.path.exists(mod_target_path):
                        shutil.rmtree(mod_target_path)
                        print(f"OK 删除原有{mod_target_path}文件夹")
                    
                    # 7. 从备份恢复文件夹
                    if os.path.exists(mod_backup_path):
                        shutil.copytree(mod_backup_path, mod_target_path)
                        print(f"OK 恢复{mod_backup_path}文件夹 -> {mod_target_path}")
                    else:
                        print(f"[WARN]  备份中没有{mod_backup_path}文件夹")
            else:
                print(f"[WARN]  没有找到mod_id为{mod_id}的备份文件夹")
        
        return True
    except Exception as e:
        print(f"[ERROR] 恢复备份失败: {e}")
        return False


def cleanup_nested_src_directories(source_path: str) -> bool:
    """
    清理嵌套的src目录结构

    Args:
        source_path: 要清理的源路径

    Returns:
        bool: 是否成功清理
    """
    print("\n===== 清理嵌套的src目录 =====")
    
    try:
        # 检查源路径是否存在
        if not os.path.exists(source_path):
            print(f"[ERROR] 源路径不存在: {source_path}")
            return False
        
        # 记录是否有清理操作
        has_cleaned = False
        
        # 存储需要处理的嵌套src目录路径
        nested_src_paths: List[str] = []
        
        # 第一遍：收集所有嵌套的src目录
        # 例如：Chinese/src/ModName/src 或 English/src/ModName/src
        for root, dirs, files in os.walk(source_path):
            # 检查当前目录是否是 src 目录
            if os.path.basename(root) == "src":
                # 检查 src 目录下是否还有 src 目录
                for sub_dir in dirs:
                    if sub_dir == "src":
                        # 计算嵌套的src目录路径
                        nested_src_path = os.path.join(root, sub_dir)
                        nested_src_paths.append(nested_src_path)
        
        # 如果没有发现嵌套的src目录，直接返回
        if not nested_src_paths:
            print("[INFO] 未发现嵌套的src目录")
            return True
        
        # 第二遍：处理所有嵌套的src目录
        for nested_src_path in nested_src_paths:
            print(f"[CLEANUP] 发现嵌套的src目录: {nested_src_path}")
            
            # 检查嵌套src目录是否存在
            if not os.path.exists(nested_src_path):
                print(f"[WARN] 嵌套src目录不存在: {nested_src_path}")
                continue
            
            # 获取父级目录路径(即包含嵌套src的目录)
            parent_dir = os.path.dirname(nested_src_path)
            
            try:
                # 将嵌套src目录中的所有文件和子目录移动到父级目录
                for item in os.listdir(nested_src_path):
                    src_item = os.path.join(nested_src_path, item)
                    dst_item = os.path.join(parent_dir, item)
                    
                    # 如果目标文件/目录已存在，先删除
                    if os.path.exists(dst_item):
                        if os.path.isdir(dst_item):
                            shutil.rmtree(dst_item)
                        else:
                            os.remove(dst_item)
                    
                    # 移动文件/目录
                    shutil.move(src_item, dst_item)
                    print(f"[OK] 移动 {item} 到 {parent_dir}")
                
                # 删除空的嵌套src目录
                shutil.rmtree(nested_src_path)
                print(f"[OK] 删除空的嵌套src目录: {nested_src_path}")
                has_cleaned = True
            except Exception as e:
                print(f"[ERROR] 处理嵌套src目录 {nested_src_path} 失败: {e}")
                continue
        
        if has_cleaned:
            print("[SUCCESS] 嵌套src目录清理完成")
        else:
            print("[INFO] 嵌套src目录清理完成，未执行实际清理操作")
        
        return True
    except Exception as e:
        print(f"[ERROR] 清理嵌套src目录失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def fix_source_directory(source_path: str, backup_path: str) -> bool:
    """
    使用backup目录修复source目录

    Args:
        source_path: source目录路径
        backup_path: source_backup目录路径

    Returns:
        bool: 是否成功修复
    """
    print("\n===== 使用backup修复source目录 =====")
    
    try:
        # 检查source和backup路径是否存在
        if not os.path.exists(source_path):
            print(f"[ERROR] source路径不存在: {source_path}")
            return False
        
        if not os.path.exists(backup_path):
            print(f"[ERROR] backup路径不存在: {backup_path}")
            return False
        
        # 1. 获取差异报告
        differences = compare_source_with_backup(source_path, backup_path)
        
        # 2. 如果没有差异，直接返回成功
        total_diff = len(differences["missing_dirs"]) + len(differences["extra_dirs"]) + \
                     len(differences["missing_files"]) + len(differences["extra_files"]) + \
                     len(differences["different_files"])
        
        if total_diff == 0:
            print("[INFO] source目录与backup目录完全一致，无需修复")
            return True
        
        # 3. 开始修复
        print("\n===== 开始修复source目录 =====")
        
        # 3.1 创建缺失的目录
        for dir_path in differences["missing_dirs"]:
            full_dir_path = os.path.join(source_path, dir_path)
            os.makedirs(full_dir_path, exist_ok=True)
            print(f"OK 创建缺失的目录: {full_dir_path}")
        
        # 3.2 删除多余的目录
        for dir_path in differences["extra_dirs"]:
            full_dir_path = os.path.join(source_path, dir_path)
            shutil.rmtree(full_dir_path)
            print(f"OK 删除多余的目录: {full_dir_path}")
        
        # 3.3 恢复缺失的文件
        for file_path in differences["missing_files"]:
            source_file = os.path.join(source_path, file_path)
            backup_file = os.path.join(backup_path, file_path)
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(source_file), exist_ok=True)
            
            # 复制文件
            shutil.copy2(backup_file, source_file)
            print(f"OK 恢复缺失的文件: {file_path}")
        
        # 3.4 删除多余的文件
        for file_path in differences["extra_files"]:
            source_file = os.path.join(source_path, file_path)
            os.remove(source_file)
            print(f"OK 删除多余的文件: {file_path}")
        
        # 3.5 恢复内容不同的文件
        for file_path in differences["different_files"]:
            source_file = os.path.join(source_path, file_path)
            backup_file = os.path.join(backup_path, file_path)
            
            # 复制文件
            shutil.copy2(backup_file, source_file)
            print(f"OK 恢复内容不同的文件: {file_path}")
        
        # 4. 验证修复结果
        print("\n===== 验证修复结果 =====")
        final_diff = compare_source_with_backup(source_path, backup_path)
        final_total_diff = len(final_diff["missing_dirs"]) + len(final_diff["extra_dirs"]) + \
                          len(final_diff["missing_files"]) + len(final_diff["extra_files"]) + \
                          len(final_diff["different_files"])
        
        if final_total_diff == 0:
            print("[SUCCESS] source目录修复成功，与backup目录完全一致")
            return True
        else:
            print(f"[ERROR] source目录修复失败，仍有 {final_total_diff} 处差异")
            return False
    except Exception as e:
        print(f"[ERROR] 修复source目录失败: {e}")
        return False


def compare_source_with_backup(source_path: str, backup_path: str) -> Dict[str, List[str]]:
    """
    比较source和source_backup目录，检测是否存在差异

    Args:
        source_path: source目录路径
        backup_path: source_backup目录路径

    Returns:
        dict: 差异报告，包含缺失的目录、多余的目录、缺失的文件、多余的文件和内容不同的文件
    """
    print("\n===== 比较source与backup目录 =====")
    
    differences: Dict[str, List[str]] = {
        "missing_dirs": [],
        "extra_dirs": [],
        "missing_files": [],
        "extra_files": [],
        "different_files": []
    }
    
    try:
        # 检查源路径和备份路径是否存在
        if not os.path.exists(source_path):
            print(f"[ERROR] source路径不存在: {source_path}")
            return differences
        
        if not os.path.exists(backup_path):
            print(f"[ERROR] backup路径不存在: {backup_path}")
            return differences
        
        # 创建一个集合来存储所有备份文件路径
        backup_files: Set[str] = set()
        backup_dirs: Set[str] = set()
        
        # 遍历备份目录，收集所有文件和目录路径
        for root, dirs, files in os.walk(backup_path):
            # 计算相对路径
            rel_path = os.path.relpath(root, backup_path)
            if rel_path != ".":
                backup_dirs.add(rel_path)
            
            for file in files:
                file_path = os.path.relpath(os.path.join(root, file), backup_path)
                backup_files.add(file_path)
        
        # 创建一个集合来存储所有源文件路径
        source_files: Set[str] = set()
        source_dirs: Set[str] = set()
        
        # 遍历源目录，收集所有文件和目录路径
        for root, dirs, files in os.walk(source_path):
            # 计算相对路径
            rel_path = os.path.relpath(root, source_path)
            if rel_path != ".":
                source_dirs.add(rel_path)
            
            for file in files:
                file_path = os.path.relpath(os.path.join(root, file), source_path)
                source_files.add(file_path)
        
        # 比较目录结构
        # 找出source中缺失的目录(backup中有，source中没有)
        differences["missing_dirs"] = sorted(backup_dirs - source_dirs)
        # 只打印前10个差异，避免输出过多
        for i, dir_path in enumerate(differences["missing_dirs"]):
            if i < 10:
                print(f"[DIFF] 缺失目录: {dir_path}")
        if len(differences["missing_dirs"]) > 10:
            print(f"[DIFF] ... 还有 {len(differences['missing_dirs']) - 10} 个缺失目录")
        
        # 找出source中多余的目录(source中有，backup中没有)
        differences["extra_dirs"] = sorted(source_dirs - backup_dirs)
        # 只打印前10个差异，避免输出过多
        for i, dir_path in enumerate(differences["extra_dirs"]):
            if i < 10:
                print(f"[DIFF] 多余目录: {dir_path}")
        if len(differences["extra_dirs"]) > 10:
            print(f"[DIFF] ... 还有 {len(differences['extra_dirs']) - 10} 个多余目录")
        
        # 比较文件存在性
        # 找出source中缺失的文件(backup中有，source中没有)
        differences["missing_files"] = sorted(backup_files - source_files)
        # 只打印前10个差异，避免输出过多
        for i, file_path in enumerate(differences["missing_files"]):
            if i < 10:
                print(f"[DIFF] 缺失文件: {file_path}")
        if len(differences["missing_files"]) > 10:
            print(f"[DIFF] ... 还有 {len(differences['missing_files']) - 10} 个缺失文件")
        
        # 找出source中多余的文件(source中有，backup中没有)
        differences["extra_files"] = sorted(source_files - backup_files)
        # 只打印前10个差异，避免输出过多
        for i, file_path in enumerate(differences["extra_files"]):
            if i < 10:
                print(f"[DIFF] 多余文件: {file_path}")
        if len(differences["extra_files"]) > 10:
            print(f"[DIFF] ... 还有 {len(differences['extra_files']) - 10} 个多余文件")
        
        # 比较文件内容
        # 找出内容不同的文件(source和backup中都有，但内容不同)
        common_files = source_files & backup_files
        for file_path in common_files:
            # 需要将标准化后的路径转换回实际路径进行比较
            # 这里简化处理，直接比较原始文件
            source_file = os.path.join(source_path, file_path)
            backup_file = os.path.join(backup_path, file_path)
            
            # 检查文件是否存在(理论上应该存在，但保险起见)
            if not os.path.exists(source_file) or not os.path.exists(backup_file):
                continue
            
            # 比较文件大小
            if os.path.getsize(source_file) != os.path.getsize(backup_file):
                differences["different_files"].append(file_path)
                print(f"[DIFF] 内容不同: {file_path}(文件大小不同)")
                continue
            
            # 比较文件内容
            with open(source_file, "rb") as f1, open(backup_file, "rb") as f2:
                if f1.read() != f2.read():
                    differences["different_files"].append(file_path)
                    print(f"[DIFF] 内容不同: {file_path}")
        
        # 汇总差异
        total_diff = len(differences["missing_dirs"]) + len(differences["extra_dirs"]) + \
                     len(differences["missing_files"]) + len(differences["extra_files"]) + \
                     len(differences["different_files"])
        
        if total_diff == 0:
            print("[INFO] source目录与backup目录完全一致，没有差异")
        else:
            print(f"[INFO] 共发现 {total_diff} 处差异")
            print(f"   缺失目录: {len(differences['missing_dirs'])}")
            print(f"   多余目录: {len(differences['extra_dirs'])}")
            print(f"   缺失文件: {len(differences['missing_files'])}")
            print(f"   多余文件: {len(differences['extra_files'])}")
            print(f"   内容不同: {len(differences['different_files'])}")
        
        return differences
    except Exception as e:
        print(f"[ERROR] 比较目录失败: {e}")
        import traceback
        traceback.print_exc()
        return differences


def move_to_complete(source_path: str, complete_path: str, language: str, timestamp: str) -> bool:
    """
    将文件移动到Complete目录

    Args:
        source_path: 源路径
        complete_path: Complete目录路径
        language: 语言类型(Chinese或English)
        timestamp: 时间戳

    Returns:
        bool: 是否成功移动
    """
    try:
        # 构建目标路径，按照架构参考.md要求，将文件移入对应语言的子文件夹
        # 例如: project/Extract/File/20251211_153000_extract_English → project/Extract/Complete/English/
        target_path = os.path.join(complete_path, language)

        # 确保目标目录存在
        ensure_directory_exists(target_path)

        # 构建源文件夹名称，包含时间戳
        source_folder_name = f"{timestamp}_{os.path.basename(source_path)}"

        # 复制文件夹而非移动，保持原始位置不变
        shutil.copytree(source_path, os.path.join(target_path, source_folder_name), dirs_exist_ok=True)
        return True
    except Exception as e:
        print(f"[ERROR] 移动到Complete目录失败: {e}")
        return False


def safe_copy_file(src: str, dst: str) -> bool:
    """
    安全复制文件

    Args:
        src: 源文件路径
        dst: 目标文件路径

    Returns:
        bool: 是否成功复制
    """
    try:
        # 确保目标目录存在
        ensure_directory_exists(os.path.dirname(dst))

        # 复制文件
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print(f"[ERROR] 复制文件失败: {src} -> {dst} - {e}")
        return False


def safe_move_file(src: str, dst: str) -> bool:
    """
    安全移动文件

    Args:
        src: 源文件路径
        dst: 目标文件路径

    Returns:
        bool: 是否成功移动
    """
    try:
        # 确保目标目录存在
        ensure_directory_exists(os.path.dirname(dst))

        # 移动文件
        shutil.move(src, dst)
        return True
    except Exception as e:
        print(f"[ERROR] 移动文件失败: {src} -> {dst} - {e}")
        return False


def safe_delete_file(file_path: str) -> bool:
    """
    安全删除文件

    Args:
        file_path: 要删除的文件路径

    Returns:
        bool: 是否成功删除
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[OK] 成功删除文件: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"[ERROR] 删除文件失败: {file_path} - {e}")
        return False


def safe_delete_directory(directory: str) -> bool:
    """
    安全删除目录

    Args:
        directory: 要删除的目录路径

    Returns:
        bool: 是否成功删除
    """
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"[OK] 成功删除目录: {directory}")
            return True
        return False
    except Exception as e:
        print(f"[ERROR] 删除目录失败: {directory} - {e}")
        return False


def batch_copy_files(file_list: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    批量复制文件

    Args:
        file_list: 包含源文件路径和目标文件路径的字典列表，格式：[{"src": "源路径", "dst": "目标路径"}]

    Returns:
        dict: 包含成功数、失败数和失败原因的字典
    """
    success_count = 0
    fail_count = 0
    fail_reasons = []

    for file_info in file_list:
        src = file_info["src"]
        dst = file_info["dst"]
        if safe_copy_file(src, dst):
            success_count += 1
        else:
            fail_count += 1
            fail_reasons.append(f"复制失败: {src} -> {dst}")

    return {
        "success_count": success_count,
        "fail_count": fail_count,
        "fail_reasons": fail_reasons
    }


def batch_move_files(file_list: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    批量移动文件

    Args:
        file_list: 包含源文件路径和目标文件路径的字典列表，格式：[{"src": "源路径", "dst": "目标路径"}]

    Returns:
        dict: 包含成功数、失败数和失败原因的字典
    """
    success_count = 0
    fail_count = 0
    fail_reasons = []

    for file_info in file_list:
        src = file_info["src"]
        dst = file_info["dst"]
        if safe_move_file(src, dst):
            success_count += 1
        else:
            fail_count += 1
            fail_reasons.append(f"移动失败: {src} -> {dst}")

    return {
        "success_count": success_count,
        "fail_count": fail_count,
        "fail_reasons": fail_reasons
    }


def batch_delete_files(file_list: List[str]) -> Dict[str, Any]:
    """
    批量删除文件

    Args:
        file_list: 要删除的文件路径列表

    Returns:
        dict: 包含成功数、失败数和失败原因的字典
    """
    success_count = 0
    fail_count = 0
    fail_reasons = []

    for file_path in file_list:
        if safe_delete_file(file_path):
            success_count += 1
        else:
            fail_count += 1
            fail_reasons.append(f"删除失败: {file_path}")

    return {
        "success_count": success_count,
        "fail_count": fail_count,
        "fail_reasons": fail_reasons
    }


def open_directory(directory: str) -> bool:
    """
    打开指定的目录

    Args:
        directory: 目录路径

    Returns:
        bool: 是否成功打开
    """
    try:
        # 根据操作系统选择打开方式
        if platform.system() == 'Windows':
            # 在Windows上使用start命令打开目录
            subprocess.run(['cmd', '/c', 'start', directory], check=True, shell=True)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', directory], check=True)
        else:  # Linux
            subprocess.run(['xdg-open', directory], check=True)

        print(f"OK 成功打开目录: {directory}")
        return True
    except Exception as e:
        print(f"[ERROR] 打开目录失败: {e}")
        return False


def contains_chinese(string: str) -> bool:
    """
    检查字符串是否包含中文

    Args:
        string: 要检查的字符串

    Returns:
        bool: 是否包含中文
    """
    if not string:
        return False
    return any('\u4e00' <= c <= '\u9fff' for c in string)


def contains_chinese_in_file(file_path: str) -> bool:
    """
    检查文件是否包含中文

    Args:
        file_path: 文件路径

    Returns:
        bool: 是否包含中文
    """
    try:
        # 首先尝试用UTF-8编码读取文件
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含实际中文字符
            if contains_chinese(content):
                return True
            
            # 如果没有实际中文字符，检查是否包含Unicode转义序列
            if re.search(r'\\u[0-9a-fA-F]{4}', content):
                # 使用latin-1编码重新读取文件，避免自动转换Unicode转义序列
                with open(file_path, 'r', encoding='latin-1') as f:
                    raw_content = f.read()
                
                # 转换Unicode转义序列为实际字符
                def replace_unicode_escape(match):
                    """替换单个Unicode转义序列"""
                    try:
                        return bytes(match.group(0), 'latin-1').decode('unicode_escape')
                    except Exception:
                        return match.group(0)
                
                converted_content = re.sub(r'\\u[0-9a-fA-F]{4}', replace_unicode_escape, raw_content)
                return contains_chinese(converted_content)
            
            return False
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，使用latin-1编码读取
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            
            # 转换Unicode转义序列为实际字符
            def replace_unicode_escape(match):
                """替换单个Unicode转义序列"""
                try:
                    return bytes(match.group(0), 'latin-1').decode('unicode_escape')
                except Exception:
                    return match.group(0)
            
            converted_content = re.sub(r'\\u[0-9a-fA-F]{4}', replace_unicode_escape, content)
            return contains_chinese(converted_content)
    except Exception as e:
        print(f"[WARN]  检查文件是否包含中文失败: {file_path} - {e}")
        return False


def contains_chinese_in_src(src_path: str) -> bool:
    """
    检查src目录是否包含中文

    Args:
        src_path: src目录路径

    Returns:
        bool: 是否包含中文
    """
    try:
        # 遍历src目录下的所有Java和Kotlin文件
        for root, dirs, files in os.walk(src_path):
            for file in files:
                if file.endswith(('.java', '.kt', '.kts')):
                    file_path = os.path.join(root, file)
                    if contains_chinese_in_file(file_path):
                        return True
        return False
    except Exception as e:
        print(f"[WARN]  检查src目录是否包含中文失败: {src_path} - {e}")
        return False


def find_src_folders(directory: str) -> List[str]:
    """
    查找目录下所有的src文件夹(包括目录本身如果它就是src的话)

    Args:
        directory: 目录路径

    Returns:
        list: src文件夹路径列表
    """
    src_folders: List[str] = []
    try:
        # 检查目录本身是否就是src目录
        if os.path.basename(directory) == 'src':
            src_folders.append(directory)
        
        # 遍历子目录查找src文件夹
        for root, dirs, files in os.walk(directory):
            if os.path.basename(root) == 'src' and root != directory:
                src_folders.append(root)
    except Exception as e:
        print(f"[WARN]  查找src文件夹失败: {directory} - {e}")
    return src_folders


def identify_directory_structure(base_path: str) -> Dict[str, List[str]]:
    """
    统一识别目录结构，确保所有模式使用相同的目录识别逻辑

    Args:
        base_path: 基础路径

    Returns:
        dict: 包含识别结果的字典
    """
    result: Dict[str, List[str]] = {
        "mod_folders": [],
        "src_folders": [],
        "jar_folders": [],
        "jar_files": []
    }
    
    try:
        # 遍历基础路径下的所有目录
        for root, dirs, files in os.walk(base_path):
            # 获取当前目录名称
            current_dir_name = os.path.basename(root)
            
            # 检查是否为mod文件夹
            # mod文件夹应该包含mod_info.json文件，或者位于src/jar目录下
            has_mod_info = os.path.exists(os.path.join(root, "mod_info.json"))
            parent_dir_name = os.path.basename(os.path.dirname(root))
            
            # 检查是否为src目录下的文件夹
            is_src_mod = parent_dir_name == "src"
            # 检查是否为jar目录下的文件夹
            is_jar_mod = parent_dir_name == "jar"
            
            if has_mod_info or is_src_mod or is_jar_mod:
                # 这是一个mod文件夹
                result["mod_folders"].append(root)
                
                # 检查是否包含src文件夹
                src_folder = os.path.join(root, "src")
                if os.path.exists(src_folder):
                    result["src_folders"].append(src_folder)
                
                # 检查是否包含jar文件夹
                jar_folder = os.path.join(root, "jar")
                if os.path.exists(jar_folder):
                    result["jar_folders"].append(jar_folder)
                
                # 查找jar文件
                for file in files:
                    if file.endswith('.jar'):
                        result["jar_files"].append(os.path.join(root, file))
    
    except Exception as e:
        print(f"[ERROR] 识别目录结构失败: {base_path} - {e}")
    
    return result


def create_jar_folder_in_mod(jar_file: str) -> str:
    """
    在mod文件夹下创建jar文件夹

    Args:
        jar_file: JAR文件路径

    Returns:
        str: 创建的jar文件夹路径
    """
    try:
        # 获取mod文件夹路径(JAR文件所在目录)
        mod_dir = os.path.dirname(jar_file)
        # 创建jar文件夹
        jar_dir = os.path.join(mod_dir, "jar")
        os.makedirs(jar_dir, exist_ok=True)
        print(f"[DIR] 在 {os.path.basename(mod_dir)} 文件夹下创建jar文件夹: {jar_dir}")
        return jar_dir
    except Exception as e:
        print(f"[WARN]  创建jar文件夹失败: {jar_file} - {e}")
        return ""


def get_mapping_source(chinese_mod_path: str) -> str:
    """
    确定使用哪个文件夹进行映射(src或jar)

    Args:
        chinese_mod_path: Chinese文件夹下的mod文件夹路径

    Returns:
        str: 用于映射的文件夹路径，如果没有可用文件夹则返回空字符串
    """
    try:
        # 查找Chinese文件夹下mod内的src和jar文件夹
        chinese_src_path = os.path.join(chinese_mod_path, "src")
        chinese_jar_path = os.path.join(chinese_mod_path, "jar")

        # 确定使用哪个文件夹进行映射
        mapping_source: Optional[str] = None

        # 检查src文件夹是否存在且包含中文
        if os.path.exists(chinese_src_path) and os.path.isdir(chinese_src_path):
            has_chinese = contains_chinese_in_src(chinese_src_path)
            if has_chinese:
                mapping_source = chinese_src_path
                print(f"[LIST] 使用 {os.path.basename(chinese_mod_path)} 文件夹下的src文件夹进行映射(包含中文)")

        # 如果src文件夹不存在或不包含中文，检查jar文件夹
        if not mapping_source and os.path.exists(chinese_jar_path) and os.path.isdir(chinese_jar_path):
            mapping_source = chinese_jar_path
            print(f"[LIST] 使用 {os.path.basename(chinese_mod_path)} 文件夹下的jar文件夹进行映射(src文件夹不存在或不包含中文)")

        if not mapping_source:
            print(f"[WARN]  {os.path.basename(chinese_mod_path)} 文件夹下未找到可用的src或jar文件夹")

        return mapping_source if mapping_source else ""
    except Exception as e:
        print(f"[WARN]  确定映射源失败: {chinese_mod_path} - {e}")
        return ""


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
            content = f.read()
        
        # 移除JSON注释
        import re
        # 移除单行注释 // ...
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        # 移除#开头或行尾的注释
        content = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
        # 移除多行注释 /* ... */
        content = re.sub(r'/\*[\s\S]*?\*/', '', content)
        # 将制表符替换为空格
        content = content.replace('\t', '    ')
        
        # 修复JSON语法错误：移除尾随逗号
        # 移除数组末尾的逗号
        content = re.sub(r',\s*\]', r']', content)
        # 移除对象末尾的逗号
        content = re.sub(r',\s*\}', r'}', content)
        # 移除对象属性后的逗号（如果后面跟着}或]）
        content = re.sub(r',\s*(\}|\])', r'\1', content)
        # 移除对象属性后的逗号（如果后面跟着换行和}或]）
        content = re.sub(r',\s*\n\s*(\}|\])', r'\n\1', content)
        
        mod_info = json.loads(content)

        return mod_info
    except Exception as e:
        print(f"[WARN]  读取mod_info.json失败: {mod_path} - {str(e)}")
        return {}


def check_source_folders() -> dict:
    """
    检查source文件夹下的src和jar子文件夹
    
    Returns:
        dict: 检测结果
    """
    from src.common.config_utils import get_directory
    from src.common.logger_utils import get_logger
    
    logger = get_logger("file_utils")
    result = {
        "english_src": False,
        "english_jar": False,
        "chinese_src": False,
        "chinese_jar": False
    }
    
    # 从配置中获取source目录路径
    source_path = get_directory("source")
    if not source_path:
        logger.error("获取source目录路径失败")
        return result
    
    # 检查英文源文件夹
    english_path = os.path.join(source_path, "English")
    if os.path.exists(english_path):
        if os.path.exists(os.path.join(english_path, "src")):
            result["english_src"] = True
        if os.path.exists(os.path.join(english_path, "jar")):
            result["english_jar"] = True
    
    # 检查中文源文件夹
    chinese_path = os.path.join(source_path, "Chinese")
    if os.path.exists(chinese_path):
        if os.path.exists(os.path.join(chinese_path, "src")):
            result["chinese_src"] = True
        if os.path.exists(os.path.join(chinese_path, "jar")):
            result["chinese_jar"] = True
    
    return result


def get_mod_id_from_folder(folder_path: str) -> str:
    """
    从mod_info.json文件中提取mod_id

    Args:
        folder_path: 模组文件夹路径

    Returns:
        str: 模组的id，如果没有找到则返回空字符串
    """
    # 读取mod_info.json
    mod_info = read_mod_info(folder_path)
    
    # 提取mod_id
    mod_id = mod_info.get('id', '')
    
    if not mod_id:
        print(f"[WARN]  {folder_path} 中没有找到有效的mod_id")
        
    return mod_id


def _extract_strings_rules(rules: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    从规则字典中提取字符串规则

    Args:
        rules: 规则字典

    Returns:
        dict: 提取的字符串规则字典
    """
    if isinstance(rules, dict):
        # 格式1: {"strings": {"rule_id": {"source": "source_string", "target": "target_string"}}}
        if "strings" in rules:
            return rules["strings"]
        else:
            # 格式2: {"rule_id": {"source": "source_string", "target": "target_string"}}
            return rules
    return {}


def copy_to_rule_folder(source_file: str, rule_path: str, language: str) -> bool:
    """
    将生成的映射规则复制到rule文件夹
    
    Args:
        source_file: 源文件路径
        rule_path: 规则文件夹路径
        language: 语言类型
    
    Returns:
        bool: 是否复制成功
    """
    try:
        # 构建目标路径
        target_dir = os.path.join(rule_path, language)
        os.makedirs(target_dir, exist_ok=True)
        
        # 获取文件名
        file_name = os.path.basename(source_file)
        target_file = os.path.join(target_dir, file_name)
        
        # 复制文件
        shutil.copy2(source_file, target_file)
        print(f"[OK] 映射规则文件已复制到: {target_file}")
        return True
    except Exception as e:
        print(f"[ERROR] 复制映射规则文件失败: {source_file} -> {rule_path} - {e}")
        return False


def _extract_strings_rules_list(rules: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    从规则字典中提取字符串规则，返回列表格式
    
    Args:
        rules: 规则字典
    
    Returns:
        list: 提取的字符串规则列表
    """
    if isinstance(rules, dict):
        # 格式1: {"strings": [{"id": "rule_id", "original": "source_string", "translated": "target_string"}]}
        if "strings" in rules:
            strings = rules["strings"]
            if isinstance(strings, list):
                return strings
            elif isinstance(strings, dict):
                # 转换为列表格式
                return [strings]
        elif "mappings" in rules:
            mappings = rules["mappings"]
            if isinstance(mappings, list):
                return mappings
            elif isinstance(mappings, dict):
                return [mappings]
        elif "rules" in rules:
            # 格式3: {"id": "mod_id", "rules": [{"id": "rule_id", "original": "source_string", "translated": "target_string"}]}
            rules_list = rules["rules"]
            if isinstance(rules_list, list):
                return rules_list
            elif isinstance(rules_list, dict):
                return [rules_list]
        else:
            # 格式2: {"rule_id": {"source": "source_string", "target": "target_string"}}
            # 转换为新格式列表
            result = []
            for rule_id, rule_content in rules.items():
                if isinstance(rule_content, dict):
                    rule_content["id"] = rule_id
                    result.append(rule_content)
            return result
    return []


def load_mapping_rules(rules_path: Any) -> List[Dict[str, Any]]:
    """
    加载映射规则文件，支持多种输入格式
    
    Args:
        rules_path: 规则文件路径、规则文件夹路径或包含路径的列表
    
    Returns:
        list: 映射规则列表
    """
    mapping_rules: List[Dict[str, Any]] = []
    
    # 支持的规则文件扩展名
    supported_extensions = ['.json', '.yaml', '.yml']
    
    # 如果是列表，遍历列表中的所有路径
    if isinstance(rules_path, list):
        for path in rules_path:
            mapping_rules.extend(load_mapping_rules(path))
        return mapping_rules
    
    # 如果是目录，遍历目录下所有YAML和JSON文件
    if os.path.isdir(rules_path):
        # 遍历规则目录下的所有文件
        for root, dirs, files in os.walk(rules_path):
            for file in files:
                if any(file.endswith(ext) for ext in supported_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        # 根据文件扩展名选择解析方法
                        if file.endswith('.json'):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                rules_data = json.load(f)
                        else:  # YAML文件
                            import yaml
                            with open(file_path, 'r', encoding='utf-8') as f:
                                rules_data = yaml.safe_load(f)
                        
                        # 处理规则文件中的id字段
                        mod_id = None
                        if isinstance(rules_data, dict) and "id" in rules_data:
                            mod_id = rules_data["id"]
                            # 验证mod_id是否存在于全局映射表中
                            from src.init_mode.core import get_mod_info_by_id
                            mod_info = get_mod_info_by_id(mod_id)
                            if mod_info:
                                print(f"[OK] 规则文件关联到mod: {mod_info.name} (id: {mod_id})")
                            else:
                                print(f"[WARN]  规则文件中的id {mod_id} 未找到对应的mod信息")
                        
                        # 提取规则
                        extracted_rules = _extract_strings_rules_list(rules_data)
                        mapping_rules.extend(extracted_rules)
                        print(f"[OK] 加载规则文件: {file_path}")
                    except Exception as e:
                        print(f"[WARN]  加载规则文件失败: {file_path} - {e}")
    elif os.path.isfile(rules_path):
        # 如果是单个文件，直接加载
        try:
            # 根据文件扩展名选择解析方法
            if rules_path.endswith('.json'):
                with open(rules_path, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
            else:  # YAML文件
                import yaml
                with open(rules_path, 'r', encoding='utf-8') as f:
                    rules_data = yaml.safe_load(f)
            
            # 处理规则文件中的id字段
            mod_id = None
            if isinstance(rules_data, dict) and "id" in rules_data:
                mod_id = rules_data["id"]
                # 验证mod_id是否存在于全局映射表中
                from src.init_mode.core import get_mod_info_by_id
                mod_info = get_mod_info_by_id(mod_id)
                if mod_info:
                    print(f"[OK] 规则文件关联到mod: {mod_info.name} (id: {mod_id})")
                else:
                    print(f"[WARN]  规则文件中的id {mod_id} 未找到对应的mod信息")
            
            # 提取规则
            extracted_rules = _extract_strings_rules_list(rules_data)
            mapping_rules.extend(extracted_rules)
            print(f"[OK] 加载规则文件: {rules_path}")
        except Exception as e:
            print(f"[WARN]  加载规则文件失败: {rules_path} - {e}")
    else:
        print(f"[ERROR] 规则路径不存在: {rules_path}")
    
    return mapping_rules