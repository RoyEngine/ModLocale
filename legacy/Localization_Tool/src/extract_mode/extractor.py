#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字符串提取模块

该模块包含字符串提取和保存功能，集成了Tree-sitter和ast-grep作为备用方案。
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# 添加项目根目录到Python搜索路径
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.append(src_dir)

from common.tools_integrator import ToolsIntegrator
from src.extract_mode.string_extractor import (
    extract_java_strings, save_extracted_strings as save_java_strings
)

# 尝试导入Tree-sitter相关模块，设置初始化标志
TREE_SITTER_AVAILABLE = False
try:
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError as e:
    print(f"[WARN]  Tree-sitter导入失败: {e}")
    print("将使用ast-grep作为备用方案")


class StringExtractor:
    """
    字符串提取类，集成了Tree-sitter和ast-grep作为备用方案
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        初始化字符串提取类
        
        Args:
            base_path: Optional[str] - 基础路径，用于查找工具
        """
        self.tree_sitter_initialized = False
        self.java_parser = None
        self.kotlin_parser = None
        self.tools_integrator = ToolsIntegrator(base_path)
        
        # 如果Tree-sitter可用，尝试初始化
        if TREE_SITTER_AVAILABLE:
            self._init_tree_sitter()
    
    def _init_tree_sitter(self):
        """
        初始化Tree-sitter解析器
        """
        try:
            # 初始化解析器
            self.java_parser = Parser()
            self.java_parser.language = Language(self.tools_integrator.base_path, "java")
            
            self.kotlin_parser = Parser()
            self.kotlin_parser.language = Language(self.tools_integrator.base_path, "kotlin")
            
            self.tree_sitter_initialized = True
            print("OK Tree-sitter初始化成功")
        except Exception as e:
            print(f"[ERROR] Tree-sitter初始化失败: {e}")
            self.tree_sitter_initialized = False
    
    def _has_chinese(self, s: str) -> bool:
        """
        判断字符串是否包含中文
        
        Args:
            s: str - 字符串
        
        Returns:
            bool - 是否包含中文
        """
        if not s:
            return False
        return any('\u4e00' <= c <= '\u9fff' for c in s)
    
    def _traverse_ast(self, node, content: bytes, replacements: List[Dict[str, Any]]):
        """
        遍历AST，找到所有字符串字面量节点
        
        Args:
            node: 树节点
            content: bytes - 原始文件内容
            replacements: List[Dict[str, Any]] - 替换列表，用于存储需要提取的字符串
        """
        # 检查当前节点是否是字符串字面量
        string_types = ["string_literal", "string", "raw_string_literal"]
        if node.type in string_types:
            # 获取字符串内容的范围
            start_byte = node.start_byte
            end_byte = node.end_byte
            
            # 读取原始字符串内容
            original_str = content[start_byte:end_byte].decode('utf-8')
            
            # 去除引号
            if original_str.startswith('"') and original_str.endswith('"'):
                string_content = original_str[1:-1]
            else:
                string_content = original_str
            
            # 记录提取的字符串
            replacements.append({
                "content": string_content,
                "line_number": node.start_point[0] + 1,
                "start_column": node.start_point[1] + 1,
                "end_line": node.end_point[0] + 1,
                "end_column": node.end_point[1] + 1
            })
        
        # 递归遍历子节点
        for child in node.children:
            self._traverse_ast(child, content, replacements)
    
    def _extract_with_tree_sitter(self, file_path: str, language: str) -> List[Dict[str, Any]]:
        """
        使用Tree-sitter从文件中提取字符串
        
        Args:
            file_path: str - 文件路径
            language: str - 语言类型
        
        Returns:
            List[Dict[str, Any]] - 提取的字符串列表
        """
        extracted_strings = []
        
        if not self.tree_sitter_initialized:
            return extracted_strings
        
        try:
            # 选择解析器
            parser = self.java_parser if language.lower() == "java" else self.kotlin_parser
            if not parser:
                return extracted_strings
            
            # 读取文件内容
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 解析文件
            tree = parser.parse(content)
            root_node = tree.root_node
            
            # 遍历AST，提取字符串
            self._traverse_ast(root_node, content, extracted_strings)
            
            print(f"OK 使用Tree-sitter从{file_path}提取了{len(extracted_strings)}个字符串")
            return extracted_strings
        except Exception as e:
            print(f"[ERROR] 使用Tree-sitter提取字符串失败: {e}")
            return []
    
    def _extract_with_ast_grep(self, file_path: str, language: str) -> List[Dict[str, Any]]:
        """
        使用ast-grep从文件中提取字符串
        
        Args:
            file_path: str - 文件路径
            language: str - 语言类型
        
        Returns:
            List[Dict[str, Any]] - 提取的字符串列表
        """
        return self.tools_integrator.extract_strings_with_ast_grep(file_path, language)
    
    def _extract_with_regex(self, file_path: str) -> List[Dict[str, Any]]:
        """
        使用正则表达式从文件中提取字符串
        
        Args:
            file_path: str - 文件路径
        
        Returns:
            List[Dict[str, Any]] - 提取的字符串列表
        """
        extracted_strings = []
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 正则表达式匹配字符串
            string_pattern = r'"(\\.|[^"\\])*"'
            lines = content.splitlines()
            
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(string_pattern, line)
                for match in matches:
                    string_content = match.group()
                    # 去除引号
                    actual_content = string_content[1:-1] if string_content.startswith('"') and string_content.endswith('"') else string_content
                    extracted_strings.append({
                        "content": actual_content,
                        "line_number": line_num,
                        "context": line.strip()
                    })
            
            print(f"OK 使用正则表达式从{file_path}提取了{len(extracted_strings)}个字符串")
            return extracted_strings
        except Exception as e:
            print(f"[ERROR] 使用正则表达式提取字符串失败: {e}")
            return []
    
    def _extract_with_javalang(self, file_path: str) -> List[Dict[str, Any]]:
        """
        使用javalang从文件中提取字符串
        
        Args:
            file_path: str - 文件路径
        
        Returns:
            List[Dict[str, Any]] - 提取的字符串列表
        """
        extracted_strings = []
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用javalang提取字符串
            java_strings = extract_java_strings(content, file_path)
            
            # 转换为内部格式
            for string_info in java_strings:
                extracted_strings.append({
                    "content": string_info.content,
                    "line_number": string_info.position.get("line", 0),
                    "start_column": string_info.position.get("column", 0),
                    "context": f"Line {string_info.position.get('line', 0)}"
                })
            
            print(f"OK 使用javalang从{file_path}提取了{len(extracted_strings)}个字符串")
            return extracted_strings
        except Exception as e:
            print(f"[ERROR] 使用javalang提取字符串失败: {e}")
            return []
    
    def extract_from_file(self, file_path: str, language: str) -> List[Dict[str, Any]]:
        """
        从单个文件中提取字符串，自动选择最佳提取方法
        
        Args:
            file_path: str - 文件路径
            language: str - 语言类型
        
        Returns:
            List[Dict[str, Any]] - 提取的字符串列表
        """
        # 1. 首先尝试使用Tree-sitter提取
        extracted_strings = self._extract_with_tree_sitter(file_path, language)
        
        # 2. 如果Tree-sitter提取失败或没有提取到字符串，尝试使用ast-grep
        if not extracted_strings:
            extracted_strings = self._extract_with_ast_grep(file_path, language)
        
        # 3. 如果ast-grep提取失败或没有提取到字符串，尝试使用javalang
        if not extracted_strings and language.lower() == "java":
            extracted_strings = self._extract_with_javalang(file_path)
        
        # 4. 如果javalang提取失败或没有提取到字符串，尝试使用正则表达式
        if not extracted_strings:
            extracted_strings = self._extract_with_regex(file_path)
        
        return extracted_strings
    
    def _classify_string(self, content: str) -> Dict[str, bool]:
        """
        对字符串进行分类
        
        Args:
            content: str - 字符串内容
        
        Returns:
            Dict[str, bool] - 分类结果
        """
        return {
            "has_chinese": self._has_chinese(content),
            "is_short": len(content) < 10,
            "is_medium": 10 <= len(content) < 50,
            "is_long": len(content) >= 50,
            "has_format_specifiers": any(c in content for c in ["%s", "%d", "%f", "%c", "%b", "%x", "%X", "%o"]),
            "has_escape_sequences": any(esc in content for esc in ["\\n", "\\t", "\\r", '"', "'", "\\\\"]),
            "is_empty": len(content.strip()) == 0,
            "has_numbers": any(char.isdigit() for char in content),
            "has_symbols": any(not char.isalnum() and not char.isspace() for char in content)
        }
    
    def _generate_string_id(self, content: str, line_number: int, file_path: str) -> str:
        """
        生成字符串ID，用于去重和跟踪
        
        Args:
            content: str - 字符串内容
            line_number: int - 行号
            file_path: str - 文件路径
        
        Returns:
            str - 字符串ID
        """
        import hashlib
        # 使用内容、行号和文件路径生成唯一ID
        unique_key = f"{content}:{line_number}:{file_path}"
        return hashlib.md5(unique_key.encode()).hexdigest()
    
    def extract_from_directory(self, directory: str, language: str) -> Dict[str, Any]:
        """
        从目录中提取字符串，实现去重与分类
        
        Args:
            directory: str - 目录路径
            language: str - 语言类型
        
        Returns:
            Dict[str, Any] - 提取的字符串数据，包含去重和分类信息
        """
        extracted_data = {
            "version": "1.0",
            "language": language,
            "strings": {},  # 去重后的字符串字典，键为字符串内容
            "string_details": {},  # 详细的字符串信息，键为字符串ID
            "string_mappings": {},  # 字符串内容到ID的映射，支持多个ID对应一个内容(不同位置)
            "categories": {
                "has_chinese": [],
                "only_english": [],
                "short_strings": [],
                "medium_strings": [],
                "long_strings": [],
                "with_format_specifiers": [],
                "with_escape_sequences": [],
                "empty_strings": [],
                "with_numbers": [],
                "with_symbols": []
            },
            "metadata": {
                "total_count": 0,
                "unique_count": 0,
                "success_count": 0,
                "fail_count": 0,
                "fail_reasons": [],
                "category_stats": {
                    "has_chinese": 0,
                    "only_english": 0,
                    "short_strings": 0,
                    "medium_strings": 0,
                    "long_strings": 0,
                    "with_format_specifiers": 0,
                    "with_escape_sequences": 0,
                    "empty_strings": 0,
                    "with_numbers": 0,
                    "with_symbols": 0
                }
            },
            "files": {}
        }
        
        # 确定文件扩展名
        extensions = [".java"] if language.lower() == "java" else [".kt", ".kts"]
        
        # 遍历目录中的所有文件
        directory_path = Path(directory)
        for ext in extensions:
            for file_path in directory_path.rglob(f"*{ext}"):
                file_path_str = str(file_path)
                rel_path = str(file_path.relative_to(directory_path))
                
                try:
                    # 提取字符串
                    strings = self.extract_from_file(file_path_str, language)
                    
                    # 更新统计信息
                    extracted_data["metadata"]["total_count"] += len(strings)
                    if strings:
                        extracted_data["metadata"]["success_count"] += 1
                        extracted_data["files"][rel_path] = strings
                        
                        # 处理每个提取的字符串
                        for string_info in strings:
                            content = string_info["content"]
                            line_number = string_info.get("line_number", 0)
                            
                            # 生成字符串ID
                            string_id = self._generate_string_id(content, line_number, rel_path)
                            
                            # 对字符串进行分类
                            classification = self._classify_string(content)
                            
                            # 将字符串添加到主字典(去重)
                            if content not in extracted_data["strings"]:
                                extracted_data["strings"][content] = {
                                    "content": content,
                                    "occurrences": 1,
                                    "classification": classification,
                                    "first_occurrence": {
                                        "file": rel_path,
                                        "line": line_number
                                    },
                                    "all_occurrences": [
                                        {
                                            "file": rel_path,
                                            "line": line_number
                                        }
                                    ]
                                }
                                extracted_data["metadata"]["unique_count"] += 1
                            else:
                                # 更新现有字符串的出现次数和位置
                                extracted_data["strings"][content]["occurrences"] += 1
                                extracted_data["strings"][content]["all_occurrences"].append({
                                    "file": rel_path,
                                    "line": line_number
                                })
                            
                            # 添加字符串详细信息
                            extracted_data["string_details"][string_id] = {
                                "id": string_id,
                                "content": content,
                                "file": rel_path,
                                "line": line_number,
                                "classification": classification
                            }
                            
                            # 更新字符串到ID的映射
                            if content not in extracted_data["string_mappings"]:
                                extracted_data["string_mappings"][content] = []
                            if string_id not in extracted_data["string_mappings"][content]:
                                extracted_data["string_mappings"][content].append(string_id)
                            
                            # 根据分类将字符串添加到不同类别
                            if classification["has_chinese"]:
                                extracted_data["categories"]["has_chinese"].append(string_id)
                                extracted_data["metadata"]["category_stats"]["has_chinese"] += 1
                            else:
                                extracted_data["categories"]["only_english"].append(string_id)
                                extracted_data["metadata"]["category_stats"]["only_english"] += 1
                            
                            if classification["is_short"]:
                                extracted_data["categories"]["short_strings"].append(string_id)
                                extracted_data["metadata"]["category_stats"]["short_strings"] += 1
                            elif classification["is_medium"]:
                                extracted_data["categories"]["medium_strings"].append(string_id)
                                extracted_data["metadata"]["category_stats"]["medium_strings"] += 1
                            else:  # is_long
                                extracted_data["categories"]["long_strings"].append(string_id)
                                extracted_data["metadata"]["category_stats"]["long_strings"] += 1
                            
                            if classification["has_format_specifiers"]:
                                extracted_data["categories"]["with_format_specifiers"].append(string_id)
                                extracted_data["metadata"]["category_stats"]["with_format_specifiers"] += 1
                            
                            if classification["has_escape_sequences"]:
                                extracted_data["categories"]["with_escape_sequences"].append(string_id)
                                extracted_data["metadata"]["category_stats"]["with_escape_sequences"] += 1
                            
                            if classification["is_empty"]:
                                extracted_data["categories"]["empty_strings"].append(string_id)
                                extracted_data["metadata"]["category_stats"]["empty_strings"] += 1
                            
                            if classification["has_numbers"]:
                                extracted_data["categories"]["with_numbers"].append(string_id)
                                extracted_data["metadata"]["category_stats"]["with_numbers"] += 1
                            
                            if classification["has_symbols"]:
                                extracted_data["categories"]["with_symbols"].append(string_id)
                                extracted_data["metadata"]["category_stats"]["with_symbols"] += 1
                    else:
                        extracted_data["metadata"]["fail_count"] += 1
                        extracted_data["metadata"]["fail_reasons"].append(f"未提取到字符串: {rel_path}")
                except Exception as e:
                    extracted_data["metadata"]["fail_count"] += 1
                    extracted_data["metadata"]["fail_reasons"].append(f"提取失败: {rel_path} - {str(e)}")
        
        # 移除空字符串(如果需要)
        for content in list(extracted_data["strings"].keys()):
            if extracted_data["strings"][content]["classification"]["is_empty"]:
                del extracted_data["strings"][content]
        
        return extracted_data


