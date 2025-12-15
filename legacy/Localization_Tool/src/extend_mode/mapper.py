#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字符串映射模块

该模块包含字符串映射功能，集成了Tree-sitter和ast-grep作为备用方案。
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

# 尝试导入Tree-sitter相关模块，设置初始化标志
TREE_SITTER_AVAILABLE = False
try:
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError as e:
    print(f"[WARN]  Tree-sitter导入失败: {e}")
    print("将使用ast-grep作为备用方案")


class StringMapper:
    """
    字符串映射类，集成了Tree-sitter和ast-grep作为备用方案
    """
    
    def __init__(self, mapping_rules: Dict[str, str], base_path: Optional[str] = None):
        """
        初始化字符串映射类
        
        Args:
            mapping_rules: Dict[str, str] - 映射规则字典
            base_path: Optional[str] - 基础路径，用于查找工具
        """
        self.mapping_rules = mapping_rules
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
            replacements: List[Dict[str, Any]] - 替换列表，用于存储需要替换的位置和内容
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
            
            # 如果字符串在映射规则中，添加到替换列表
            if string_content in self.mapping_rules:
                mapped_content = self.mapping_rules[string_content]
                replacements.append({
                    "start_byte": start_byte,
                    "end_byte": end_byte,
                    "original_str": original_str,
                    "mapped_str": f"\"{mapped_content}\""
                })
        
        # 递归遍历子节点
        for child in node.children:
            self._traverse_ast(child, content, replacements)
    
    def _apply_replacements(self, content: bytes, replacements: List[Dict[str, Any]]) -> bytes:
        """
        应用替换列表到文件内容
        
        Args:
            content: bytes - 原始文件内容
            replacements: List[Dict[str, Any]] - 替换列表
        
        Returns:
            bytes - 替换后的文件内容
        """
        # 按起始位置排序，从后往前替换，避免位置偏移
        replacements.sort(key=lambda x: x["start_byte"], reverse=True)
        
        # 应用替换
        result = content
        for replacement in replacements:
            result = (result[:replacement["start_byte"]] + 
                     replacement["mapped_str"].encode('utf-8') + 
                     result[replacement["end_byte"]:])
        
        return result
    
    def _map_with_tree_sitter(self, file_path: str, language: str) -> Dict[str, Any]:
        """
        使用Tree-sitter映射字符串
        
        Args:
            file_path: str - 文件路径
            language: str - 语言类型
        
        Returns:
            Dict[str, Any] - 映射结果
        """
        result = {
            "success": False,
            "message": "",
            "replacement_count": 0
        }
        
        if not self.tree_sitter_initialized:
            result["message"] = "Tree-sitter未初始化"
            return result
        
        try:
            # 选择解析器
            parser = self.java_parser if language.lower() == "java" else self.kotlin_parser
            if not parser:
                result["message"] = f"不支持的语言: {language}"
                return result
            
            # 读取文件内容
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 解析文件
            tree = parser.parse(content)
            root_node = tree.root_node
            
            # 遍历AST，收集需要替换的字符串
            replacements = []
            self._traverse_ast(root_node, content, replacements)
            
            if replacements:
                # 应用替换
                modified_content = self._apply_replacements(content, replacements)
                
                # 写入修改后的内容
                with open(file_path, 'wb') as f:
                    f.write(modified_content)
                
                result["success"] = True
                result["message"] = f"成功替换了{len(replacements)}个字符串"
                result["replacement_count"] = len(replacements)
                print(f"OK 使用Tree-sitter从{file_path}替换了{len(replacements)}个字符串")
            else:
                result["success"] = True
                result["message"] = "没有找到需要替换的字符串"
                result["replacement_count"] = 0
                print(f"ℹ️  使用Tree-sitter从{file_path}没有找到需要替换的字符串")
            
            return result
        except Exception as e:
            result["message"] = f"使用Tree-sitter映射失败: {e}"
            print(f"[ERROR] 使用Tree-sitter映射失败: {e}")
            return result
    
    def _map_with_regex(self, file_path: str) -> Dict[str, Any]:
        """
        使用正则表达式映射字符串
        
        Args:
            file_path: str - 文件路径
        
        Returns:
            Dict[str, Any] - 映射结果
        """
        result = {
            "success": False,
            "message": "",
            "replacement_count": 0
        }
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 正则表达式模式：匹配字符串字面量，支持单行
            string_pattern = r'"(\\.|[^"\\])*"'
            
            # 应用映射规则
            modified_content = content
            replacement_count = 0
            
            def replace_match(match):
                nonlocal replacement_count
                original_str = match.group()
                # 去除引号
                content = original_str[1:-1]
                
                # 如果内容在映射规则中，执行替换
                if content in self.mapping_rules:
                    mapped_content = self.mapping_rules[content]
                    replacement_count += 1
                    return f'"{mapped_content}"'
                return original_str
            
            # 执行替换
            modified_content = re.sub(string_pattern, replace_match, modified_content)
            
            # 写入修改后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            result["success"] = True
            result["message"] = f"成功替换了{replacement_count}个字符串"
            result["replacement_count"] = replacement_count
            print(f"OK 使用正则表达式从{file_path}替换了{replacement_count}个字符串")
            return result
        except Exception as e:
            result["message"] = f"使用正则表达式映射失败: {e}"
            print(f"[ERROR] 使用正则表达式映射失败: {e}")
            return result
    
    def map_file(self, file_path: str, language: str) -> Dict[str, Any]:
        """
        映射单个文件中的字符串，自动选择最佳映射方法
        
        Args:
            file_path: str - 文件路径
            language: str - 语言类型
        
        Returns:
            Dict[str, Any] - 映射结果
        """
        # 1. 首先尝试使用Tree-sitter映射
        result = self._map_with_tree_sitter(file_path, language)
        
        # 2. 如果Tree-sitter映射失败，尝试使用正则表达式
        if not result["success"]:
            result = self._map_with_regex(file_path)
        
        return result
    
    def map_directory(self, src_path: str, output_path: str) -> Dict[str, Any]:
        """
        映射目录中的所有文件
        
        Args:
            src_path: str - 源目录路径
            output_path: str - 输出目录路径
        
        Returns:
            Dict[str, Any] - 映射结果
        """
        mapping_result = {
            "total_count": 0,
            "success_count": 0,
            "fail_count": 0,
            "fail_reasons": [],
            "replacement_count": 0
        }
        
        # 创建输出目录
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # 遍历源目录中的所有文件
        src_dir = Path(src_path)
        for file_path in src_dir.rglob("*"):
            if file_path.is_file():
                mapping_result["total_count"] += 1
                
                # 确定文件语言
                file_ext = file_path.suffix.lower()
                language = "java" if file_ext == ".java" else "kotlin" if file_ext in [".kt", ".kts"] else ""
                
                if not language:
                    mapping_result["fail_count"] += 1
                    mapping_result["fail_reasons"].append(f"不支持的文件类型: {file_path}")
                    continue
                
                # 复制文件到输出目录
                rel_path = file_path.relative_to(src_dir)
                output_file_path = output_dir / rel_path
                output_file_path.parent.mkdir(exist_ok=True, parents=True)
                
                # 复制文件
                import shutil
                shutil.copy2(file_path, output_file_path)
                
                # 映射输出文件中的字符串
                result = self.map_file(str(output_file_path), language)
                
                if result["success"]:
                    mapping_result["success_count"] += 1
                    mapping_result["replacement_count"] += result["replacement_count"]
                else:
                    mapping_result["fail_count"] += 1
                    mapping_result["fail_reasons"].append(f"文件映射失败: {output_file_path} - {result['message']}")
        
        return mapping_result


