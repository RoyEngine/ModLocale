#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workflow子模块 - 规则更新功能

负责更新现有翻译规则
"""

from typing import List, Dict, Any
from datetime import datetime

from src.common.yaml_utils import (
    load_yaml_mappings,
    update_translation_rules,
    RuleConflictDetector
)

def update_translation_rules_func(
    existing_rules_file: str,
    new_english_file: str,
    new_chinese_file: str,
    output_file: str,
    mod_id: str = ""
) -> Dict[str, Any]:
    """
    更新现有翻译规则
    
    Args:
        existing_rules_file: 现有规则文件路径
        new_english_file: 新的英文映射文件路径
        new_chinese_file: 新的中文映射文件路径
        output_file: 输出规则文件路径
        mod_id: 模组ID
    
    Returns:
        Dict[str, Any]: 处理结果，包含状态和消息
    """
    # 验证输入文件是否存在
    import os
    for file_path in [existing_rules_file, new_english_file, new_chinese_file]:
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "message": f"文件不存在: {file_path}"
            }
    
    # 更新翻译规则
    success = update_translation_rules(
        existing_rules_file,
        new_english_file,
        new_chinese_file,
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
            "message": "翻译规则更新完成",
            "output_file": output_file,
            "rule_count": len(rules),
            "conflicts": conflict_info
        }
    else:
        return {
            "status": "error",
            "message": "翻译规则更新失败"
        }
