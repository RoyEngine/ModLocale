#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字符串提取功能
"""

import os
import sys
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Localization_Tool.src.common.tree_sitter_utils import extract_ast_mappings, extract_strings_from_file
from Localization_Tool.src.common.yaml_utils import generate_initial_yaml_mappings

def test_string_extraction():
    """
    测试字符串提取功能
    """
    # 创建一个测试Java文件
    test_java_content = '''
public class TestClass {
    public static void main(String[] args) {
        String greeting = "Hello, World!";
        String message = "This is a test string.";
        System.out.println(greeting);
        System.out.println(message);
    }
}
    '''
    
    # 创建一个测试Kotlin文件
    test_kotlin_content = '''
class TestClass {
    fun main(args: Array<String>) {
        val greeting = "Hello, Kotlin!"
        val message = "This is a Kotlin test string."
        println(greeting)
        println(message)
    }
}
    '''
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 保存测试文件
        java_file = os.path.join(temp_dir, "TestClass.java")
        with open(java_file, 'w', encoding='utf-8') as f:
            f.write(test_java_content.strip())
        
        kotlin_file = os.path.join(temp_dir, "TestClass.kt")
        with open(kotlin_file, 'w', encoding='utf-8') as f:
            f.write(test_kotlin_content.strip())
        
        print("=" * 60)
        print("          测试字符串提取功能")
        print("=" * 60)
        
        # 测试Java文件字符串提取
        print(f"\n[TEST] 测试Java文件: {java_file}")
        java_strings = extract_strings_from_file(java_file)
        print(f"[INFO] 提取到 {len(java_strings)} 个字符串")
        for i, string in enumerate(java_strings):
            print(f"  [{i+1}] {string['original']} (行号: {string['meta']['line']})")
        
        # 测试Kotlin文件字符串提取
        print(f"\n[TEST] 测试Kotlin文件: {kotlin_file}")
        kotlin_strings = extract_strings_from_file(kotlin_file)
        print(f"[INFO] 提取到 {len(kotlin_strings)} 个字符串")
        for i, string in enumerate(kotlin_strings):
            print(f"  [{i+1}] {string['original']} (行号: {string['meta']['line']})")
        
        # 测试生成初步规则文件
        print(f"\n[TEST] 测试生成初步规则文件")
        ast_mappings = extract_ast_mappings(temp_dir)
        print(f"[INFO] 从目录提取到 {len(ast_mappings)} 个AST映射")
        
        yaml_mappings = generate_initial_yaml_mappings(ast_mappings)
        print(f"[INFO] 生成了 {len(yaml_mappings)} 个YAML映射")
        for i, mapping in enumerate(yaml_mappings):
            print(f"  [{i+1}] {mapping['original']} -> {mapping['translated']} (状态: {mapping['status']})")
        
        print("\n" + "=" * 60)
        print("          字符串提取测试完成")
        print("=" * 60)

if __name__ == "__main__":
    test_string_extraction()
