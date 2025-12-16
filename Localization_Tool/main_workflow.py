#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地化工具主工作流程脚本

该脚本整合了本地化工具的所有功能模块，实现从双语数据加载到翻译回写的完整流程。
"""

import os
import sys
import argparse
import yaml
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.common.yaml_utils import (
    load_yaml_mappings,
    generate_translation_rules,
    update_translation_rules,
    generate_translation_report,
    apply_yaml_mapping,
    RuleConflictDetector
)

from src.common.tree_sitter_utils import extract_ast_mappings
from src.common.file_utils import ensure_directory_exists

def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        description="本地化工具主工作流程脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：

# 生成翻译规则
python main_workflow.py generate-rules --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --output-file rules.yaml

# 更新翻译规则
python main_workflow.py update-rules --existing-rules old_rules.yaml --new-english new_en.yaml --new-chinese new_zh.yaml --output-file updated_rules.yaml

# 运行完整工作流
python main_workflow.py workflow --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --source-dir ./src --output-dir ./output
        """
    )
    
    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 1. 生成翻译规则命令
    parser_generate = subparsers.add_parser("generate-rules", help="从双语数据生成翻译规则")
    parser_generate.add_argument(
        "--english-file",
        type=str,
        required=True,
        help="英文映射文件路径"
    )
    parser_generate.add_argument(
        "--chinese-file",
        type=str,
        required=True,
        help="中文映射文件路径"
    )
    parser_generate.add_argument(
        "--output-file",
        type=str,
        required=True,
        help="输出规则文件路径"
    )
    parser_generate.add_argument(
        "--mod-id",
        type=str,
        default="",
        help="模组ID"
    )
    
    # 2. 更新翻译规则命令
    parser_update = subparsers.add_parser("update-rules", help="更新现有翻译规则")
    parser_update.add_argument(
        "--existing-rules",
        type=str,
        required=True,
        help="现有规则文件路径"
    )
    parser_update.add_argument(
        "--new-english",
        type=str,
        required=True,
        help="新的英文映射文件路径"
    )
    parser_update.add_argument(
        "--new-chinese",
        type=str,
        required=True,
        help="新的中文映射文件路径"
    )
    parser_update.add_argument(
        "--output-file",
        type=str,
        required=True,
        help="输出规则文件路径"
    )
    parser_update.add_argument(
        "--mod-id",
        type=str,
        default="",
        help="模组ID"
    )
    
    # 3. 完整工作流命令
    parser_workflow = subparsers.add_parser("workflow", help="运行完整工作流")
    parser_workflow.add_argument(
        "--english-file",
        type=str,
        required=True,
        help="英文映射文件路径"
    )
    parser_workflow.add_argument(
        "--chinese-file",
        type=str,
        required=True,
        help="中文映射文件路径"
    )
    parser_workflow.add_argument(
        "--source-dir",
        type=str,
        default="./src",
        help="源代码目录路径"
    )
    parser_workflow.add_argument(
        "--output-dir",
        type=str,
        default="./output",
        help="输出目录路径"
    )
    parser_workflow.add_argument(
        "--mod-id",
        type=str,
        default="",
        help="模组ID"
    )
    parser_workflow.add_argument(
        "--existing-rules",
        type=str,
        default="",
        help="现有规则文件路径（可选）"
    )
    
    return parser.parse_args()

def run_generate_rules(args):
    """
    运行生成翻译规则流程
    """
    print("=" * 60)
    print("          生成翻译规则")
    print("=" * 60)
    
    # 加载双语映射文件
    print(f"[INFO] 加载英文映射文件: {args.english_file}")
    english_mappings = load_yaml_mappings(args.english_file)
    
    print(f"[INFO] 加载中文映射文件: {args.chinese_file}")
    chinese_mappings = load_yaml_mappings(args.chinese_file)
    
    # 生成翻译规则
    success = generate_translation_rules(
        english_mappings,
        chinese_mappings,
        args.output_file,
        args.mod_id
    )
    
    if success:
        print("\n[SUCCESS] 翻译规则生成完成")
        
        # 检测规则冲突
        print("\n[INFO] 检测规则冲突...")
        rules = load_yaml_mappings(args.output_file)
        detector = RuleConflictDetector()
        conflicts = detector.detect_all_conflicts(rules)
        
        if conflicts['total_conflicts'] > 0:
            print(f"[WARN] 检测到 {conflicts['total_conflicts']} 个冲突")
            print(f"  - 重复ID: {conflicts['conflict_summary']['duplicate_ids']}")
            print(f"  - 重复原始字符串: {conflicts['conflict_summary']['duplicate_originals']}")
            print(f"  - 翻译冲突: {conflicts['conflict_summary']['translation_conflicts']}")
        else:
            print("[OK] 未检测到冲突")
        
        return 0
    else:
        print("\n[ERROR] 翻译规则生成失败")
        return 1

