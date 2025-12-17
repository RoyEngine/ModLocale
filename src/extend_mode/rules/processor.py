#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rules子模块 - 未映射内容处理功能

负责处理映射规则中的未映射内容
"""

from typing import List, Dict, Any

from src.common.yaml_utils import (
    load_yaml_mappings,
    generate_unmapped_report,
    list_unmapped_content,
    mark_unmapped_as_translated
)

def process_unmapped_content(
    rule_file: str,
    report_file: str = None,
    list_unmapped: bool = False,
    mark_translated: bool = False,
    output_file: str = None
) -> Dict[str, Any]:
    """
    处理未映射内容
    
    Args:
        rule_file: 映射规则文件路径
        report_file: 生成未映射内容报告的文件路径
        list_unmapped: 是否列出所有未映射内容
        mark_translated: 是否将未映射内容标记为已翻译
        output_file: 输出文件路径
    
    Returns:
        Dict[str, Any]: 处理结果，包含状态和消息
    """
    # 加载映射规则
    rules = load_yaml_mappings(rule_file)
    
    if not rules:
        return {
            "status": "error",
            "message": f"未从文件 {rule_file} 加载到任何映射规则"
        }
    
    # 生成未映射内容报告
    if report_file:
        generate_unmapped_report(rules, report_file)
    
    # 列出所有未映射内容
    if list_unmapped:
        list_unmapped_content(rules, output_file)
    
    # 将未映射内容标记为已翻译
    if mark_translated:
        mark_unmapped_as_translated(rules, output_file)
    
    # 如果没有指定任何操作，返回错误信息
    if not any([report_file, list_unmapped, mark_translated]):
        return {
            "status": "error",
            "message": "必须指定至少一个操作: report, list, 或 mark_translated"
        }
    
    return {
        "status": "success",
        "message": "未映射内容处理完成"
    }
