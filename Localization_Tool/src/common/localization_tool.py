#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一的本地化工具命令行入口

该脚本整合了所有本地化相关的命令行功能，包括：
1. 映射规则生成
2. 未映射内容处理
3. 冲突检测和解决
"""

import os
import sys
import argparse
from typing import List, Dict, Any

# 导入核心模块
from .yaml_utils import (
    load_yaml_mappings,
    save_yaml_mappings,
    update_mapping_status,
    generate_initial_yaml_mappings,
    merge_mapping_rules,
    extract_mappings_from_processed_folder,
    generate_unmapped_report,
    list_unmapped_content,
    mark_unmapped_as_translated,
    RuleConflictDetector,
    generate_translation_rules,
    update_translation_rules
)
from .tree_sitter_utils import extract_ast_mappings

def command_extract(args: argparse.Namespace) -> int:
    """
    提取映射规则命令
    """
    print("=" * 60)
    print("          映射规则提取工具")
    print("=" * 60)
    
    # 验证输入参数
    if not args.source_dir and not args.processed_dir:
        print("[ERROR] 必须提供 --source-dir 或 --processed-dir 参数")
        return 1
    
    if args.source_dir and not os.path.exists(args.source_dir):
        print(f"[ERROR] 源目录不存在: {args.source_dir}")
        return 1
    
    if args.processed_dir and not os.path.exists(args.processed_dir):
        print(f"[ERROR] 已处理文件夹不存在: {args.processed_dir}")
        return 1
    
    if args.existing_rule and not os.path.exists(args.existing_rule):
        print(f"[ERROR] 现有规则文件不存在: {args.existing_rule}")
        return 1
    
    # 确保输出目录存在
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"[OK] 创建输出目录: {output_dir}")
    
    # 提取映射规则
    new_rules = []
    
    if args.source_dir:
        print(f"[INFO] 从源目录提取规则: {args.source_dir}")
        # 提取AST映射
        ast_mappings = extract_ast_mappings(args.source_dir)
        
        if not ast_mappings:
            print(f"[WARN]  未从源目录 {args.source_dir} 提取到任何字符串")
        else:
            # 生成初始YAML映射
            new_rules = generate_initial_yaml_mappings(ast_mappings, mark_unmapped=args.mark_unmapped)
            print(f"[OK] 从源目录提取到 {len(new_rules)} 条映射规则")
    
    if args.processed_dir:
        print(f"[INFO] 从已处理文件夹提取规则: {args.processed_dir}")
        # 从已处理文件夹提取映射规则
        processed_rules = extract_mappings_from_processed_folder(args.processed_dir, args.language)
        
        if processed_rules:
            new_rules.extend(processed_rules)
            print(f"[OK] 从已处理文件夹提取到 {len(processed_rules)} 条映射规则")
    
    if not new_rules:
        print(f"[ERROR] 未提取到任何映射规则")
        return 1
    
    # 如果提供了现有规则，合并规则
    if args.existing_rule:
        print(f"[INFO] 合并现有规则: {args.existing_rule}")
        # 加载现有规则
        existing_rules = load_yaml_mappings(args.existing_rule)
        
        if existing_rules:
            # 合并规则
            merged_rules = merge_mapping_rules(existing_rules, new_rules)
            # 更新规则状态
            updated_rules = update_mapping_status(merged_rules)
            
            print(f"[OK] 合并完成: 现有 {len(existing_rules)} 条 + 新增 {len(new_rules)} 条 = 总计 {len(updated_rules)} 条")
            print(f"[OK] 其中未映射规则: {sum(1 for r in updated_rules if r['status'] == 'unmapped')} 条")
            
            # 保存合并后的规则
            if save_yaml_mappings(updated_rules, args.output_file):
                print(f"\n[SUCCESS] 映射规则已保存到: {args.output_file}")
                return 0
            else:
                print(f"\n[ERROR] 保存映射规则失败: {args.output_file}")
                return 1
    
    # 更新规则状态
    updated_rules = update_mapping_status(new_rules)
    
    # 保存映射规则
    print(f"\n[INFO] 准备保存映射规则到: {args.output_file}")
    print(f"[INFO] 规则数量: {len(updated_rules)} 条")
    print(f"[INFO] 未映射规则: {sum(1 for r in updated_rules if r['status'] == 'unmapped')} 条")
    print(f"[INFO] 已映射规则: {sum(1 for r in updated_rules if r['status'] != 'unmapped')} 条")
    
    if save_yaml_mappings(updated_rules, args.output_file):
        print(f"\n[SUCCESS] 映射规则已保存到: {args.output_file}")
        return 0
    else:
        print(f"\n[ERROR] 保存映射规则失败: {args.output_file}")
        return 1



def command_process_unmapped(args: argparse.Namespace) -> int:
    """
    处理未映射内容命令
    """
    print("=" * 60)
    print("          未映射内容处理工具")
    print("=" * 60)
    
    # 验证输入参数
    if not os.path.exists(args.rule_file):
        print(f"[ERROR] 规则文件不存在: {args.rule_file}")
        return 1
    
    # 加载映射规则
    print(f"[INFO] 加载映射规则: {args.rule_file}")
    rules = load_yaml_mappings(args.rule_file)
    
    if not rules:
        print(f"[ERROR] 未从文件 {args.rule_file} 加载到任何映射规则")
        return 1
    
    print(f"[OK] 加载到 {len(rules)} 条映射规则")
    
    # 生成未映射内容报告
    if args.report:
        generate_unmapped_report(rules, args.report)
    
    # 列出所有未映射内容
    if args.list:
        list_unmapped_content(rules, args.output)
    
    # 将未映射内容标记为已翻译
    if args.mark_translated:
        mark_unmapped_as_translated(rules, args.output)
    
    # 如果没有指定任何操作，显示错误信息
    if not any([args.report, args.list, args.mark_translated]):
        print("[ERROR] 必须指定至少一个操作: --report, --list, 或 --mark-translated")
        return 1
    
    return 0

def command_conflict(args: argparse.Namespace) -> int:
    """
    冲突检测和解决命令
    """
    print("=" * 60)
    print("          冲突检测和解决工具")
    print("=" * 60)
    
    # 验证输入参数
    if not os.path.exists(args.rule_file):
        print(f"[ERROR] 规则文件不存在: {args.rule_file}")
        return 1
    
    # 加载映射规则
    print(f"[INFO] 加载映射规则: {args.rule_file}")
    rules = load_yaml_mappings(args.rule_file)
    
    if not rules:
        print(f"[ERROR] 未从文件 {args.rule_file} 加载到任何映射规则")
        return 1
    
    print(f"[OK] 加载到 {len(rules)} 条映射规则")
    
    # 检测冲突
    detector = RuleConflictDetector()
    conflicts = detector.detect_all_conflicts(rules)
    
    print(f"[INFO] 冲突检测完成: {conflicts['total_conflicts']} 个冲突")
    print(f"[INFO] 重复ID: {conflicts['conflict_summary']['duplicate_ids']}")
    print(f"[INFO] 重复原始字符串: {conflicts['conflict_summary']['duplicate_originals']}")
    print(f"[INFO] 翻译冲突: {conflicts['conflict_summary']['translation_conflicts']}")
    
    # 生成冲突报告
    if args.report:
        report = detector.generate_conflict_report(conflicts)
        output_dir = os.path.dirname(args.report)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"[OK] 冲突报告已保存到: {args.report}")
    
    # 解决冲突
    if args.resolve:
        resolved = detector.resolve_conflicts(conflicts, args.resolve_strategy)
        print(f"[INFO] 冲突解决完成，使用策略: {args.resolve_strategy}")
        # 这里可以根据需要扩展冲突解决功能
    
    return 0

def command_generate_rules(args: argparse.Namespace) -> int:
    """
    生成自监督规则命令
    """
    print("=" * 60)
    print("        自监督规则生成工具")
    print("=" * 60)
    
    # 验证输入参数
    if not os.path.exists(args.english_file):
        print(f"[ERROR] 英文映射文件不存在: {args.english_file}")
        return 1
    
    if not os.path.exists(args.chinese_file):
        print(f"[ERROR] 中文映射文件不存在: {args.chinese_file}")
        return 1
    
    # 加载双语映射文件
    print(f"[INFO] 加载英文映射文件: {args.english_file}")
    english_mappings = load_yaml_mappings(args.english_file)
    
    print(f"[INFO] 加载中文映射文件: {args.chinese_file}")
    chinese_mappings = load_yaml_mappings(args.chinese_file)
    
    # 生成翻译规则
    success = generate_translation_rules(english_mappings, chinese_mappings, args.output_file, args.mod_id)
    
    return 0 if success else 1

def command_update_rules(args: argparse.Namespace) -> int:
    """
    更新翻译规则命令
    """
    print("=" * 60)
    print("        翻译规则更新工具")
    print("=" * 60)
    
    # 验证输入参数
    if not os.path.exists(args.existing_rules):
        print(f"[ERROR] 现有规则文件不存在: {args.existing_rules}")
        return 1
    
    if not os.path.exists(args.new_english):
        print(f"[ERROR] 新的英文映射文件不存在: {args.new_english}")
        return 1
    
    if not os.path.exists(args.new_chinese):
        print(f"[ERROR] 新的中文映射文件不存在: {args.new_chinese}")
        return 1
    
    # 更新翻译规则
    success = update_translation_rules(args.existing_rules, args.new_english, args.new_chinese, args.output_file, args.mod_id)
    
    return 0 if success else 1

def main() -> int:
    """
    主函数
    """
    # 创建顶层解析器
    parser = argparse.ArgumentParser(
        description="统一的本地化工具命令行入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例用法：

# 提取映射规则
python -m src.common.localization_tool extract --source-dir ./Localization_File/source/English/src --output-file ./Localization_File/rule/English/mapping_rules.yaml

# 或使用入口脚本
python run_localization.py extract --source-dir ./Localization_File/source/English/src --output-file ./Localization_File/rule/English/mapping_rules.yaml

# 生成未映射内容报告
python -m src.common.localization_tool process-unmapped --rule-file ./Localization_File/rule/English/mapping_rules.yaml --report ./Localization_File/output/unmapped_report.txt

# 检测冲突
python -m src.common.localization_tool conflict --rule-file ./Localization_File/rule/English/mapping_rules.yaml --report ./Localization_File/output/conflict_report.txt
        """
    )
    
    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 1. 提取映射规则命令
    parser_extract = subparsers.add_parser("extract", help="提取映射规则")
    parser_extract.add_argument(
        "--source-dir",
        type=str,
        help="源目录路径，用于提取映射规则",
        default=None
    )
    parser_extract.add_argument(
        "--processed-dir",
        type=str,
        help="已处理文件夹路径，用于从已处理内容提取映射规则",
        default=None
    )
    parser_extract.add_argument(
        "--existing-rule",
        type=str,
        help="现有规则文件路径，用于合并新提取的规则",
        default=None
    )
    parser_extract.add_argument(
        "--output-file",
        type=str,
        help="输出规则文件路径",
        required=True
    )
    parser_extract.add_argument(
        "--language",
        type=str,
        choices=["Chinese", "English"],
        help="语言类型",
        default="English"
    )
    parser_extract.add_argument(
        "--mark-unmapped",
        action="store_true",
        help="将未映射内容标记为'unmapped'状态",
        default=True
    )
    
    # 2. 处理未映射内容命令
    parser_process = subparsers.add_parser("process-unmapped", help="处理未映射内容")
    parser_process.add_argument(
        "--rule-file",
        type=str,
        help="映射规则文件路径",
        required=True
    )
    parser_process.add_argument(
        "--report",
        type=str,
        help="生成未映射内容报告",
        default=None
    )
    parser_process.add_argument(
        "--list",
        action="store_true",
        help="列出所有未映射内容",
        default=False
    )
    parser_process.add_argument(
        "--mark-translated",
        action="store_true",
        help="将所有未映射内容标记为已翻译",
        default=False
    )
    parser_process.add_argument(
        "--output",
        type=str,
        help="输出文件路径",
        default=None
    )
    
    # 3. 冲突检测和解决命令
    parser_conflict = subparsers.add_parser("conflict", help="检测和解决规则冲突")
    parser_conflict.add_argument(
        "--rule-file",
        type=str,
        help="映射规则文件路径",
        required=True
    )
    parser_conflict.add_argument(
        "--report",
        type=str,
        help="生成冲突报告",
        default=None
    )
    parser_conflict.add_argument(
        "--resolve",
        action="store_true",
        help="解决冲突",
        default=False
    )
    parser_conflict.add_argument(
        "--resolve-strategy",
        type=str,
        choices=["latest", "first", "longest", "shortest", "manual"],
        help="冲突解决策略",
        default="latest"
    )
    
    # 4. 生成自监督规则命令
    parser_generate_rules = subparsers.add_parser("generate-rules", help="从双语数据生成翻译规则")
    parser_generate_rules.add_argument(
        "--english-file",
        type=str,
        help="英文映射文件路径",
        required=True
    )
    parser_generate_rules.add_argument(
        "--chinese-file",
        type=str,
        help="中文映射文件路径",
        required=True
    )
    parser_generate_rules.add_argument(
        "--output-file",
        type=str,
        help="输出规则文件路径",
        required=True
    )
    parser_generate_rules.add_argument(
        "--mod-id",
        type=str,
        help="模组ID",
        default=""
    )
    
    # 5. 更新翻译规则命令
    parser_update_rules = subparsers.add_parser("update-rules", help="更新现有翻译规则")
    parser_update_rules.add_argument(
        "--existing-rules",
        type=str,
        help="现有规则文件路径",
        required=True
    )
    parser_update_rules.add_argument(
        "--new-english",
        type=str,
        help="新的英文映射文件路径",
        required=True
    )
    parser_update_rules.add_argument(
        "--new-chinese",
        type=str,
        help="新的中文映射文件路径",
        required=True
    )
    parser_update_rules.add_argument(
        "--output-file",
        type=str,
        help="输出规则文件路径",
        required=True
    )
    parser_update_rules.add_argument(
        "--mod-id",
        type=str,
        help="模组ID",
        default=""
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 如果没有指定命令，显示帮助信息
    if not args.command:
        parser.print_help()
        return 1
    
    # 执行相应的命令
    if args.command == "extract":
        return command_extract(args)
    elif args.command == "process-unmapped":
        return command_process_unmapped(args)
    elif args.command == "conflict":
        return command_conflict(args)
    elif args.command == "generate-rules":
        return command_generate_rules(args)
    elif args.command == "update-rules":
        return command_update_rules(args)
    else:
        print(f"[ERROR] 未知命令: {args.command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
