#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extend_mode模块使用示例

该脚本展示了如何使用extend_mode模块的主要功能，包括：
1. 规则提取
2. 未映射内容处理
3. 冲突检测和解决
4. 规则生成
5. 规则更新
6. 完整工作流执行
"""

import os
import sys
import tempfile
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入extend_mode模块
from src.extend_mode import (
    extract_mapping_rules,
    process_unmapped_content,
    detect_and_resolve_conflicts,
    generate_translation_rules,
    update_translation_rules,
    run_complete_workflow,
    run_extend_sub_flow
)

def create_sample_mapping_file(file_path: str, language: str = "English") -> None:
    """
    创建示例映射文件
    
    Args:
        file_path: 文件路径
        language: 语言类型
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        if language == "English":
            f.write("- id: test_1\n  original: Hello, world!\n")
            f.write("- id: test_2\n  original: This is a test.\n")
            f.write("- id: test_3\n  original: Welcome to ModLocale.\n")
        else:
            f.write("- id: test_1\n  original: 你好，世界！\n")
            f.write("- id: test_2\n  original: 这是一个测试。\n")
            f.write("- id: test_3\n  original: 欢迎使用ModLocale。\n")

def example_rule_extraction():
    """
    示例：规则提取
    """
    print("\n=== 示例1: 规则提取 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建示例源文件
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir, exist_ok=True)
        
        # 创建示例Java文件
        java_file = os.path.join(source_dir, "Test.java")
        with open(java_file, 'w', encoding='utf-8') as f:
            f.write('public class Test {\n')
            f.write('    public static void main(String[] args) {\n')
            f.write('        System.out.println("Hello, world!");\n')
            f.write('        System.out.println("This is a test.");\n')
            f.write('    }\n')
            f.write('}\n')
        
        # 提取映射规则
        result = extract_mapping_rules(
            source_dir=source_dir,
            output_file=os.path.join(temp_dir, "extracted_rules.yaml")
        )
        
        print(f"规则提取结果: {result}")
        print(f"输出文件: {os.path.join(temp_dir, 'extracted_rules.yaml')}")

def example_unmapped_processing():
    """
    示例：未映射内容处理
    """
    print("\n=== 示例2: 未映射内容处理 ===")
    
    # 创建示例规则文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("- id: test_1\n  original: test string 1\n  translated: \n  status: unmapped\n")
        f.write("- id: test_2\n  original: test string 2\n  translated: translated string 2\n  status: translated\n")
        f.write("- id: test_3\n  original: test string 3\n  translated: \n  status: unmapped\n")
        rule_file = f.name
    
    try:
        # 列出未映射内容
        result = process_unmapped_content(
            rule_file=rule_file,
            list_unmapped=True
        )
        
        print(f"未映射内容处理结果: {result}")
    finally:
        os.unlink(rule_file)

def example_conflict_detection():
    """
    示例：冲突检测和解决
    """
    print("\n=== 示例3: 冲突检测和解决 ===")
    
    # 创建示例规则文件（包含冲突）
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("- id: duplicate_id\n  original: test string\n  translated: translation 1\n  status: translated\n")
        f.write("- id: duplicate_id\n  original: test string\n  translated: translation 2\n  status: translated\n")
        rule_file = f.name
    
    try:
        # 检测冲突
        result = detect_and_resolve_conflicts(
            rule_file=rule_file
        )
        
        print(f"冲突检测结果: {result}")
    finally:
        os.unlink(rule_file)

def example_rule_generation():
    """
    示例：规则生成
    """
    print("\n=== 示例4: 规则生成 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建示例映射文件
        en_file = os.path.join(temp_dir, "english.yaml")
        zh_file = os.path.join(temp_dir, "chinese.yaml")
        
        create_sample_mapping_file(en_file, "English")
        create_sample_mapping_file(zh_file, "Chinese")
        
        # 生成翻译规则
        result = generate_translation_rules(
            english_file=en_file,
            chinese_file=zh_file,
            output_file=os.path.join(temp_dir, "generated_rules.yaml")
        )
        
        print(f"规则生成结果: {result}")

def example_rule_update():
    """
    示例：规则更新
    """
    print("\n=== 示例5: 规则更新 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建现有规则文件
        existing_file = os.path.join(temp_dir, "existing_rules.yaml")
        with open(existing_file, 'w', encoding='utf-8') as f:
            f.write("- id: test_1\n  original: Hello\n  translated: 旧翻译\n  status: translated\n")
        
        # 创建新的映射文件
        en_file = os.path.join(temp_dir, "new_english.yaml")
        zh_file = os.path.join(temp_dir, "new_chinese.yaml")
        
        create_sample_mapping_file(en_file, "English")
        create_sample_mapping_file(zh_file, "Chinese")
        
        # 更新翻译规则
        result = update_translation_rules(
            existing_rules_file=existing_file,
            new_english_file=en_file,
            new_chinese_file=zh_file,
            output_file=os.path.join(temp_dir, "updated_rules.yaml")
        )
        
        print(f"规则更新结果: {result}")

def example_complete_workflow():
    """
    示例：完整工作流执行
    """
    print("\n=== 示例6: 完整工作流执行 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建示例映射文件
        en_file = os.path.join(temp_dir, "english.yaml")
        zh_file = os.path.join(temp_dir, "chinese.yaml")
        
        create_sample_mapping_file(en_file, "English")
        create_sample_mapping_file(zh_file, "Chinese")
        
        # 创建示例源目录
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir, exist_ok=True)
        
        # 创建示例Java文件
        java_file = os.path.join(source_dir, "Test.java")
        with open(java_file, 'w', encoding='utf-8') as f:
            f.write('public class Test {\n')
            f.write('    public static void main(String[] args) {\n')
            f.write('        System.out.println("Hello, world!");\n')
            f.write('    }\n')
            f.write('}\n')
        
        # 执行完整工作流
        result = run_complete_workflow(
            english_file=en_file,
            chinese_file=zh_file,
            source_dir=source_dir,
            output_dir=os.path.join(temp_dir, "output"),
            use_cache=False
        )
        
        print(f"完整工作流结果: {result}")
        print(f"输出目录: {result['output_dir']}")
        print(f"规则文件: {result['rules_file']}")
        print(f"报告文件: {result['report_file']}")

def example_extend_flow():
    """
    示例：执行Extend子流程
    """
    print("\n=== 示例7: 执行Extend子流程 ===")
    
    # 执行映射流程
    result = run_extend_sub_flow(
        sub_flow="已有中文src文件夹映射流程"
    )
    
    print(f"映射流程结果: {result}")

def main():
    """
    运行所有示例
    """
    print("extend_mode模块使用示例")
    print("=" * 60)
    
    start_time = datetime.now()
    
    example_rule_extraction()
    example_unmapped_processing()
    example_conflict_detection()
    example_rule_generation()
    example_rule_update()
    example_complete_workflow()
    example_extend_flow()
    
    end_time = datetime.now()
    print(f"\n示例运行完成! 总耗时: {end_time - start_time}")
    print("=" * 60)

if __name__ == "__main__":
    main()