def map_strings(
    src_path: str,
    mapping_rules_path: str,
    output_path: str,
    base_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用映射规则映射字符串

    Args:
        src_path: src目录路径
        mapping_rules_path: 映射规则文件路径
        output_path: 输出目录路径
        base_path: 基础路径，用于查找工具

    Returns:
        Dict[str, Any]: 映射结果
    """
    try:
        # 加载映射规则
        mapping_rules = load_mapping_rules(mapping_rules_path)
        
        # 初始化字符串映射器，传递base_path参数
        mapper = StringMapper(mapping_rules, base_path)
        
        # 映射目录中的所有文件
        return mapper.map_directory(src_path, output_path)
    except Exception as e:
        print(f"[ERROR] 映射字符串失败: {e}")
        return {
            "total_count": 0,
            "success_count": 0,
            "fail_count": 1,
            "fail_reasons": [f"映射字符串失败: {str(e)}"],
        }


def load_mapping_rules(mapping_rules_path: str) -> Dict[str, str]:
    """
    加载映射规则

    Args:
        mapping_rules_path: 映射规则文件路径

    Returns:
        Dict[str, str]: 映射规则
    """
    try:
        with open(mapping_rules_path, "r", encoding="utf-8") as f:
            mapping_rules = json.load(f)

        return mapping_rules.get("strings", {})
    except Exception as e:
        print(f"[ERROR] 加载映射规则失败: {e}")
        return {}
