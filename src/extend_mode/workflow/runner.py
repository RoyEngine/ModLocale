#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workflow子模块 - 完整工作流执行功能

负责执行完整的翻译工作流
"""

import os
from typing import Dict, Any
from datetime import datetime

from src.common.yaml_utils import (
    load_yaml_mappings,
    generate_translation_report,
    RuleConflictDetector,
    save_yaml_mappings
)
from src.common.tree_sitter_utils import extract_ast_mappings
from src.common.file_utils import ensure_directory_exists
from src.extend_mode.rules.generator import auto_generate_rules, batch_generate_rules

def run_complete_workflow(
    source_dir: str,
    output_dir: str,
    english_file: str = "",
    chinese_file: str = "",
    bilingual_src_dir: str = "",
    mod_id: str = "",
    existing_rules: str = "",
    parallel: bool = False,
    max_workers: int = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    执行完整的翻译工作流
    
    Args:
        source_dir: 源代码目录路径
        output_dir: 输出目录路径
        english_file: 英文映射文件路径（可选）
        chinese_file: 中文映射文件路径（可选）
        bilingual_src_dir: 双语源代码目录路径，包含英文和中文src文件夹（可选）
        mod_id: 模组ID
        existing_rules: 现有规则文件路径（可选）
        parallel: 是否启用并行处理
        max_workers: 最大工作线程数
        use_cache: 是否使用缓存机制
    
    Returns:
        Dict[str, Any]: 处理结果，包含状态和消息
    """
    # 确保输出目录存在
    ensure_directory_exists(output_dir)
    
    # 准备文件路径
    rules_file = os.path.join(output_dir, "rules.yaml")
    report_file = os.path.join(output_dir, "translation_report.md")
    translated_dir = os.path.join(output_dir, "translated")
    ensure_directory_exists(translated_dir)
    
    # 1. 生成或更新翻译规则
    success = True
    
    # 优先使用双语src文件夹自动生成规则
    if bilingual_src_dir and os.path.exists(bilingual_src_dir):
        # 从双语src文件夹自动生成规则
        result = auto_generate_rules(
            bilingual_src_dir,
            output_file=rules_file,
            mod_id=mod_id,
            existing_rules=existing_rules,
            use_cache=use_cache
        )
        success = result["status"] == "success"
    elif english_file and chinese_file and os.path.exists(english_file) and os.path.exists(chinese_file):
        # 使用传统方式生成规则
        from src.common.yaml_utils import generate_translation_rules, update_translation_rules
        
        if existing_rules and os.path.exists(existing_rules):
            # 更新现有规则
            success = update_translation_rules(
                existing_rules,
                english_file,
                chinese_file,
                rules_file,
                mod_id
            )
        else:
            # 生成新规则
            english_mappings = load_yaml_mappings(english_file)
            chinese_mappings = load_yaml_mappings(chinese_file)
            success = generate_translation_rules(
                english_mappings,
                chinese_mappings,
                rules_file,
                mod_id
            )
    else:
        return {
            "status": "error",
            "message": "必须提供双语src文件夹或英文+中文映射文件"
        }
    
    if not success:
        return {
            "status": "error",
            "message": "翻译规则处理失败"
        }
    
    # 2. 检测规则冲突
    rules = load_yaml_mappings(rules_file)
    detector = RuleConflictDetector()
    conflicts = detector.detect_all_conflicts(rules)
    
    resolved_rules = rules
    if conflicts['total_conflicts'] > 0:
        # 自动解决冲突
        resolved_rules = detector.resolve_conflicts(rules, conflicts, "latest")
        
        # 保存解决后的规则
        from src.common.yaml_utils import save_yaml_mappings
        save_yaml_mappings(resolved_rules, rules_file, version_control=True)
        
        # 重新加载规则
        resolved_rules = load_yaml_mappings(rules_file)
    
    # 3. 生成翻译报告
    generate_translation_report(resolved_rules, report_file, "markdown")
    
    # 4. 提取AST映射
    ast_mappings = list(extract_ast_mappings(
        source_dir, 
        use_parallel=parallel, 
        max_workers=max_workers, 
        use_cache=use_cache
    ))
    
    # 5. 应用翻译到源代码
    print(f"[INFO] 开始将翻译应用到源代码...")
    from src.common.yaml_utils import apply_yaml_mapping
    from src.common.tree_sitter_utils import extract_ast_mappings
    import shutil
    
    # 复制源代码到翻译目录
    shutil.copytree(source_dir, translated_dir, dirs_exist_ok=True)
    
    # 提取源代码中的字符串映射
    source_files = []
    for root, dirs, files in os.walk(translated_dir):
        for file in files:
            if file.endswith('.java') or file.endswith('.kt') or file.endswith('.kts'):
                source_files.append(os.path.join(root, file))
    
    # 应用翻译到每个源文件
    applied_count = 0
    for source_file in source_files:
        # 提取文件中的字符串
        file_ast_mappings = extract_ast_mappings(source_file, root_dir=translated_dir)
        
        if file_ast_mappings:
            # 应用映射
            translated_content = apply_yaml_mapping(source_file, resolved_rules)
            
            # 保存翻译后的内容
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            applied_count += 1
    
    print(f"[OK] 成功将翻译应用到 {applied_count} 个源文件")
    
    # 准备结果
    result = {
        "status": "success",
        "message": "完整工作流执行完成",
        "output_dir": output_dir,
        "rules_file": rules_file,
        "report_file": report_file,
        "translated_dir": translated_dir,
        "rule_count": len(resolved_rules),
        "ast_mapping_count": len(ast_mappings),
        "conflicts": {
            "total_conflicts": conflicts['total_conflicts'],
            "resolved": conflicts['total_conflicts'] > 0
        }
    }
    
    return result
