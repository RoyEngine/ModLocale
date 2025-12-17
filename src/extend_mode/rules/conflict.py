#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rules子模块 - 冲突检测和解决功能

负责检测和解决映射规则中的冲突
"""

from typing import List, Dict, Any

from src.common.yaml_utils import (
    load_yaml_mappings,
    RuleConflictDetector
)

def detect_and_resolve_conflicts(
    rule_file: str,
    generate_report: bool = False,
    report_file: str = None,
    resolve: bool = False,
    resolve_strategy: str = "latest"
) -> Dict[str, Any]:
    """
    检测和解决规则冲突
    
    Args:
        rule_file: 映射规则文件路径
        generate_report: 是否生成冲突报告
        report_file: 冲突报告文件路径
        resolve: 是否解决冲突
        resolve_strategy: 冲突解决策略
    
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
    
    # 检测冲突
    detector = RuleConflictDetector()
    conflicts = detector.detect_all_conflicts(rules)
    
    # 生成冲突报告
    if generate_report and report_file:
        report = detector.generate_conflict_report(conflicts)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    # 解决冲突
    if resolve:
        resolved = detector.resolve_conflicts(conflicts, resolve_strategy)
        return {
            "status": "success",
            "message": "冲突检测完成",
            "total_conflicts": conflicts['total_conflicts'],
            "duplicate_ids": len(conflicts['duplicate_ids']),
            "duplicate_originals": len(conflicts['duplicate_originals']),
            "translation_conflicts": len(conflicts['translation_conflicts'])
        }
    
    return {
        "status": "success",
        "message": "冲突检测完成",
        "total_conflicts": conflicts['total_conflicts'],
        "conflict_details": {
            "duplicate_ids": len(conflicts['duplicate_ids']),
            "duplicate_originals": len(conflicts['duplicate_originals']),
            "translation_conflicts": len(conflicts['translation_conflicts'])
        }
    }
