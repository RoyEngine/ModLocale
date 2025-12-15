#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
未映射内容处理脚本

该脚本用于处理映射规则中的未映射内容，生成报告并提供可视化功能。
"""

import os
import sys
import argparse
import json
from typing import List, Dict, Any
from datetime import datetime

# 添加项目根目录到Python搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.yaml_utils import (
    load_yaml_mappings,
    save_yaml_mappings,
    update_mapping_status,
    RuleConflictDetector
)


def generate_unmapped_report(rules: List[Dict[str, Any]], output_file: str = None) -> Dict[str, Any]:
    """
    生成未映射内容报告
    
    Args:
        rules: 映射规则列表
        output_file: 输出报告文件路径
    
    Returns:
        Dict[str, Any]: 未映射内容报告
    """
    # 统计未映射内容
    total_rules = len(rules)
    unmapped_rules = [r for r in rules if r['status'] == 'unmapped']
    unmapped_count = len(unmapped_rules)
    mapped_count = total_rules - unmapped_count
    
    # 计算未映射比例
    unmapped_ratio = (unmapped_count / total_rules) * 100 if total_rules > 0 else 0
    
    # 按文件路径分组统计未映射内容
    file_statistics = {}
    for rule in unmapped_rules:
        # 从id中提取文件路径(格式：文件路径:行号)
        if ':' in rule['id']:
            file_path = rule['id'].split(':')[0]
        else:
            file_path = 'unknown'
        
        if file_path not in file_statistics:
            file_statistics[file_path] = {
                'unmapped_count': 0,
                'rules': []
            }
        
        file_statistics[file_path]['unmapped_count'] += 1
        file_statistics[file_path]['rules'].append(rule)
    
    # 生成报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_rules': total_rules,
        'mapped_count': mapped_count,
        'unmapped_count': unmapped_count,
        'unmapped_ratio': round(unmapped_ratio, 2),
        'file_statistics': file_statistics,
        'unmapped_rules': unmapped_rules
    }
    
    # 保存报告
    if output_file:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 保存为JSON格式
        if output_file.endswith('.json'):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"[OK] JSON报告已保存到: {output_file}")
        # 保存为文本格式
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# 未映射内容报告\n\n")
                f.write(f"生成时间: {report['timestamp']}\n")
                f.write(f"总规则数: {report['total_rules']}\n")
                f.write(f"已映射规则: {report['mapped_count']}\n")
                f.write(f"未映射规则: {report['unmapped_count']}\n")
                f.write(f"未映射比例: {report['unmapped_ratio']}%\n\n")
                
                f.write("## 按文件统计\n\n")
                for file_path, stats in sorted(file_statistics.items(), key=lambda x: x[1]['unmapped_count'], reverse=True):
                    f.write(f"### {file_path}\n")
                    f.write(f"未映射数量: {stats['unmapped_count']}\n")
                    f.write("\n")
                    for rule in stats['rules'][:10]:  # 每个文件只显示前10个
                        f.write(f"- {rule['original']}\n")
                    if len(stats['rules']) > 10:
                        f.write(f"... 还有 {len(stats['rules']) - 10} 条未映射内容\n")
                    f.write("\n")
            print(f"[OK] 文本报告已保存到: {output_file}")
    
    return report


def list_unmapped_content(rules: List[Dict[str, Any]], output_file: str = None) -> None:
    """
    列出所有未映射内容
    
    Args:
        rules: 映射规则列表
        output_file: 输出文件路径
    """
    # 过滤未映射规则
    unmapped_rules = [r for r in rules if r['status'] == 'unmapped']
    
    if not unmapped_rules:
        print("[INFO] 没有未映射内容")
        return
    
    output_lines = []
    output_lines.append("=" * 60)
    output_lines.append("          未映射内容列表")
    output_lines.append("=" * 60)
    output_lines.append(f"未映射内容总数: {len(unmapped_rules)}")
    output_lines.append("\n")
    
    for i, rule in enumerate(unmapped_rules, 1):
        output_lines.append(f"[{i}] {rule['original']}")
        output_lines.append(f"  文件: {rule['id'].split(':')[0] if ':' in rule['id'] else 'unknown'}")
        if rule.get('context'):
            output_lines.append(f"  上下文: {rule['context']}")
        output_lines.append("")
    
    output_content = "\n".join(output_lines)
    
    if output_file:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"[OK] 未映射内容列表已保存到: {output_file}")
    else:
        print(output_content)


def mark_unmapped_as_translated(rules: List[Dict[str, Any]], output_file: str = None) -> List[Dict[str, Any]]:
    """
    将所有未映射内容标记为已翻译
    
    Args:
        rules: 映射规则列表
        output_file: 输出文件路径
    
    Returns:
        List[Dict[str, Any]]: 更新后的映射规则列表
    """
    updated_rules = []
    updated_count = 0
    
    for rule in rules:
        updated_rule = rule.copy()
        if updated_rule['status'] == 'unmapped':
            updated_rule['status'] = 'translated'
            updated_rule['translated'] = updated_rule['original']
            updated_count += 1
        updated_rules.append(updated_rule)
    
    print(f"[OK] 已将 {updated_count} 条未映射内容标记为已翻译")
    
    if output_file:
        if save_yaml_mappings(updated_rules, output_file):
            print(f"[OK] 更新后的规则已保存到: {output_file}")
        else:
            print(f"[ERROR] 保存更新后的规则失败: {output_file}")
    
    return updated_rules


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="未映射内容处理脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例用法：

# 生成未映射内容报告
python scripts/process_unmapped.py --rule-file ./rule/English/mapping_rules.yaml --report ./output/unmapped_report.txt

# 列出所有未映射内容
python scripts/process_unmapped.py --rule-file ./rule/English/mapping_rules.yaml --list

# 保存未映射内容列表到文件
python scripts/process_unmapped.py --rule-file ./rule/English/mapping_rules.yaml --list --output ./output/unmapped_list.txt

# 将未映射内容标记为已翻译
python scripts/process_unmapped.py --rule-file ./rule/English/mapping_rules.yaml --mark-translated --output ./rule/English/updated_rules.yaml
        """
    )
    
    # 添加命令行参数
    parser.add_argument(
        "--rule-file",
        type=str,
        help="映射规则文件路径",
        required=True
    )
    
    parser.add_argument(
        "--report",
        type=str,
        help="生成未映射内容报告",
        default=None
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有未映射内容",
        default=False
    )
    
    parser.add_argument(
        "--mark-translated",
        action="store_true",
        help="将所有未映射内容标记为已翻译",
        default=False
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="输出文件路径",
        default=None
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
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
    
    # 如果没有指定任何操作，显示帮助信息
    if not any([args.report, args.list, args.mark_translated]):
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
