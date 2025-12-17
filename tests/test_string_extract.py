#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字符串提取功能
"""

import os
import sys
import tempfile

# 从当前目录导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.common.tree_sitter_utils import extract_ast_mappings, extract_strings_from_file
from src.common.yaml_utils import generate_initial_yaml_mappings

def test_string_extraction():
    """
    测试字符串提取功能
    """
    print("=" * 60)
    print("          测试字符串提取功能")
    print("=" * 60)
    
    # 创建测试文件内容
    # 1. Java文件
    test_java_content = '''
public class TestClass {
    public static void main(String[] args) {
        String greeting = "Hello, World!";
        String message = "This is a test string.";
        String multiline = """
This is a
multiline string
in Java
""";
        
        System.out.println(greeting);
        System.out.println(message);
        System.out.println(multiline);
    }
}
    '''
    
    # 2. Kotlin文件
    test_kotlin_content = '''
class TestClass {
    fun main(args: Array<String>) {
        val greeting = "Hello, Kotlin!"
        val message = "This is a Kotlin test string."
        
        println(greeting);
        println(message);
    }
}
    '''
    
    # 3. Python文件
    test_python_content = '''
def main():
    greeting = "Hello, Python!"
    message = 'Single quote string'
    multiline = """
This is a
multiline string
in Python
"""
    
    print(greeting)
    print(message)
    print(multiline)
    
if __name__ == "__main__":
    main()
    '''
    
    # 4. JavaScript文件
    test_js_content = '''
function showMenu() {
    console.log("Start Game");
    console.log("Exit Game");
    console.log("Settings");
}
    '''
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 保存测试文件
        test_files = [
            ("TestClass.java", test_java_content),
            ("TestClass.kt", test_kotlin_content),
            ("test.py", test_python_content),
            ("app.js", test_js_content)
        ]
        
        source_files = []
        for filename, content in test_files:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            source_files.append(file_path)
        
        print(f"\n[INFO] 创建了 {len(source_files)} 个测试源文件:")
        for file_path in source_files:
            print(f"  - {os.path.basename(file_path)}")
        
        # 测试单个文件字符串提取
        for file_path in source_files:
            print(f"\n[TEST] 测试文件: {os.path.basename(file_path)}")
            strings = extract_strings_from_file(file_path)
            print(f"  ✓ 提取到 {len(strings)} 个字符串")
            for i, string in enumerate(strings):
                print(f"    {i+1}. '{string['original']}' (行号: {string['meta']['line']})")
        
        # 测试目录提取
        print(f"\n[TEST] 测试从目录提取AST映射")
        ast_mappings = list(extract_ast_mappings(temp_dir))
        print(f"  ✓ 从目录提取到 {len(ast_mappings)} 个AST映射")
        
        # 测试生成初步YAML映射
        yaml_mappings = generate_initial_yaml_mappings(ast_mappings)
        print(f"  ✓ 生成了 {len(yaml_mappings)} 个YAML映射")
        for i, mapping in enumerate(yaml_mappings[:5]):
            print(f"    {i+1}. '{mapping['original']}' -> '{mapping['translated']}' (状态: {mapping['status']})")
        
        if len(yaml_mappings) > 5:
            print(f"    ... 以及 {len(yaml_mappings) - 5} 个更多映射")
        
        print("\n" + "=" * 60)
        print("          字符串提取测试完成")
        print("=" * 60)

if __name__ == "__main__":
    test_string_extraction()