def run_update_rules(args):
    """
    运行更新翻译规则流程
    """
    print("=" * 60)
    print("          更新翻译规则")
    print("=" * 60)
    
    # 更新翻译规则
    success = update_translation_rules(
        args.existing_rules,
        args.new_english,
        args.new_chinese,
        args.output_file,
        args.mod_id
    )
    
    if success:
        print("\n[SUCCESS] 翻译规则更新完成")
        
        # 检测规则冲突
        print("\n[INFO] 检测规则冲突...")
        rules = load_yaml_mappings(args.output_file)
        detector = RuleConflictDetector()
        conflicts = detector.detect_all_conflicts(rules)
        
        if conflicts['total_conflicts'] > 0:
            print(f"[WARN] 检测到 {conflicts['total_conflicts']} 个冲突")
            print(f"  - 重复ID: {conflicts['conflict_summary']['duplicate_ids']}")
            print(f"  - 重复原始字符串: {conflicts['conflict_summary']['duplicate_originals']}")
            print(f"  - 翻译冲突: {conflicts['conflict_summary']['translation_conflicts']}")
        else:
            print("[OK] 未检测到冲突")
        
        return 0
    else:
        print("\n[ERROR] 翻译规则更新失败")
        return 1

def run_complete_workflow(args):
    """
    运行完整工作流
    """
    print("=" * 60)
    print("          完整工作流")
    print("=" * 60)
    
    # 创建输出目录
    ensure_directory_exists(args.output_dir)
    
    # 1. 准备文件路径
    rules_file = os.path.join(args.output_dir, "rules.yaml")
    report_file = os.path.join(args.output_dir, "translation_report.md")
    translated_dir = os.path.join(args.output_dir, "translated")
    
    # 2. 生成或更新翻译规则
    if args.existing_rules and os.path.exists(args.existing_rules):
        # 更新现有规则
        print("\n[STEP 1] 更新翻译规则")
        success = update_translation_rules(
            args.existing_rules,
            args.english_file,
            args.chinese_file,
            rules_file,
            args.mod_id
        )
    else:
        # 生成新规则
        print("\n[STEP 1] 生成翻译规则")
        english_mappings = load_yaml_mappings(args.english_file)
        chinese_mappings = load_yaml_mappings(args.chinese_file)
        success = generate_translation_rules(
            english_mappings,
            chinese_mappings,
            rules_file,
            args.mod_id
        )
    
    if not success:
        print("\n[ERROR] 翻译规则处理失败")
        return 1
    
    # 3. 检测规则冲突
    print("\n[STEP 2] 检测规则冲突")
    rules = load_yaml_mappings(rules_file)
    detector = RuleConflictDetector()
    conflicts = detector.detect_all_conflicts(rules)
    
    if conflicts['total_conflicts'] > 0:
        print(f"[WARN] 检测到 {conflicts['total_conflicts']} 个冲突")
        print(f"  - 重复ID: {conflicts['conflict_summary']['duplicate_ids']}")
        print(f"  - 重复原始字符串: {conflicts['conflict_summary']['duplicate_originals']}")
        print(f"  - 翻译冲突: {conflicts['conflict_summary']['translation_conflicts']}")
        
        # 自动解决冲突
        print("\n[STEP 2.1] 自动解决冲突")
        resolved_rules = detector.resolve_conflicts(rules, conflicts, "latest")
        
        # 保存解决后的规则
        from src.common.yaml_utils import save_yaml_mappings
        save_yaml_mappings(resolved_rules, rules_file, version_control=True)
        print(f"[OK] 冲突已解决，规则已更新")
        
        # 重新加载规则
        rules = load_yaml_mappings(rules_file)
    else:
        print("[OK] 未检测到冲突")
    
    # 4. 生成翻译报告
    print("\n[STEP 3] 生成翻译报告")
    generate_translation_report(rules, report_file, "markdown")
    
    # 5. 提取AST映射（可选，用于后续分析）
    print("\n[STEP 4] 提取源代码AST映射")
    ast_mappings = extract_ast_mappings(args.source_dir)
    print(f"[INFO] 从源代码提取到 {len(ast_mappings)} 个映射")
    
    # 6. 应用翻译到源代码（示例）
    print("\n[STEP 5] 应用翻译到源代码")
    # 这里可以添加批量回写逻辑，例如：
    # for file_path in source_files:
    #     apply_yaml_mapping(file_path, rules)
    
    print("\n[SUCCESS] 完整工作流执行完成")
    print(f"\n[INFO] 输出文件：")
    print(f"  - 翻译规则: {rules_file}")
    print(f"  - 翻译报告: {report_file}")
    print(f"  - 翻译后代码: {translated_dir}")
    
    return 0

def main():
    """
    主函数
    """
    args = parse_args()
    
    if not args.command:
        print("[ERROR] 请指定命令")
        return 1
    
    # 执行相应的命令
    if args.command == "generate-rules":
        return run_generate_rules(args)
    elif args.command == "update-rules":
        return run_update_rules(args)
    elif args.command == "workflow":
        return run_complete_workflow(args)
    else:
        print(f"[ERROR] 未知命令: {args.command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
