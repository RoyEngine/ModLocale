#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rules子模块 - 自动规则生成功能

负责从双语src文件夹自动生成映射规则
"""

import os
from typing import List, Dict, Any

from src.common.yaml_utils import (
    load_yaml_mappings,
    save_yaml_mappings,
    generate_translation_rules,
    RuleConflictDetector
)
from src.common.tree_sitter_utils import extract_ast_mappings


def auto_generate_rules(
    chinese_src_dir: str,
    english_src_dir: str = "",
    output_file: str = "",
    mod_id: str = "",
    language: str = "English",
    existing_rules: str = "",
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    从双语src文件夹自动生成映射规则
    
    Args:
        chinese_src_dir: 中文src文件夹路径，或包含中英文src文件夹的父目录
        english_src_dir: 英文src文件夹路径（可选）
        output_file: 输出规则文件路径
        mod_id: 模组ID
        language: 主要语言类型
        existing_rules: 现有规则文件路径（可选）
        use_cache: 是否使用缓存机制
    
    Returns:
        Dict[str, Any]: 处理结果，包含状态和消息
    """
    # 解析输入参数，支持多种目录结构
    actual_chinese_src = chinese_src_dir
    actual_english_src = english_src_dir
    
    # 如果english_src_dir为空，尝试从chinese_src_dir中解析出中英文文件夹
    if not english_src_dir:
        # 检查chinese_src_dir是否为包含中英文文件夹的父目录
        possible_chinese = os.path.join(chinese_src_dir, "Chinese")
        possible_english = os.path.join(chinese_src_dir, "English")
        
        if os.path.exists(possible_chinese) and os.path.exists(possible_english):
            # 检查是否包含src子目录
            if os.path.exists(os.path.join(possible_chinese, "src")):
                actual_chinese_src = os.path.join(possible_chinese, "src")
            else:
                actual_chinese_src = possible_chinese
            
            if os.path.exists(os.path.join(possible_english, "src")):
                actual_english_src = os.path.join(possible_english, "src")
            else:
                actual_english_src = possible_english
        else:
            # 检查另一种常见结构：chinese_src_dir为中文文件夹，english_src_dir未提供
            # 尝试从chinese_src_dir的父目录中找到英文文件夹
            parent_dir = os.path.dirname(chinese_src_dir)
            possible_english = os.path.join(parent_dir, "English")
            
            if os.path.exists(possible_english):
                if os.path.exists(os.path.join(possible_english, "src")):
                    actual_english_src = os.path.join(possible_english, "src")
                else:
                    actual_english_src = possible_english
            else:
                # 检查chinese_src_dir是否直接包含src子目录
                if os.path.exists(os.path.join(chinese_src_dir, "src")):
                    actual_chinese_src = os.path.join(chinese_src_dir, "src")
                    # 尝试从当前目录的父目录中找到英文src文件夹
                    parent_dir = os.path.dirname(chinese_src_dir)
                    possible_english = os.path.join(parent_dir, "English", "src")
                    if os.path.exists(possible_english):
                        actual_english_src = possible_english
                    else:
                        possible_english = os.path.join(parent_dir, "English")
                        if os.path.exists(possible_english):
                            actual_english_src = possible_english
    
    # 验证输入参数
    if not actual_chinese_src or not os.path.exists(actual_chinese_src):
        return {
            "status": "error",
            "message": "中文src文件夹路径无效"
        }
    
    if not actual_english_src or not os.path.exists(actual_english_src):
        return {
            "status": "error",
            "message": "英文src文件夹路径无效"
        }
    
    # 提取中文映射规则
    print(f"正在从中文src文件夹提取映射规则：{actual_chinese_src}")
    chinese_mappings = extract_ast_mappings(actual_chinese_src, use_cache=use_cache)
    
    if not chinese_mappings:
        return {
            "status": "error",
            "message": "从中文src文件夹提取映射规则失败"
        }
    
    print(f"成功提取中文映射规则 {len(chinese_mappings)} 条")
    
    # 提取英文映射规则
    print(f"正在从英文src文件夹提取映射规则：{actual_english_src}")
    english_mappings = extract_ast_mappings(actual_english_src, use_cache=use_cache)
    
    if not english_mappings:
        return {
            "status": "error",
            "message": "从英文src文件夹提取映射规则失败"
        }
    
    print(f"成功提取英文映射规则 {len(english_mappings)} 条")
    
    # 生成翻译规则
    print(f"正在生成翻译规则...")
    
    if existing_rules and os.path.exists(existing_rules):
        # 更新现有规则
        from src.common.yaml_utils import update_translation_rules
        success = update_translation_rules(
            existing_rules,
            english_mappings,
            chinese_mappings,
            output_file,
            mod_id
        )
    else:
        # 生成新规则
        success = generate_translation_rules(
            english_mappings,
            chinese_mappings,
            output_file,
            mod_id
        )
    
    if success:
        # 检测规则冲突
        rules = load_yaml_mappings(output_file)
        detector = RuleConflictDetector()
        conflicts = detector.detect_all_conflicts(rules)
        
        conflict_info = {
            "total_conflicts": conflicts['total_conflicts'],
            "duplicate_ids": len(conflicts['duplicate_ids']),
            "duplicate_originals": len(conflicts['duplicate_originals']),
            "translation_conflicts": len(conflicts['translation_conflicts'])
        }
        
        print(f"翻译规则生成完成，输出文件：{output_file}")
        print(f"生成规则 {len(rules)} 条，检测到冲突 {conflict_info['total_conflicts']} 个")
        
        return {
            "status": "success",
            "message": "翻译规则自动生成完成",
            "output_file": output_file,
            "rule_count": len(rules),
            "chinese_mappings_count": len(chinese_mappings),
            "english_mappings_count": len(english_mappings),
            "conflicts": conflict_info
        }
    else:
        return {
            "status": "error",
            "message": "翻译规则生成失败"
        }


