#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地测试自监督学习功能

该脚本在Localization_Tool目录中运行，用于测试自监督学习功能。
"""

import os
import sys
import tempfile

# 从当前目录导入模块
from src.common.yaml_utils import (
    generate_translation_rules,
    generate_incremental_rules,
    update_translation_rules,
    load_yaml_mappings,
    save_yaml_mappings
)

def test_generate_translation_rules():
    """
    测试从双语数据生成翻译规则
    """
    print("=" * 60)
    print("          测试生成翻译规则")
    print("=" * 60)
    
    # 创建临时文件
    with tempfile.TemporaryDirectory() as temp_dir:
        # 示例英文映射数据
        english_data = [
            {
                "id": "main_menu.py:10",
                "original": "Start Game",
                "context": "UI/MainMenu",
                "placeholders": []
            },
            {
                "id": "main_menu.py:15",
                "original": "Exit Game",
                "context": "UI/MainMenu",
                "placeholders": []
            },
            {
                "id": "settings.py:20",
                "original": "Settings",
                "context": "UI/Settings",
                "placeholders": []
            }
        ]
        
        # 示例中文映射数据
        chinese_data = [
            {
                "id": "main_menu.py:10",
                "original": "开始游戏",
                "context": "UI/MainMenu",
                "placeholders": []
            },
            {
                "id": "main_menu.py:15",
                "original": "退出游戏",
                "context": "UI/MainMenu",
                "placeholders": []
            },
            {
                "id": "settings.py:20",
                "original": "设置",
                "context": "UI/Settings",
                "placeholders": []
            }
        ]
        
        output_file = os.path.join(temp_dir, "rules.yaml")
        
        # 生成翻译规则
        success = generate_translation_rules(english_data, chinese_data, output_file, mod_id="test_mod")
        
        if success:
            print("[OK] 生成翻译规则成功")
            
            # 验证生成的规则
            rules = load_yaml_mappings(output_file)
            print(f"[INFO] 生成的规则数量: {len(rules)}")
            
            for rule in rules:
                print(f"  - {rule['original']} -> {rule['translated']} (状态: {rule['status']})")
            
            return rules
        else:
            print("[ERROR] 生成翻译规则失败")
            return []

def test_generate_incremental_rules(existing_rules):
    """
    测试生成增量规则
    """
    print("\n" + "=" * 60)
    print("          测试生成增量规则")
    print("=" * 60)
    
    # 新的英文映射数据（包含新的条目）
    new_english_data = [
        {
            "id": "main_menu.py:10",
            "original": "Start Game",
            "context": "UI/MainMenu",
            "placeholders": []
        },
        {
            "id": "main_menu.py:15",
            "original": "Exit Game",
            "context": "UI/MainMenu",
            "placeholders": []
        },
        {
            "id": "settings.py:20",
            "original": "Settings",
            "context": "UI/Settings",
            "placeholders": []
        },
        {
            "id": "about.py:25",
            "original": "About",
            "context": "UI/About",
            "placeholders": []
        }
    ]
    
    # 生成增量规则
    incremental_rules = generate_incremental_rules(new_english_data, existing_rules)
    
    print(f"[INFO] 生成的增量规则数量: {len(incremental_rules)}")
    
    for rule in incremental_rules:
        status = rule['status']
        if status == 'translated':
            print(f"  ✓ {rule['original']} -> {rule['translated']} (状态: {status})")
        else:
            print(f"  ? {rule['original']} -> (未翻译) (状态: {status})")
    
    return incremental_rules

def test_update_translation_rules():
    """
    测试更新现有翻译规则
    """
    print("\n" + "=" * 60)
    print("          测试更新翻译规则")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建现有规则文件
        existing_rules_file = os.path.join(temp_dir, "existing_rules.yaml")
        new_english_file = os.path.join(temp_dir, "new_english.yaml")
        new_chinese_file = os.path.join(temp_dir, "new_chinese.yaml")
        output_file = os.path.join(temp_dir, "updated_rules.yaml")
        
        # 示例现有规则
        existing_rules = [
            {
                "id": "main_menu.py:10",
                "original": "Start Game",
                "translated": "开始游戏",
                "context": "UI/MainMenu",
                "status": "translated",
                "placeholders": []
            }
        ]
        
        # 示例新的英文映射
        new_english = [
            {
                "id": "main_menu.py:10",
                "original": "Start Game",
                "context": "UI/MainMenu",
                "placeholders": []
            },
            {
                "id": "main_menu.py:15",
                "original": "Exit Game",
                "context": "UI/MainMenu",
                "placeholders": []
            }
        ]
        
        # 示例新的中文映射
        new_chinese = [
            {
                "id": "main_menu.py:10",
                "original": "开始游戏",
                "context": "UI/MainMenu",
                "placeholders": []
            },
            {
                "id": "main_menu.py:15",
                "original": "退出游戏",
                "context": "UI/MainMenu",
                "placeholders": []
            }
        ]
        
        # 保存现有规则
        save_yaml_mappings(existing_rules, existing_rules_file)
        save_yaml_mappings(new_english, new_english_file)
        save_yaml_mappings(new_chinese, new_chinese_file)
        
        # 更新规则
        success = update_translation_rules(existing_rules_file, new_english_file, new_chinese_file, output_file, mod_id="test_mod")
        
        if success:
            print("[OK] 更新翻译规则成功")
            
            # 验证更新后的规则
            updated_rules = load_yaml_mappings(output_file)
            print(f"[INFO] 更新后的规则数量: {len(updated_rules)}")
            
            for rule in updated_rules:
                print(f"  - {rule['original']} -> {rule['translated']} (状态: {rule['status']})")
            
            return updated_rules
        else:
            print("[ERROR] 更新翻译规则失败")
            return []

def main():
    """
    主测试函数
    """
    print("=" * 60)
    print("      本地化工具自监督学习功能测试")
    print("=" * 60)
    
    # 测试1: 生成翻译规则
    rules = test_generate_translation_rules()
    
    if rules:
        # 测试2: 生成增量规则
        test_generate_incremental_rules(rules)
    
    # 测试3: 更新现有规则
    test_update_translation_rules()
    
    print("\n" + "=" * 60)
    print("      所有测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
