#!/usr/bin/env python3
"""
测试 _should_filter_string 函数的功能
"""

import sys
import os

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 计算Localization_Tool的根目录
localization_tool_root = os.path.join(os.path.dirname(current_file_path), 'Localization_Tool')
# 添加Localization_Tool的根目录到Python搜索路径
sys.path.insert(0, localization_tool_root)

# 导入_should_filter_string函数
from src.common.tree_sitter_utils import _should_filter_string

def test_filter_function():
    """
    测试 _should_filter_string 函数的各种情况
    """
    # 测试用例：(输入字符串, 预期结果)
    test_cases = [
        # 空字符串测试
        ("", True),
        # 短字符串测试
        ("a", True),
        ("%", True),
        ("+", False),
        # 标识符测试
        ("test", True),
        ("$test", True),
        ("TEST_123", True),
        # 路径测试
        ("path/to/file.txt", True),
        ("C:\\Windows\\System32", True),
        ("file.json", True),
        ("config.yaml", True),
        # 格式字符串测试
        ("%s", True),
        ("%", True),
        (" sec", True),
        ("Level: ", True),
        ("placeholder_1", True),
        ("seconds", True),
        # UI标识符测试
        ("icon_button", True),
        ("UI_Element", True),
        ("ui_text", True),
        # 配置项测试
        ("cr_effect", True),
        ("noDeployCRPercent", True),
        ("deployCR", True),
        ("CR", True),
        ("dp", True),
        ("deploy_points", True),
        # 调试字符串测试
        ("test", True),
        ("debug", True),
        ("DEBUG", True),
        ("wefwefwefwefe", True),
        # 数值测试
        ("123", True),
        ("123.45", True),
        ("0", True),
        # 特殊字符测试
        ("!@#$%^&*()", True),
        ("_", True),
        ("-", True),
        # 应该保留的字符串测试
        ("这是一个测试字符串", False),
        ("This is a test string", False),
        ("Hello, World!", False),
        ("测试文本", False),
        ("Localization Tool", False),
    ]
    
    # 执行测试
    passed = 0
    failed = 0
    
    print("开始测试 _should_filter_string 函数...")
    print("=" * 60)
    
    for i, (test_input, expected) in enumerate(test_cases):
        result = _should_filter_string(test_input)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
            print(f"{i+1:3d}. {status} | 输入: '{test_input}' | 预期: {expected} | 实际: {result}")
    
    print("=" * 60)
    print(f"测试完成: 共 {len(test_cases)} 个测试用例")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    
    if failed == 0:
        print("🎉 所有测试用例通过！")
        return 0
    else:
        print("❌ 部分测试用例失败，请检查代码")
        return 1

if __name__ == "__main__":
    sys.exit(test_filter_function())