def batch_generate_rules(
    mods_dir: str,
    output_dir: str,
    language: str = "English"
) -> Dict[str, Any]:
    """
    批量从双语src文件夹自动生成映射规则
    
    Args:
        mods_dir: 包含多个mod的目录路径，目录结构应为：mods_dir/mod_name/(Chinese/English)/src
        output_dir: 输出规则文件的目录路径
        language: 主要语言类型
    
    Returns:
        Dict[str, Any]: 处理结果，包含状态和消息
    """
    if not mods_dir or not os.path.exists(mods_dir):
        return {
            "status": "error",
            "message": "mods目录路径无效"
        }
    
    if not output_dir:
        output_dir = mods_dir
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    results = {
        "status": "success",
        "message": "批量生成规则完成",
        "total_mods": 0,
        "success_mods": 0,
        "failed_mods": 0,
        "mod_results": []
    }
    
    # 遍历mods目录
    for mod_name in os.listdir(mods_dir):
        mod_path = os.path.join(mods_dir, mod_name)
        if not os.path.isdir(mod_path):
            continue
        
        results["total_mods"] += 1
        mod_result = {
            "mod_name": mod_name,
            "status": "success",
            "message": "规则生成成功"
        }
        
        # 检查双语src文件夹
        chinese_src = os.path.join(mod_path, "Chinese", "src")
        english_src = os.path.join(mod_path, "English", "src")
        
        if not os.path.exists(chinese_src):
            mod_result["status"] = "error"
            mod_result["message"] = "缺少中文src文件夹"
            results["failed_mods"] += 1
            results["mod_results"].append(mod_result)
            continue
        
        if not os.path.exists(english_src):
            mod_result["status"] = "error"
            mod_result["message"] = "缺少英文src文件夹"
            results["failed_mods"] += 1
            results["mod_results"].append(mod_result)
            continue
        
        # 生成规则
        output_file = os.path.join(output_dir, f"{mod_name}_mappings.yaml")
        result = auto_generate_rules(
            chinese_src, english_src, output_file, mod_name, language
        )
        
        if result["status"] == "success":
            results["success_mods"] += 1
            mod_result.update(result)
        else:
            results["failed_mods"] += 1
            mod_result["status"] = "error"
            mod_result["message"] = result["message"]
        
        results["mod_results"].append(mod_result)
    
    return results
