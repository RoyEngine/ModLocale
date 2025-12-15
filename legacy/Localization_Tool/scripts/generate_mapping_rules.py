#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
映射规则自动生成脚本

该脚本用于从源目录或已处理文件夹自动提取映射规则，生成带有未映射标记的YAML规则文件。
"""

import os
import sys
import argparse
from typing import List, Dict, Any

# 添加项目根目录到Python搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.yaml_utils import (
    extract_mappings_from_processed_folder,
    create_yaml_mapping_from_directory,
    save_yaml_mappings,
    load_yaml_mappings,
    generate_initial_yaml_mappings,
    update_mapping_status,
    merge_mapping_rules
)
from src.common.tree_sitter_utils import extract_ast_mappings


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="映射规则自动生成脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例用法：

# 从源目录提取映射规则
python scripts/generate_mapping_rules.py --source-dir ./source/English/src --output-file ./rule/English/mapping_rules.yaml

# 从已处理文件夹提取映射规则
python scripts/generate_mapping_rules.py --processed-dir ./output/Extract_English --output-file ./rule/English/extracted_rules.yaml

# 合并现有规则与新提取的规则
python scripts/generate_mapping_rules.py --source-dir ./source/English/src --existing-rule ./rule/English/old_rules.yaml --output-file ./rule/English/merged_rules.yaml
        """
    )
    
    # 添加命令行参数
    parser.add_argument(
        "--source-dir",
        type=str,
        help="源目录路径，用于提取映射规则",
        default=None
    )
    
    parser.add_argument(
        "--processed-dir",
        type=str,
        help="已处理文件夹路径，用于从已处理内容提取映射规则",
        default=None
    )
    
    parser.add_argument(
        "--existing-rule",
        type=str,
        help="现有规则文件路径，用于合并新提取的规则",
        default=None
    )
    
    parser.add_argument(
        "--output-file",
        type=str,
        help="输出规则文件路径",
        required=True
    )
    
    parser.add_argument(
        "--language",
        type=str,
        choices=["Chinese", "English"],
        help="语言类型",
        default="English"
    )
    
    parser.add_argument(
        "--mark-unmapped",
        action="store_true",
        help="将未映射内容标记为'unmapped'状态",
        default=True
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    print("=" * 60)
    print("          映射规则自动生成脚本")
    print("=" * 60)
    
    # 验证输入参数
    if not args.source_dir and not args.processed_dir:
        print("[ERROR] 必须提供 --source-dir 或 --processed-dir 参数")
        parser.print_help()
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


if __name__ == "__main__":
    sys.exit(main())
