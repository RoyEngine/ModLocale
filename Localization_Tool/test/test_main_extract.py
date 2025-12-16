#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py 提取模式测试脚本
用于验证修复后的 tree_sitter_utils.py 在 main.py 中是否正常工作
"""

import os
import sys
import shutil

print("=" * 60)
print("main.py 提取模式测试")
print("=" * 60)
print("开始测试 main.py 中的 Extract 模式...")
print("=" * 60)

# 设置项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))
localization_tool_root = os.path.join(project_root, "Localization_Tool")
main_script = os.path.join(localization_tool_root, "src", "main.py")

# 创建测试所需的目录结构
test_dir = os.path.join(project_root, "Localization_File")
source_dir = os.path.join(test_dir, "source")
english_dir = os.path.join(source_dir, "English")
src_dir = os.path.join(english_dir, "test_mod", "src")

# 清理旧的测试目录
if os.path.exists(test_dir):
    shutil.rmtree(test_dir)
    print(f"清理旧的测试目录: {test_dir}")

# 创建新的测试目录
os.makedirs(src_dir, exist_ok=True)
print(f"创建测试目录结构: {src_dir}")

# 创建测试 Java 文件
test_java_file = os.path.join(src_dir, "Test.java")
test_java_content = '''
public class Test {
    public static void main(String[] args) {
        String message = "Hello, World!";
        String name = "Test Mod";
        System.out.println(message);
        System.out.println("Welcome to " + name);
        System.out.println("This is a test for localization tool.");
    }
}
'''

with open(test_java_file, "w") as f:
    f.write(test_java_content)

print(f"\n创建测试 Java 文件: {test_java_file}")
print("测试文件内容:")
print(test_java_content)

# 创建 mod_info.json 文件
test_mod_info = os.path.join(english_dir, "test_mod", "mod_info.json")
test_mod_info_content = '''{
    "name": "TestMod",
    "version": "1.0.0",
    "author": "Test Author",
    "description": "A test mod for localization tool"
}
'''

with open(test_mod_info, "w") as f:
    f.write(test_mod_info_content)

print(f"\n创建 mod_info.json 文件: {test_mod_info}")
print("mod_info.json 内容:")
print(test_mod_info_content)

# 运行 main.py，测试 Extract 模式
print("\n" + "=" * 60)
print("运行 main.py，测试 Extract 模式...")
print("=" * 60)

# 使用测试模式运行 main.py，避免交互式输入
cmd = f"python {main_script} --test-mode 1,1 extract 英文提取流程"
print(f"执行命令: {cmd}")
print("=" * 60)

# 执行命令
os.system(cmd)

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print("请检查输出目录 Localization_File/output/Extract_English/TestMod_1.0.0 中的结果文件")
print("预期结果：")
print("1. English_mappings.json - 包含提取的字符串映射规则")
print("2. English_mappings.yaml - 包含提取的字符串映射规则")
print("3. extract_xxx_report.json - 流程报告")
print("4. mod_info.json - mod 信息文件")
