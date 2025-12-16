#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract模式核心模块

该模块负责从源码中提取字符串并生成映射规则，支持以下功能：
1. 从src文件夹提取字符串
2. 从JAR文件提取字符串（通过decompile_mode API）
3. 生成YAML和JSON格式的映射规则
4. 支持中英文内容提取
5. 生成提取报告
6. 支持多mod并行处理

该模块不再执行初始化操作，仅专注于字符串提取功能，初始化操作由init_mode模块统一处理
"""

import os
import json
from typing import Any, Dict, List

# 注意：不需要添加sys.path，main.py已经设置了正确的Python搜索路径

from src.common import (
    generate_report,  # noqa: E402, E501
    get_timestamp, save_report, find_src_folders,
    setup_logger)  # noqa: E402, E501

from src.common.config_utils import get_directory  # noqa: E402
# 导入流程执行器

# 移除对备用提取实现的引用，直接使用Tree-sitter实现

# 设置日志记录器
logger = setup_logger("extract_mode")


# 添加缺失的generate_mapping_rules函数
def generate_mapping_rules(mappings: List[Dict[str, Any]], base_path: str, language: str, mod_name: str, version: str, timestamp: str, mod_id: str) -> None:
    """
    生成映射规则文件
    
    Args:
        mappings: 映射规则列表
        base_path: 基础路径
        language: 语言类型
        mod_name: 模组名称
        version: 模组版本
        timestamp: 时间戳
        mod_id: 模组ID
    """
    # 获取rules目录
    rules_dir = get_directory("rules")
    if not rules_dir:
        logger.error("无法获取rules目录")
        return
    
    # 创建模组规则目录
    mod_rules_dir = os.path.join(rules_dir, language, mod_name)
    os.makedirs(mod_rules_dir, exist_ok=True)
    
    # 保存映射规则
    yaml_path = os.path.join(mod_rules_dir, f"{language}_mappings.yaml")
    json_path = os.path.join(mod_rules_dir, f"{language}_mappings.json")
    
    # 使用yaml_utils中的save_yaml_mappings函数保存YAML文件
    from src.common.yaml_utils import save_yaml_mappings
    save_yaml_mappings(mappings, yaml_path, mod_id=mod_id)
    
    # 保存JSON文件，添加mod_id到顶层
    json_data = {
        "id": mod_id,
        "rules": mappings
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"映射规则已保存到: {mod_rules_dir}")
    
    # 优化：将生成的规则文件复制到output目录下的对应位置
    # 获取output目录
    output_dir = get_directory("output")
    if output_dir:
        # 创建output目录下的对应语言和mod文件夹
        output_mod_dir = os.path.join(output_dir, f"Extract_{language}", mod_name)
        os.makedirs(output_mod_dir, exist_ok=True)
        
        # 复制规则文件到output目录
        import shutil
        shutil.copy(yaml_path, os.path.join(output_mod_dir, f"{language}_mappings.yaml"))
        shutil.copy(json_path, os.path.join(output_mod_dir, f"{language}_mappings.json"))
        
        logger.info(f"映射规则已复制到output目录: {output_mod_dir}")


def _extract_strings_from_source(source_path: str, language: str, base_path: str, timestamp: str) -> Dict[str, Any]:
    """
    从指定源路径提取字符串
    
    Args:
        source_path: 源路径(src或jar文件夹)
        language: 语言类型(Chinese或English)
        base_path: 基础路径
        timestamp: 时间戳
    
    Returns:
        Dict[str, Any]: 提取结果，包含output_path
    """
    # 获取mod文件夹，source_path已经是模组文件夹路径
    mod_folder = source_path
    
    # 复用init_mode的文件夹命名逻辑，保持源mod文件夹名称不变
    # 使用源文件夹的原始名称作为mod_name
    mod_name = os.path.basename(mod_folder)
    
    # 优先使用init_mode中已经构建好的mod映射关系
    version = "unknown"
    mod_id = ""
    
    # 尝试从init_mode的映射关系中获取mod_id和version
    try:
        from src.init_mode import get_mod_mapping
        mod_mappings = get_mod_mapping()
        
        # 遍历映射关系，查找当前mod_folder对应的映射
        for current_mod_id, mod_info in mod_mappings.items():
            if mod_folder in mod_info["mod_path"]:
                mod_id = current_mod_id
                version = mod_info["mod_info"].version
                break
        
        # 如果没有找到，尝试从mod_folder中提取id
        if not mod_id:
            mod_info_path = os.path.join(mod_folder, "mod_info.json")
            if os.path.exists(mod_info_path):
                try:
                    with open(mod_info_path, 'r', encoding='utf-8') as f:
                        # 直接从第一行提取id字段，避免过度解析
                        first_line = f.readline()
                        if first_line.strip().startswith('{'):
                            # 继续读取直到找到id字段
                            content = first_line + f.read()
                            import re
                            # 简单匹配id字段，假设id在文件中出现一次且格式正确
                            id_match = re.search(r'["\']?id["\']?\s*:\s*["\']?([^"\'\s,]+)["\']?', content)
                            if id_match:
                                mod_id = id_match.group(1)
                            # 简单匹配version字段
                            version_match = re.search(r'["\']?version["\']?\s*:\s*["\']?([^"\'\s,]+)["\']?', content)
                            if version_match:
                                version = version_match.group(1)
                except Exception as e:
                    print(f"[WARN]  读取mod_info.json失败: {mod_info_path} - {e}")
    except Exception as e:
        print(f"[WARN]  从init_mode获取mod映射关系时发生异常: {e}")
        # 如果发生异常，使用文件夹名称作为mod_id
        mod_id = os.path.basename(mod_folder)
        print(f"[WARN]  mod文件夹 {mod_folder} 缺少id信息，使用文件夹名称作为mod_id: {mod_id}")
    
    # 如果mod_id为空，使用文件夹名称作为mod_id，确保每个mod都有唯一标识符
    if not mod_id:
        mod_id = os.path.basename(mod_folder)
        print(f"[WARN]  mod文件夹 {mod_folder} 缺少id信息，使用文件夹名称作为mod_id: {mod_id}")
    
    # 提取AST映射
    from src.common.tree_sitter_utils import extract_ast_mappings
    ast_mappings = extract_ast_mappings(source_path)
    
    if not ast_mappings:
        return {
            "success": False,
            "data": {
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": ["未提取到任何字符串"],
            }
        }
    
    # 生成初始YAML映射，包含未映射标记
    from src.common.yaml_utils import generate_initial_yaml_mappings, save_yaml_mappings
    yaml_mappings = generate_initial_yaml_mappings(ast_mappings, mark_unmapped=True)
    
    # 构建输出文件夹路径: File/output/Extract_English/源mod文件夹名/
    from src.common.config_utils import get_directory
    output_root = get_directory("output")
    output_path = os.path.join(output_root, f"Extract_{language}", mod_name)
    os.makedirs(output_path, exist_ok=True)
    
    # 保存YAML映射，传递mod_id
    yaml_file_path = os.path.join(output_path, f"{language}_mappings.yaml")
    if not save_yaml_mappings(yaml_mappings, yaml_file_path, mod_id=mod_id):
        return {
            "success": False,
            "data": {
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": ["保存YAML映射失败"],
            }
        }
    
    # 同时保存为JSON格式，添加顶层id字段，保持与YAML格式一致
    json_file_path = os.path.join(output_path, f"{language}_mappings.json")
    json_data = {
        "id": mod_id,
        "rules": yaml_mappings
    }
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    # 复制mod_info.json到输出文件夹
    if os.path.exists(mod_info_path):
        import shutil
        shutil.copy(mod_info_path, os.path.join(output_path, "mod_info.json"))
    
    # 提取结果统计
    extracted_result = {
        "total_count": len(ast_mappings),
        "success_count": len(yaml_mappings),
        "fail_count": 0,
        "fail_reasons": [],
        "unmapped_count": sum(1 for m in yaml_mappings if m["status"] == "unmapped"),
        "output_path": output_path
    }
    
    # 生成映射规则文件到rule文件夹
    generate_mapping_rules(yaml_mappings, base_path, language, mod_name, version, timestamp, mod_id)
    
    return {
        "success": True,
        "data": extracted_result
    }


def _process_extract_flow(language: str, base_path: str, timestamp: str, report: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理提取流程
    
    Args:
        language: 语言类型(Chinese或English)
        base_path: 基础路径
        timestamp: 时间戳
        report: 报告
    
    Returns:
        Dict[str, Any]: 处理结果
    """
    try:
        # 1. 构建语言文件路径
        source_dir = get_directory("source")
        if not source_dir:
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": [f"无法获取source目录"],
                },
            )
        language_file_path = os.path.join(source_dir, language)
        if not os.path.exists(language_file_path):
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": [f"{language}文件目录不存在: {language_file_path}"],
                },
            )
        
        # 2. 查找所有src文件夹
        src_folders = find_src_folders(language_file_path)
        
        # 3. 查找所有jar文件夹
        jar_folders = []
        for root, dirs, files in os.walk(language_file_path):
            if os.path.basename(root) == 'jars':
                jar_folders.append(root)
        
        # 4. 收集所有提取源
        extract_sources = []
        
        # 添加所有src文件夹对应的模组文件夹
        for src_folder in src_folders:
            extract_source = os.path.dirname(src_folder)
            extract_sources.append((extract_source, "src"))
        
        # 添加所有jar文件夹对应的模组文件夹
        for jar_folder in jar_folders:
            extract_source = os.path.dirname(jar_folder)
            extract_sources.append((extract_source, "jar"))
        
        if not extract_sources:
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["未找到src或jars文件夹"],
                },
            )
        
        # 5. 执行提取，为每个提取源生成单独的报告
        total_count = len(extract_sources)
        success_count = 0
        all_fail_reasons = []
        
        for extract_source, source_type in extract_sources:
            print(f"\n[SEARCH] 处理提取源：{extract_source} ({source_type})")
            print(f"[INFO] 使用模组文件夹作为提取源：{extract_source}")
            
            # 执行提取
            extract_result = _extract_strings_from_source(extract_source, language, base_path, timestamp)
            
            if extract_result["success"]:
                success_count += 1
                
                # 为每个提取源生成单独的报告
                mod_name = os.path.basename(extract_source)
                single_report = generate_report(
                    process_id=f"{timestamp}_extract_{mod_name}",
                    mode="Extract",
                    sub_flow=report["sub_flow"],
                    status="success",
                    data=extract_result["data"]
                )
                
                # 添加mode和language到结果中
                single_report["mode"] = "Extract"
                single_report["language"] = language
                single_report["output_path"] = extract_result["data"]["output_path"]
                
                # 将报告保存到对应输出文件夹内
                save_report(single_report, extract_result["data"]["output_path"], timestamp)
            else:
                all_fail_reasons.extend(extract_result["data"]["fail_reasons"])
        
        # 6. 生成综合报告
        if success_count > 0:
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="success",
                data={
                    "total_count": total_count,
                    "success_count": success_count,
                    "fail_count": total_count - success_count,
                    "fail_reasons": all_fail_reasons,
                }
            )
        else:
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": total_count,
                    "success_count": 0,
                    "fail_count": total_count,
                    "fail_reasons": all_fail_reasons,
                }
            )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return generate_report(
            process_id=report["process_id"],
            mode="Extract",
            sub_flow=report["sub_flow"],
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"处理提取流程时发生异常: {e}"],
            },
        )


