#!/usr/bin/env python3
"""
合并中英文YAML映射文件，生成已完成翻译的映射文件
"""

import yaml
import os
import re
from typing import Dict, List, Any

def extract_file_line_id(full_id: str) -> str:
    """
    从完整id中提取文件名和行号，格式为"文件名:行号"
    例如：从"c:/xxx/Chinese/Quality Captains 1.7.0/src/xxx/CaptainsAutomatedShips.java:73"
    提取为"CaptainsAutomatedShips.java:73"
    """
    # 使用正则表达式提取文件名和行号
    match = re.search(r'([^\\/:]+\.java):(\d+)$', full_id)
    if match:
        return f"{match.group(1)}:{match.group(2)}"
    return full_id

def merge_mappings(chinese_file: str, english_file: str, output_file: str) -> None:
    """
    合并中英文YAML映射文件
    
    Args:
        chinese_file: 中文映射文件路径
        english_file: 英文映射文件路径
        output_file: 输出文件路径
    """
    # 加载中文映射文件
    with open(chinese_file, 'r', encoding='utf-8') as f:
        chinese_data = yaml.safe_load(f)
    
    # 加载英文映射文件
    with open(english_file, 'r', encoding='utf-8') as f:
        english_data = yaml.safe_load(f)
    
    # 按文件名分组中文映射
    chinese_by_file = {}
    for mapping in chinese_data['mappings']:
        file_name = extract_file_line_id(mapping['id']).split(':')[0]  # 只取文件名
        if file_name not in chinese_by_file:
            chinese_by_file[file_name] = []
        chinese_by_file[file_name].append(mapping)
    
    # 按文件名分组英文映射
    english_by_file = {}
    for mapping in english_data['mappings']:
        file_name = extract_file_line_id(mapping['id']).split(':')[0]  # 只取文件名
        if file_name not in english_by_file:
            english_by_file[file_name] = []
        english_by_file[file_name].append(mapping)
    
    # 合并映射
    merged_mappings = []
    translated_count = 0
    needs_review_count = 0
    
    for file_name, chinese_mappings in chinese_by_file.items():
        # 获取对应的英文映射
        english_mappings = english_by_file.get(file_name, [])
        
        # 按顺序配对中英文条目
        max_len = max(len(chinese_mappings), len(english_mappings))
        
        for i in range(max_len):
            if i < len(chinese_mappings):
                # 有中文条目
                merged_mapping = chinese_mappings[i].copy()
                
                if i < len(english_mappings):
                    # 有对应英文条目
                    merged_mapping['translated'] = english_mappings[i]['original']
                    merged_mapping['status'] = 'translated'
                    translated_count += 1
                else:
                    # 没有对应英文条目
                    merged_mapping['status'] = 'needs_review'
                    needs_review_count += 1
                
                merged_mappings.append(merged_mapping)
            else:
                # 只有英文条目，跳过
                pass
    
    # 创建输出数据
    output_data = {
        'version': chinese_data['version'],
        'created_at': chinese_data['created_at'],
        'id': chinese_data['id'],
        'mappings': merged_mappings
    }
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(output_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"合并完成，输出文件：{output_file}")
    print(f"总条目数：{len(merged_mappings)}")
    print("翻译状态统计：")
    print(f"  translated: {translated_count}")
    print(f"  needs_review: {needs_review_count}")
    
    # 计算翻译率
    total_count = len(merged_mappings)
    translation_rate = (translated_count / total_count) * 100 if total_count > 0 else 0
    print(f"翻译率：{translation_rate:.2f}%")

if __name__ == "__main__":
    # 定义文件路径
    chinese_file = r"c:\Users\Roki\Documents\GitHub\Tool\Localization_Tool\File\output\Extract_Chinese\Quality Captains 高质量舰长 1.7.0\Chinese_mappings.yaml"
    english_file = r"c:\Users\Roki\Documents\GitHub\Tool\Localization_Tool\File\output\Extract_English\Quality Captains 1.7.0\English_mappings.yaml"
    output_file = r"c:\Users\Roki\Documents\GitHub\Tool\Localization_Tool\File\output\Merged\Quality Captains 1.7.0\merged_mappings.yaml"
    
    # 创建输出目录
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 执行合并
    merge_mappings(chinese_file, english_file, output_file)
