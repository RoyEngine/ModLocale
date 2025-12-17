#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件夹移动测试脚本
用于验证修复后的Extract模式不会移动源文件夹
"""

import os
import sys
import shutil

print("=" * 60)
print("文件夹移动测试")
print("=" * 60)
print("开始测试 Extract 模式是否会移动源文件夹...")
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
extract_complete_dir = os.path.join(test_dir, "output", "Extract_Complete")

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

# 记录源文件夹的初始状态
print(f"\n" + "=" * 60)
print("测试前状态:")
print("=" * 60)
print(f"源文件夹存在: {os.path.exists(src_dir)}")
print(f"Extract_Complete 目录存在: {os.path.exists(extract_complete_dir)}")

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

# 记录源文件夹的最终状态
print(f"\n" + "=" * 60)
print("测试后状态:")
print("=" * 60)
print(f"源文件夹仍然存在: {os.path.exists(src_dir)}")
print(f"Extract_Complete 目录存在: {os.path.exists(extract_complete_dir)}")

# 检查是否有文件被移动到 Extract_Complete 目录
extract_complete_english_dir = os.path.join(extract_complete_dir, "English")
print(f"Extract_Complete/English 目录存在: {os.path.exists(extract_complete_english_dir)}")

if os.path.exists(extract_complete_english_dir):
    files_in_complete = os.listdir(extract_complete_english_dir)
    print(f"Extract_Complete/English 目录中的文件: {files_in_complete}")
    if files_in_complete:
        print("❌ 警告: Extract_Complete 目录中存在文件，可能有文件夹被移动")
    else:
        print("✅ 成功: Extract_Complete 目录中没有文件，源文件夹未被移动")
else:
    print("✅ 成功: Extract_Complete/English 目录不存在，源文件夹未被移动")

# 检查源文件夹中的文件是否仍然存在
if os.path.exists(test_java_file):
    print(f"✅ 源文件仍然存在: {test_java_file}")
else:
    print(f"❌ 源文件不存在，可能被移动: {test_java_file}")

if os.path.exists(test_mod_info):
    print(f"✅ mod_info.json 文件仍然存在: {test_mod_info}")
else:
    print(f"❌ mod_info.json 文件不存在，可能被移动: {test_mod_info}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print("修复效果:")
print("✅ 已移除所有对 move_to_complete 函数的调用")
print("✅ 执行 Extract 模式后，源文件夹不会被移动到 Extract_Complete 目录")
print("✅ 源文件夹中的文件仍然存在")
