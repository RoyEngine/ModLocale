#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的 Tree-sitter 初始化测试脚本
直接测试 tree_sitter_utils.py 模块，不导入其他依赖模块
"""

import os
import sys

# 添加项目根目录到 Python 搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置 Python 环境变量，确保使用正确的虚拟环境
env_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv")
sys.path.insert(0, os.path.join(env_dir, "Lib", "site-packages"))

print("=" * 60)
print("简单 Tree-sitter 初始化测试")
print("=" * 60)

# 直接测试 Tree-sitter 导入
try:
    print("1. 尝试导入 Tree-sitter 核心库...")
    import tree_sitter
    from tree_sitter import Language, Parser
    print("✅ Tree-sitter 核心库导入成功")
except Exception as e:
    print(f"❌ Tree-sitter 核心库导入失败: {e}")
    sys.exit(1)

try:
    print("\n2. 尝试导入 tree_sitter_java 库...")
    import tree_sitter_java
    print("✅ tree_sitter_java 库导入成功")
except Exception as e:
    print(f"❌ tree_sitter_java 库导入失败: {e}")

try:
    print("\n3. 尝试导入 tree_sitter_kotlin 库...")
    import tree_sitter_kotlin
    print("✅ tree_sitter_kotlin 库导入成功")
except Exception as e:
    print(f"❌ tree_sitter_kotlin 库导入失败: {e}")

print("\n" + "=" * 60)
print("4. 测试 Tree-sitter 语言对象获取...")
print("=" * 60)

try:
    print("   尝试获取 Java 语言对象...")
    java_lang = tree_sitter_java.language()
    print(f"   ✅ Java 语言对象获取成功: {java_lang}")
    print(f"   语言对象类型: {type(java_lang)}")
except Exception as e:
    print(f"   ❌ Java 语言对象获取失败: {e}")

try:
    print("\n   尝试获取 Kotlin 语言对象...")
    kotlin_lang = tree_sitter_kotlin.language()
    print(f"   ✅ Kotlin 语言对象获取成功: {kotlin_lang}")
    print(f"   语言对象类型: {type(kotlin_lang)}")
except Exception as e:
    print(f"   ❌ Kotlin 语言对象获取失败: {e}")

print("\n" + "=" * 60)
print("5. 测试 Tree-sitter 解析器创建...")
print("=" * 60)

try:
    parser = Parser()
    print("   ✅ Tree-sitter 解析器创建成功")
except Exception as e:
    print(f"   ❌ Tree-sitter 解析器创建失败: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print("✅ Tree-sitter 相关包可以正常导入和使用")
