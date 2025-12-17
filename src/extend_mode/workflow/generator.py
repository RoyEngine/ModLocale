#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workflow子模块 - 规则生成功能

负责从双语数据生成翻译规则
"""

from typing import List, Dict, Any
from datetime import datetime

from src.common.yaml_utils import (
    load_yaml_mappings,
    generate_translation_rules,
    save_yaml_mappings,
    RuleConflictDetector
)

def generate_translation_rules_func(
    english_file: str,
    chinese_file: str,
    output_file: str,
    mod_id: str = ""
) -> Dict[str, Any]:
    """
    从双语数据生成翻译规则
    
    Args:
        english_file: 英文映射文件路径
        chinese_file: 中文映射文件路径
        output_file: 输出规则文件路径
        mod_id: 模组ID
    
    Returns:
        Dict[str, Any]: 处理结果，包含状态和消息
    """
    # 加载双语映射文件
    english_mappings = load_yaml_mappings(english_file)
    chinese_mappings = load_yaml_mappings(chinese_file)
    
    # 数据验证
    if not english_mappings:
        return {
            "status": "error",
            "message": "英文映射数据为空"
        }
    
    if not chinese_mappings:
        return {
            "status": "error",
            "message": "中文映射数据为空"
        }
    
    # 生成翻译规则
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
        
        return {
            "status": "success",
            "message": "翻译规则生成完成",
            "output_file": output_file,
            "rule_count": len(rules),
            "conflicts": conflict_info
        }
    else:
        return {
            "status": "error",
            "message": "翻译规则生成失败"
        }
