#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tree-sitter 修复验证测试脚本
用于验证修复后的 tree_sitter_utils.py 是否可以正常工作
"""

import os
import sys

# 添加 Localization_Tool/src 目录到 Python 搜索路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Localization_Tool", "src"))

print("=" * 60)
print("Tree-sitter 修复验证测试")
print("=" * 60)
print("开始测试 tree_sitter_utils.py 修复效果...")
print("=" * 60)

# 1. 测试模块导入
try:
    print("\n1. 测试 tree_sitter_utils 模块导入...")
    from common.tree_sitter_utils import (
        TREE_SITTER_AVAILABLE,
        initialize_languages,
        get_parser,
        extract_strings_from_file
    )
    print("✅ 模块导入成功")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. 测试 Tree-sitter 初始化
try:
    print("\n2. 测试 Tree-sitter 初始化...")
    initialize_languages()
    print("✅ Tree-sitter 初始化成功")
except Exception as e:
    print(f"❌ Tree-sitter 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 创建一个简单的测试 Java 文件用于测试字符串提取
test_java_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.java")
test_java_content = '''
public class Test {
    public static void main(String[] args) {
        String message = "Hello, World!";
        String name = "Test";
        System.out.println(message);
        System.out.println("Welcome to " + name);
    }
}
'''

with open(test_java_file, "w") as f:
    f.write(test_java_content)

print(f"\n3. 创建测试 Java 文件: {test_java_file}")
print("测试文件内容:")
print(test_java_content)

# 4. 测试 get_parser 函数
try:
    print("\n4. 测试 get_parser 函数...")
    parser = get_parser(test_java_file)
    if parser:
        print("✅ get_parser 函数成功返回解析器")
        print(f"解析器类型: {type(parser)}")
    else:
        print("❌ get_parser 函数返回 None")
except Exception as e:
    print(f"❌ get_parser 函数失败: {e}")
    import traceback
    traceback.print_exc()

# 5. 测试 extract_strings_from_file 函数
try:
    print("\n5. 测试 extract_strings_from_file 函数...")
    strings = extract_strings_from_file(test_java_file)
    if strings:
        print(f"✅ extract_strings_from_file 函数成功提取 {len(strings)} 个字符串")
        for i, string in enumerate(strings):
            print(f"   字符串 {i+1}: {string['original']}")
            print(f"   位置: {string['meta']['file']}:{string['meta']['line']}")
    else:
        print("❌ extract_strings_from_file 函数没有提取到字符串")
except Exception as e:
    print(f"❌ extract_strings_from_file 函数失败: {e}")
    import traceback
    traceback.print_exc()

# 6. 清理测试文件
os.remove(test_java_file)
print(f"\n6. 清理测试文件: {test_java_file}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print("✅ Tree-sitter 修复验证测试完成")