def run_extract_sub_flow(sub_flow: str, base_path: str) -> Dict[str, Any]:
    """
    运行Extract子流程
    
    Args:
        sub_flow: 子流程类型
        base_path: 基础路径
    
    Returns:
        Dict[str, Any]: 处理结果
    """
    # 1. 初始化init_mode，构建mod映射关系
    try:
        from src.init_mode import build_mod_mappings
        from src.common.config_utils import get_directory
        mod_root = get_directory("mod_root")
        if mod_root:
            build_mod_mappings(mod_root)
            print("[OK] 已初始化mod映射关系")
    except Exception as e:
        print(f"[WARN]  初始化mod映射关系失败: {e}")
    
    # 2. 生成时间戳
    timestamp = get_timestamp()
    
    # 3. 创建流程报告
    report = {
        "process_id": timestamp,
        "timestamp": timestamp,
        "mode": "Extract",
        "sub_flow": sub_flow,
        "status": "running",
        "data": {
            "total_count": 0,
            "success_count": 0,
            "fail_count": 0,
            "fail_reasons": [],
        }
    }
    
    # 4. 处理不同的子流程
    if sub_flow in ["英文提取流程", "已有英文src文件夹提取流程", "没有英文src文件夹提取流程"]:
        language = "English"
    elif sub_flow in ["中文提取流程", "已有中文src文件夹提取流程", "没有中文src文件夹提取流程"]:
        language = "Chinese"
    else:
        report["status"] = "fail"
        report["data"]["fail_count"] = 1
        report["data"]["fail_reasons"].append(f"不支持的子流程: {sub_flow}")
        return report
    
    # 5. 执行提取流程
    result = _process_extract_flow(language, base_path, timestamp, report)
    
    # 6. 保存报告
    from src.common.config_utils import get_directory
    report_path = get_directory("output")
    if report_path:
        save_report(result, report_path, timestamp)
    
    return result
