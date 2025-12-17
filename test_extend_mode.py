#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试extend_mode模块的功能
"""

import os
import sys
import tempfile
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_rules_extractor():
    """
    测试rules子模块的extractor功能
    """
    print("\n=== 测试规则提取功能 ===")
    from src.extend_mode.rules.extractor import extract_mapping_rules
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        result = extract_mapping_rules(
            source_dir=temp_dir,
            output_file=os.path.join(temp_dir, "test_rules.yaml")
        )
        print(f"测试结果: {result}")
        print("✓ 规则提取功能测试完成")

def test_rules_processor():
    """
    测试rules子模块的processor功能
    """
    print("\n=== 测试未映射内容处理功能 ===")
    from src.extend_mode.rules.processor import process_unmapped_content
    
    # 创建临时YAML文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("- id: test_1\n  original: test string\n  translated: \n  status: unmapped\n")
        temp_file = f.name
    
    try:
        result = process_unmapped_content(
            rule_file=temp_file,
            list_unmapped=True
        )
        print(f"测试结果: {result}")
        print("✓ 未映射内容处理功能测试完成")
    finally:
        os.unlink(temp_file)

def test_rules_conflict():
    """
    测试rules子模块的conflict功能
    """
    print("\n=== 测试冲突检测功能 ===")
    from src.extend_mode.rules.conflict import detect_and_resolve_conflicts
    
    # 创建临时YAML文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("- id: test_1\n  original: test string\n  translated: test translation\n  status: translated\n")
        temp_file = f.name
    
    try:
        result = detect_and_resolve_conflicts(
            rule_file=temp_file
        )
        print(f"测试结果: {result}")
        print("✓ 冲突检测功能测试完成")
    finally:
        os.unlink(temp_file)

def test_workflow_generator():
    """
    测试workflow子模块的generator功能
    """
    print("\n=== 测试规则生成功能 ===")
    from src.extend_mode.workflow.generator import generate_translation_rules_func
    
    # 创建临时YAML文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f1, \
         tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f2:
        f1.write("- id: test_1\n  original: test string\n")
        f2.write("- id: test_1\n  original: 测试字符串\n")
        en_file = f1.name
        zh_file = f2.name
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = os.path.join(temp_dir, "test_rules.yaml")
        try:
            result = generate_translation_rules_func(
                english_file=en_file,
                chinese_file=zh_file,
                output_file=output_file
            )
            print(f"测试结果: {result}")
            print("✓ 规则生成功能测试完成")
        finally:
            os.unlink(en_file)
            os.unlink(zh_file)

def test_workflow_updater():
    """
    测试workflow子模块的updater功能
    """
    print("\n=== 测试规则更新功能 ===")
    from src.extend_mode.workflow.updater import update_translation_rules_func
    
    # 创建临时YAML文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f1, \
         tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f2, \
         tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f3:
        f1.write("- id: test_1\n  original: test string\n  translated: old translation\n")
        f2.write("- id: test_1\n  original: test string\n")
        f3.write("- id: test_1\n  original: 新测试字符串\n")
        existing_file = f1.name
        en_file = f2.name
        zh_file = f3.name
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = os.path.join(temp_dir, "test_rules.yaml")
        try:
            result = update_translation_rules_func(
                existing_rules_file=existing_file,
                new_english_file=en_file,
                new_chinese_file=zh_file,
                output_file=output_file
            )
            print(f"测试结果: {result}")
            print("✓ 规则更新功能测试完成")
        finally:
            os.unlink(existing_file)
            os.unlink(en_file)
            os.unlink(zh_file)

def test_workflow_runner():
    """
    测试workflow子模块的runner功能
    """
    print("\n=== 测试完整工作流功能 ===")
    from src.extend_mode.workflow.runner import run_complete_workflow
    
    # 创建临时YAML文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f1, \
         tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f2:
        f1.write("- id: test_1\n  original: test string\n")
        f2.write("- id: test_1\n  original: 测试字符串\n")
        en_file = f1.name
        zh_file = f2.name
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            result = run_complete_workflow(
                english_file=en_file,
                chinese_file=zh_file,
                source_dir=temp_dir,
                output_dir=os.path.join(temp_dir, "output"),
                use_cache=False
            )
            print(f"测试结果: {result}")
            print("✓ 完整工作流功能测试完成")
        finally:
            os.unlink(en_file)
            os.unlink(zh_file)

def test_core_function():
    """
    测试core模块的核心功能
    """
    print("\n=== 测试核心映射功能 ===")
    from src.extend_mode.core import run_extend_sub_flow
    
    result = run_extend_sub_flow(
        sub_flow="已有中文src文件夹映射流程"
    )
    print(f"测试结果: {result}")
    print("✓ 核心映射功能测试完成")

def main():
    """
    运行所有测试
    """
    print("开始测试extend_mode模块...")
    start_time = datetime.now()
    
    test_rules_extractor()
    test_rules_processor()
    test_rules_conflict()
    test_workflow_generator()
    test_workflow_updater()
    test_workflow_runner()
    test_core_function()
    
    end_time = datetime.now()
    print(f"\n测试完成! 总耗时: {end_time - start_time}")
    print("✓ 所有功能测试通过")

if __name__ == "__main__":
    main()
