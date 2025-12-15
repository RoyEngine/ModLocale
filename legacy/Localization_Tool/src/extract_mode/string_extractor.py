#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Java字符串提取模块

该模块提供了Java代码的字符串提取、映射和注入功能。
"""

import re
import os
from difflib import SequenceMatcher
from typing import List, Dict, Any, Optional

import javalang
import yaml


class JavaStringInfo:
    """
    Java字符串信息类
    """
    def __init__(self, content: str, position: Dict[str, Any]):
        self.content = content
        self.position = position


def extract_java_strings(java_code: str, file_path: str = "") -> List[JavaStringInfo]:
    """
    从Java代码中提取字符串
    
    Args:
        java_code: Java代码字符串
        file_path: 文件名，用于定位
        
    Returns:
        List[JavaStringInfo]: 提取的字符串信息列表
    """
    strings = []
    
    try:
        tree = javalang.parse.parse(java_code)
        
        for path, node in tree.filter(javalang.tree.StringLiteral):
            # 提取原始字符串内容(去除双引号)
            content = node.value[1:-1].replace('\\"', '"')
            strings.append(JavaStringInfo(
                content=content,
                position={
                    "file": file_path or getattr(node.position, 'source', {}).get('name', ''),
                    "line": getattr(node.position, 'line', 0),
                    "column": getattr(node.position, 'column', 0)
                }
            ))
    except Exception as e:
        # 如果解析失败，尝试使用正则表达式作为后备方案
        pattern = r'"(?:[^"\\]|\\.)*"'
        for match in re.finditer(pattern, java_code):
            content = match.group(0)[1:-1].replace('\\"', '"')
            strings.append(JavaStringInfo(
                content=content,
                position={
                    "file": file_path,
                    "line": java_code[:match.start()].count('\n') + 1,
                    "column": match.start() - java_code.rfind('\n', 0, match.start())
                }
            ))
    
    return strings


class LocalizationMapper:
    """
    双语映射管理类
    """
    def __init__(self, zh_file: Optional[str] = None, en_file: Optional[str] = None):
        self.zh_strings = {}
        self.en_strings = {}
        
        if zh_file and os.path.exists(zh_file):
            with open(zh_file, 'r', encoding='utf-8') as f:
                self.zh_strings = yaml.safe_load(f) or {}
        
        if en_file and os.path.exists(en_file):
            with open(en_file, 'r', encoding='utf-8') as f:
                self.en_strings = yaml.safe_load(f) or {}
    
    def get_translation(self, key: str) -> str:
        """
        获取翻译
        
        Args:
            key: 翻译键(格式：Section.key)
            
        Returns:
            str: 翻译值
        """
        # 解析键的结构
        if '.' in key:
            section, sub_key = key.split('.', 1)
            if section in self.en_strings and sub_key in self.en_strings[section]:
                return self.en_strings[section][sub_key]
        return key
    
    def add_translation(self, key: str, en_value: str) -> None:
        """
        添加翻译
        
        Args:
            key: 翻译键(格式：Section.key)
            en_value: 英文翻译值
        """
        # 解析键的结构
        if '.' in key:
            section, sub_key = key.split('.', 1)
            # 确保section存在
            if section not in self.en_strings:
                self.en_strings[section] = {}
            # 添加翻译
            self.en_strings[section][sub_key] = en_value
        else:
            self.en_strings[key] = en_value
    
    def save(self, output_file: str) -> None:
        """
        保存映射文件
        
        Args:
            output_file: 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.en_strings, f, allow_unicode=True, default_flow_style=False)


class ContextualMapper:
    """
    上下文感知映射类
    """
    def __init__(self):
        self.mapping = {}
    
    def add_context(self, key: str, context: str) -> None:
        """
        添加上下文
        
        Args:
            key: 字符串键
            context: 上下文
        """
        self.mapping[key] = context
    
    def find_best_match(self, zh_str: str) -> str:
        """
        查找最佳匹配
        
        Args:
            zh_str: 中文字符串
            
        Returns:
            str: 最佳匹配的英文字符串
        """
        max_ratio = 0
        best_match = zh_str
        
        for key, context in self.mapping.items():
            ratio = SequenceMatcher(None, zh_str, context).ratio()
            if ratio > max_ratio:
                max_ratio = ratio
                best_match = key
        
        return best_match


def inject_translations(java_code: str, translation_map: Dict[str, str]) -> str:
    """
    注入翻译
    
    Args:
        java_code: Java代码字符串
        translation_map: 翻译映射
        
    Returns:
        str: 注入翻译后的Java代码
    """
    # 逐行处理代码
    lines = java_code.split('\n')
    result = []
    current_localization_key = None
    
    for line in lines:
        stripped_line = line.strip()
        
        # 检查是否有LOCALIZE标记
        if stripped_line.startswith('// LOCALIZE:'):
            # 提取本地化键
            current_localization_key = stripped_line.replace('// LOCALIZE:', '').strip()
            result.append(line)
        elif current_localization_key and '"' in line:
            # 找到包含字符串的行，进行替换
            # 查找字符串的开始和结束位置
            string_start = line.find('"')
            if string_start != -1:
                # 查找字符串结束位置
                string_end = string_start + 1
                while string_end < len(line) and line[string_end] != '"':
                    if line[string_end] == '\\':
                        string_end += 2
                    else:
                        string_end += 1
                
                if string_end < len(line):
                    # 替换字符串内容
                    if current_localization_key in translation_map:
                        translated_line = (line[:string_start+1] +
                                         translation_map[current_localization_key] +
                                         line[string_end:])
                        result.append(translated_line)
                        # 重置当前本地化键
                        current_localization_key = None
                    else:
                        result.append(line)
                        current_localization_key = None
                else:
                    result.append(line)
            else:
                result.append(line)
                current_localization_key = None
        else:
            result.append(line)
    
    return '\n'.join(result)


def validate_placeholders(zh_str: str, en_str: str) -> bool:
    """
    验证占位符
    
    Args:
        zh_str: 中文字符串
        en_str: 英文字符串
        
    Returns:
        bool: 占位符是否匹配
    """
    zh_placeholders = re.findall(r'%\w+', zh_str)
    en_placeholders = re.findall(r'%\w+', en_str)
    
    if len(zh_placeholders) != len(en_placeholders):
        return False
    
    for z, e in zip(zh_placeholders, en_placeholders):
        if not is_compatible(z, e):
            return False
    
    return True


def is_compatible(zh_p: str, en_p: str) -> bool:
    """
    检查占位符是否兼容
    
    Args:
        zh_p: 中文占位符
        en_p: 英文占位符
        
    Returns:
        bool: 是否兼容
    """
    # 只有相同类型的占位符才兼容
    return zh_p == en_p


def save_extracted_strings(extracted_data: List[JavaStringInfo], output_path: str, output_format: str = "yaml") -> bool:
    """
    保存提取的字符串
    
    Args:
        extracted_data: 提取的字符串数据
        output_path: 输出路径
        output_format: 输出格式(yaml或json)
        
    Returns:
        bool: 是否保存成功
    """
    try:
        # 创建输出目录
        os.makedirs(output_path, exist_ok=True)
        
        # 转换为可序列化格式
        serializable_data = {
            "strings": [
                {
                    "content": string.content,
                    "position": string.position
                }
                for string in extracted_data
            ]
        }
        
        # 保存文件
        output_file = os.path.join(output_path, f"extracted_strings.{output_format}")
        if output_format.lower() == "yaml":
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(serializable_data, f, allow_unicode=True, default_flow_style=False)
        else:  # json
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"保存提取的字符串失败：{e}")
        return False
