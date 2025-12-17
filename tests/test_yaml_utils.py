#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yaml_utils模块单元测试
"""

import os
import sys
import tempfile
import unittest
from typing import List, Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.yaml_utils import (
    load_yaml_mappings,
    save_yaml_mappings,
    generate_translation_rules,
    update_translation_rules,
    generate_translation_report,
    apply_yaml_mapping,
    RuleConflictDetector
)

class TestYAMLUtils(unittest.TestCase):
    """测试yaml_utils模块的功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试数据
        self.english_mappings = [
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
        
        self.chinese_mappings = [
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
        
        # 保存测试数据到文件
        self.english_file = os.path.join(self.temp_dir, "english_mappings.yaml")
        self.chinese_file = os.path.join(self.temp_dir, "chinese_mappings.yaml")
        
        save_yaml_mappings(self.english_mappings, self.english_file, version_control=False)
        save_yaml_mappings(self.chinese_mappings, self.chinese_file, version_control=False)
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_yaml_mappings(self):
        """测试加载YAML映射文件"""
        mappings = load_yaml_mappings(self.english_file)
        self.assertEqual(len(mappings), 2)
        self.assertEqual(mappings[0]["original"], "Start Game")
    
    def test_save_yaml_mappings(self):
        """测试保存YAML映射文件"""
        output_file = os.path.join(self.temp_dir, "test_output.yaml")
        success = save_yaml_mappings(self.english_mappings, output_file, version_control=False)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_file))
    
    def test_generate_translation_rules(self):
        """测试生成翻译规则"""
        output_file = os.path.join(self.temp_dir, "rules.yaml")
        success = generate_translation_rules(
            self.english_mappings, 
            self.chinese_mappings, 
            output_file
        )
        self.assertTrue(success)
        
        # 验证生成的规则
        rules = load_yaml_mappings(output_file)
        self.assertEqual(len(rules), 2)
        self.assertEqual(rules[0]["original"], "Start Game")
        self.assertEqual(rules[0]["translated"], "开始游戏")
    
    def test_update_translation_rules(self):
        """测试更新翻译规则"""
        # 先生成初始规则
        initial_rules = os.path.join(self.temp_dir, "initial_rules.yaml")
        generate_translation_rules(
            self.english_mappings, 
            self.chinese_mappings, 
            initial_rules
        )
        
        # 创建新的测试数据，包含一个新条目
        new_english = self.english_mappings.copy()
        new_english.append({
            "id": "settings.py:20",
            "original": "Settings",
            "context": "UI/Settings",
            "placeholders": []
        })
        
        new_chinese = self.chinese_mappings.copy()
        new_chinese.append({
            "id": "settings.py:20",
            "original": "设置",
            "context": "UI/Settings",
            "placeholders": []
        })
        
        # 保存新数据
        new_english_file = os.path.join(self.temp_dir, "new_english.yaml")
        new_chinese_file = os.path.join(self.temp_dir, "new_chinese.yaml")
        save_yaml_mappings(new_english, new_english_file, version_control=False)
        save_yaml_mappings(new_chinese, new_chinese_file, version_control=False)
        
        # 更新规则
        updated_rules = os.path.join(self.temp_dir, "updated_rules.yaml")
        success = update_translation_rules(
            initial_rules,
            new_english_file,
            new_chinese_file,
            updated_rules
        )
        self.assertTrue(success)
        
        # 验证更新后的规则
        rules = load_yaml_mappings(updated_rules)
        self.assertEqual(len(rules), 3)  # 应该有3条规则
        
    def test_conflict_detection(self):
        """测试冲突检测功能"""
        # 创建有冲突的映射数据
        conflicting_mappings = [
            {
                "id": "main_menu.py:10",
                "original": "Start Game",
                "translated": "开始游戏",
                "status": "translated"
            },
            {
                "id": "main_menu.py:10",  # 重复ID
                "original": "Start Game",
                "translated": "启动游戏",
                "status": "translated"
            },
            {
                "id": "main_menu.py:20",
                "original": "Exit Game",
                "translated": "退出游戏",
                "status": "translated"
            },
            {
                "id": "main_menu.py:25",
                "original": "Exit Game",  # 重复原始字符串
                "translated": "退出",
                "status": "translated"
            }
        ]
        
        # 检测冲突
        detector = RuleConflictDetector()
        conflicts = detector.detect_all_conflicts(conflicting_mappings)
        
        # 验证冲突检测结果
        self.assertEqual(conflicts["total_conflicts"], 2)  # 应该有2个冲突
        self.assertEqual(len(conflicts["duplicate_ids"]), 1)  # 1个重复ID冲突
        self.assertEqual(len(conflicts["duplicate_originals"]), 1)  # 1个重复原始字符串冲突
    
    def test_conflict_resolution(self):
        """测试冲突解决功能"""
        # 创建有冲突的映射数据
        conflicting_mappings = [
            {
                "id": "main_menu.py:10",
                "original": "Start Game",
                "translated": "开始游戏",
                "status": "translated"
            },
            {
                "id": "main_menu.py:10",  # 重复ID
                "original": "Start Game",
                "translated": "启动游戏",
                "status": "translated"
            }
        ]
        
        # 检测冲突
        detector = RuleConflictDetector()
        conflicts = detector.detect_all_conflicts(conflicting_mappings)
        
        # 解决冲突
        resolved = detector.resolve_conflicts(conflicting_mappings, conflicts, "latest")
        
        # 验证冲突解决结果
        self.assertEqual(len(resolved), 1)  # 应该只有1条规则
        self.assertEqual(resolved[0]["translated"], "启动游戏")  # 使用最新的翻译
    
    def test_generate_translation_report(self):
        """测试生成翻译报告"""
        # 生成测试规则
        rules = [
            {
                "id": "main_menu.py:10",
                "original": "Start Game",
                "translated": "开始游戏",
                "status": "translated"
            },
            {
                "id": "main_menu.py:15",
                "original": "Exit Game",
                "translated": "退出游戏",
                "status": "translated"
            },
            {
                "id": "settings.py:20",
                "original": "Settings",
                "translated": "",
                "status": "untranslated"
            }
        ]
        
        # 生成报告
        report_file = os.path.join(self.temp_dir, "report.md")
        report = generate_translation_report(rules, report_file, "markdown")
        
        # 验证报告生成
        self.assertIsInstance(report, dict)
        self.assertEqual(report["total_rules"], 3)
        self.assertEqual(report["status_counts"]["translated"], 2)
        self.assertEqual(report["status_counts"]["untranslated"], 1)
        self.assertTrue(os.path.exists(report_file))
    
    def test_data_alignment(self):
        """测试数据对齐功能"""
        # 创建数量不一致的测试数据
        english_mappings = self.english_mappings.copy()
        english_mappings.append({
            "id": "settings.py:20",
            "original": "Settings",
            "context": "UI/Settings",
            "placeholders": []
        })
        
        # 中文数据只有2条，英文数据有3条
        output_file = os.path.join(self.temp_dir, "rules_aligned.yaml")
        success = generate_translation_rules(
            english_mappings, 
            self.chinese_mappings, 
            output_file
        )
        self.assertTrue(success)
        
        # 验证生成的规则数量应该是2条（取较小的数量）
        rules = load_yaml_mappings(output_file)
        self.assertEqual(len(rules), 2)
    
    def test_apply_yaml_mapping(self):
        """测试应用YAML映射到源代码文件"""
        # 创建测试Java文件
        test_file = os.path.join(self.temp_dir, "TestFile.java")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("""
public class TestFile {
    public void main() {
        System.out.println("Start Game");
        System.out.println("Exit Game");
    }
}
            """)
        
        # 创建测试规则
        test_rules = [
            {
                "original": "Start Game",
                "translated": "开始游戏",
                "status": "translated"
            },
            {
                "original": "Exit Game",
                "translated": "退出游戏",
                "status": "translated"
            }
        ]
        
        # 应用映射
        translated_content = apply_yaml_mapping(test_file, test_rules)
        
        # 验证翻译结果
        self.assertIn("开始游戏", translated_content)
        self.assertIn("退出游戏", translated_content)
        self.assertNotIn("Start Game", translated_content)
        self.assertNotIn("Exit Game", translated_content)

if __name__ == "__main__":
    unittest.main()
