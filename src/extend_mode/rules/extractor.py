#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rules子模块 - 规则提取功能

负责从源代码或已处理文件夹提取映射规则
"""

import os
from typing import List, Dict, Any

from src.common.yaml_utils import (
    load_yaml_mappings,
    save_yaml_mappings,
    update_mapping_status,
    generate_initial_yaml_mappings,
    merge_mapping_rules,
    extract_mappings_from_processed_folder
)
from src.common.tree_sitter_utils import extract_ast_mappings

def extract_mapping_rules(
    source_dir: str = None,
    processed_dir: str = None,
    existing_rule: str = None,
    output_file: str = None,
    language: str = "English"
) -> Dict[str, Any]:
    """
    提取映射规则
    
    Args:
        source_dir: 源目录路径，用于提取映射规则
        processed_dir: 已处理文件夹路径，用于从已处理内容提取映射规则
        existing_rule: 现有规则文件路径，用于合并新提取的规则
        output_file: 输出规则文件路径
        language: 语言类型
    
    Returns:
        Dict[str, Any]: 提取结果，包含规则数量和状态
    """
    # 验证输入参数
    if not source_dir and not processed_dir:
        return {
            "status": "error",
            "message": "必须提供source_dir或processed_dir参数"
        }
    
    if source_dir and not os.path.exists(source_dir):
        return {
            "status": "error",
            "message": f"源目录不存在: {source_dir}"
        }
    
    if processed_dir and not os.path.exists(processed_dir):
        return {
            "status": "error",
            "message": f"已处理文件夹不存在: {processed_dir}"
        }
    
    if existing_rule and not os.path.exists(existing_rule):
        return {
            "status": "error",
            "message": f"现有规则文件不存在: {existing_rule}"
        }
    
    # 确保输出目录存在
    if output_file:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
    
    # 提取映射规则
    new_rules = []
    
    if source_dir:
        # 提取AST映射
        ast_mappings = list(extract_ast_mappings(source_dir))
        
        if ast_mappings:
            # 生成初始YAML映射，不标记未映射内容（由processor.py处理）
            new_rules = generate_initial_yaml_mappings(ast_mappings, mark_unmapped=False)
        
    if processed_dir:
        # 从已处理文件夹提取映射规则
        processed_rules = extract_mappings_from_processed_folder(processed_dir, language)
        
        if processed_rules:
            new_rules.extend(processed_rules)
    
    if not new_rules:
        return {
            "status": "error",
            "message": "未提取到任何映射规则"
        }
    
    # 如果提供了现有规则，合并规则
    if existing_rule:
        # 加载现有规则
        existing_rules = load_yaml_mappings(existing_rule)
        
        if existing_rules:
            # 合并规则
            merged_rules = merge_mapping_rules(existing_rules, new_rules)
            # 更新规则状态
            updated_rules = update_mapping_status(merged_rules)
            
            # 保存合并后的规则
            if output_file:
                if save_yaml_mappings(updated_rules, output_file):
                    return {
                        "status": "success",
                        "message": "映射规则已保存",
                        "rules_count": len(updated_rules),
                        "unmapped_count": sum(1 for r in updated_rules if r['status'] == 'unmapped')
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"保存映射规则失败: {output_file}"
                    }
    
    # 更新规则状态
    updated_rules = update_mapping_status(new_rules)
    
    # 保存映射规则
    if output_file:
        if save_yaml_mappings(updated_rules, output_file):
            return {
                "status": "success",
                "message": "映射规则已保存",
                "rules_count": len(updated_rules),
                "unmapped_count": sum(1 for r in updated_rules if r['status'] == 'unmapped')
            }
        else:
            return {
                "status": "error",
                "message": f"保存映射规则失败: {output_file}"
            }
    
    return {
        "status": "success",
        "message": "映射规则提取完成",
        "rules_count": len(updated_rules),
        "unmapped_count": sum(1 for r in updated_rules if r['status'] == 'unmapped')
    }
