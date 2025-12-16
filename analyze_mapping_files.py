#!/usr/bin/env python3
"""
分析中英文YAML映射文件的结构，找出匹配规律
"""

import yaml
import os
import re
from typing import Dict, List, Any

def extract_file_info(full_id: str) -> Dict[str, Any]:
    """
    从完整id中提取文件信息
    
    Args:
        full_id: 完整的id字符串
        
    Returns:
        文件信息字典，包含file_path, file_name, line_number
    """
    # 提取行号
    line_number = None
    line_match = re.search(r':(\d+)$', full_id)
    if line_match:
        line_number = int(line_match.group(1))
    
    # 提取文件名
    file_name = None
    name_match = re.search(r'([^\\/:]+\.java)', full_id)
    if name_match:
        file_name = name_match.group(1)
    
    return {
        'full_id': full_id,
        'file_name': file_name,
        'line_number': line_number
    }

def analyze_mapping_files(chinese_file: str, english_file: str) -> None:
    """
    分析中英文YAML映射文件的结构，找出匹配规律
    
    Args:
        chinese_file: 中文映射文件路径
        english_file: 英文映射文件路径
    """
    # 加载中文映射文件
    with open(chinese_file, 'r', encoding='utf-8') as f:
        chinese_data = yaml.safe_load(f)
    
    # 加载英文映射文件
    with open(english_file, 'r', encoding='utf-8') as f:
        english_data = yaml.safe_load(f)
    
    # 分析中文映射文件
    print("中文映射文件分析：")
    print(f"总条目数：{len(chinese_data['mappings'])}")
    
    # 按文件名分组
    chinese_by_file = {}
    for mapping in chinese_data['mappings']:
        info = extract_file_info(mapping['id'])
        if info['file_name'] not in chinese_by_file:
            chinese_by_file[info['file_name']] = []
        chinese_by_file[info['file_name']].append(info)
    
    print(f"涉及文件数：{len(chinese_by_file)}")
    for file_name, infos in chinese_by_file.items():
        print(f"  {file_name}: {len(infos)}条")
    
    # 分析英文映射文件
    print("\n英文映射文件分析：")
    print(f"总条目数：{len(english_data['mappings'])}")
    
    # 按文件名分组
    english_by_file = {}
    for mapping in english_data['mappings']:
        info = extract_file_info(mapping['id'])
        if info['file_name'] not in english_by_file:
            english_by_file[info['file_name']] = []
        english_by_file[info['file_name']].append(info)
    
    print(f"涉及文件数：{len(english_by_file)}")
    for file_name, infos in english_by_file.items():
        print(f"  {file_name}: {len(infos)}条")
    
    # 比较文件匹配情况
    print("\n文件匹配情况：")
    common_files = set(chinese_by_file.keys()) & set(english_by_file.keys())
    print(f"共同文件数：{len(common_files)}")
    
    for file_name in common_files:
        chinese_count = len(chinese_by_file[file_name])
        english_count = len(english_by_file[file_name])
        print(f"  {file_name}: 中文{chinese_count}条，英文{english_count}条，差异{abs(chinese_count - english_count)}条")
    
    # 检查不匹配的文件
    chinese_only = set(chinese_by_file.keys()) - set(english_by_file.keys())
    english_only = set(english_by_file.keys()) - set(chinese_by_file.keys())
    
    if chinese_only:
        print(f"\n仅中文文件：{chinese_only}")
    
    if english_only:
        print(f"\n仅英文文件：{english_only}")

if __name__ == "__main__":
    # 定义文件路径
    chinese_file = r"c:\Users\Roki\Documents\GitHub\Tool\Localization_Tool\File\output\Extract_Chinese\Quality Captains 高质量舰长 1.7.0\Chinese_mappings.yaml"
    english_file = r"c:\Users\Roki\Documents\GitHub\Tool\Localization_Tool\File\output\Extract_English\Quality Captains 1.7.0\English_mappings.yaml"
    
    # 执行分析
    analyze_mapping_files(chinese_file, english_file)
