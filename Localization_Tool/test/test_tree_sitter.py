#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tree-sitter 初始化测试脚本
用于验证 tree_sitter_utils.py 是否可以正确使用已安装的 Tree-sitter 相关包
"""

import os
import sys

# 直接将 Localization_Tool/src 目录添加到 Python 搜索路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Localization_Tool", "src"))

# 直接导入 tree_sitter_utils 模块
from common.tree_sitter_utils import (
    initialize_languages,
    TREE_SITTER_AVAILABLE,
    JAVA_LANGUAGE,
    KOTLIN_LANGUAGE
)


def test_tree_sitter_initialization():
    """测试 Tree-sitter 初始化"""
    print("=" * 60)
    print("Tree-sitter 初始化测试")
    print("=" * 60)
    
    # 打印初始状态
    print(f"初始 Tree-sitter 可用状态: {TREE_SITTER_AVAILABLE}")
    print(f"初始 Java 语言对象: {JAVA_LANGUAGE}")
    print(f"初始 Kotlin 语言对象: {KOTLIN_LANGUAGE}")
    
    print("\n" + "=" * 60)
    print("开始初始化 Tree-sitter...")
    print("=" * 60)
    
    # 调用初始化函数
    initialize_languages()
    
    print("\n" + "=" * 60)
    print("初始化结果:")
    print("=" * 60)
    
    # 打印初始化后的状态
    print(f"Tree-sitter 可用状态: {TREE_SITTER_AVAILABLE}")
    print(f"Java 语言对象: {JAVA_LANGUAGE}")
    print(f"Kotlin 语言对象: {KOTLIN_LANGUAGE}")
    
    # 检查是否成功初始化
    if TREE_SITTER_AVAILABLE:
        print("\n✅ Tree-sitter 库导入成功")
        
        if JAVA_LANGUAGE:
            print("✅ Java 语言解析器初始化成功")
        else:
            print("❌ Java 语言解析器初始化失败")
            
        if KOTLIN_LANGUAGE:
            print("✅ Kotlin 语言解析器初始化成功")
        else:
            print("❌ Kotlin 语言解析器初始化失败")
            
        if JAVA_LANGUAGE or KOTLIN_LANGUAGE:
            print("\n🎉 Tree-sitter 初始化成功，可以正常使用")
            return True
        else:
            print("\n❌ Tree-sitter 初始化失败，无法使用")
            return False
    else:
        print("\n❌ Tree-sitter 库导入失败，将使用备用方案")
        return False


if __name__ == "__main__":
    test_tree_sitter_initialization()