def extract_strings(
    src_path: str,
    language: str = "English",
    base_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    从src目录提取字符串

    Args:
        src_path: src目录路径
        language: 语言类型
        base_path: 基础路径，用于查找工具

    Returns:
        Dict[str, Any]: 提取的字符串数据
    """
    try:
        extractor = StringExtractor(base_path)
        return extractor.extract_from_directory(src_path, language)
    except Exception as e:
        print(f"[ERROR] 提取字符串失败: {e}")
        return {
            "version": "1.0",
            "language": language,
            "strings": {},
            "metadata": {
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"提取字符串失败: {str(e)}"],
            },
        }


def save_extracted_strings(
    extracted_data: Dict[str, Any], output_path: str, language: str,
    output_format: str = "json", mod_folder_name: str = "unknown", version: str = "unknown", timestamp: str = ""
) -> bool:
    """
    保存提取的字符串到规则文件

    Args:
        extracted_data: 提取的字符串数据
        output_path: 输出路径
        language: 语言类型
        output_format: 输出格式(json或yaml)
        mod_folder_name: 模组文件夹名
        version: 模组版本号
        timestamp: 时间戳

    Returns:
        bool: 是否成功保存
    """
    try:
        # 构建新的输出文件夹路径
        if mod_folder_name != "unknown" and timestamp:
            mode = "Extract"
            
            # 从mod_folder_name中提取纯净的模组名称(去掉末尾可能的版本号)
            from src.common import extract_pure_mod_name
            pure_mod_name = extract_pure_mod_name(mod_folder_name)
            
            output_folder_name = f"{pure_mod_name}_{version}_{mode}_{timestamp}_{language}_strings"
            output_path = os.path.join(os.path.dirname(output_path), output_folder_name)
        
        # 确保输出目录存在
        os.makedirs(output_path, exist_ok=True)

        # 构建规则文件名
        rule_file = os.path.join(
            output_path, f"strings_{language.lower()}.{output_format}"
        )

        # 保存提取的字符串
        if output_format.lower() == "yaml":
            import yaml
            with open(rule_file, "w", encoding="utf-8") as f:
                yaml.dump(extracted_data, f, ensure_ascii=False, default_flow_style=False)
        else:  # json
            with open(rule_file, "w", encoding="utf-8") as f:
                json.dump(extracted_data, f, ensure_ascii=False, indent=2)

        print(f"OK 提取的字符串已保存到: {rule_file}")
        return True
    except Exception as e:
        print(f"[ERROR] 保存提取的字符串失败: {e}")
        return False
