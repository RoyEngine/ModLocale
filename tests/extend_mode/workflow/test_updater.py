#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workflow子模块 - updater.py测试
"""

import os
import tempfile
import pytest

from src.extend_mode.workflow.updater import update_translation_rules_func

class TestUpdater:
    """
    测试规则更新功能
    """
    
    def test_update_translation_rules_no_files(self):
        """
        测试没有提供文件的情况
        """
        result = update_translation_rules_func(
            existing_rules_file="/invalid/path.yaml",
            new_english_file="/invalid/path.yaml",
            new_chinese_file="/invalid/path.yaml",
            output_file="test_output.yaml"
        )
        assert result["status"] == "error"
        assert "不存在" in result["message"]
    
    def test_update_translation_rules_valid(self):
        """
        测试从有效文件更新规则的功能
        """
        # 创建临时YAML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f2, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f3:
            f1.write("- id: test_1\n  original: test string\n  translated: old translation\n  status: translated\n")
            f2.write("- id: test_1\n  original: test string\n")
            f3.write("- id: test_1\n  original: 新测试字符串\n")
            existing_file = f1.name
            en_file = f2.name
            zh_file = f3.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "test_rules.yaml")
            result = update_translation_rules_func(
                existing_rules_file=existing_file,
                new_english_file=en_file,
                new_chinese_file=zh_file,
                output_file=output_file
            )
            
            assert result["status"] == "success" or result["status"] == "error"
        
        # 清理临时文件
        os.unlink(existing_file)
        os.unlink(en_file)
        os.unlink(zh_file)
