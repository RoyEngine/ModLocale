#!/usr/bin/env python3
"""
检查合并后的YAML映射文件的翻译状态统计
"""

import yaml
import os

def check_translation_status(merged_file: str) -> None:
    """
    检查合并后的YAML映射文件的翻译状态统计
    
    Args:
        merged_file: 合并后的YAML映射文件路径
    """
    # 加载合并后的映射文件
    with open(merged_file, 'r', encoding='utf-8') as f:
        merged_data = yaml.safe_load(f)
    
    # 统计翻译状态
    status_counts = {}
    for mapping in merged_data['mappings']:
        status = mapping['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # 输出统计结果
    print(f"文件：{merged_file}")
    print(f"总条目数：{len(merged_data['mappings'])}")
    print("翻译状态统计：")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    # 计算翻译率
    translated_count = status_counts.get('translated', 0)
    total_count = len(merged_data['mappings'])
    translation_rate = (translated_count / total_count) * 100 if total_count > 0 else 0
    print(f"翻译率：{translation_rate:.2f}%")

if __name__ == "__main__":
    # 定义文件路径
    merged_file = r"c:\Users\Roki\Documents\GitHub\Tool\Localization_Tool\File\output\Merged\Quality Captains 1.7.0\merged_mappings.yaml"
    
    # 执行检查
    check_translation_status(merged_file)
