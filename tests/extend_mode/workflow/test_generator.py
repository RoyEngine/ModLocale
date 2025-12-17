#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workflow子模块 - generator.py测试
"""

import os
import tempfile
import pytest

from src.extend_mode.workflow.generator import generate_translation_rules_func

class TestGenerator:
    """
    测试规则生成功能
    """
    
    def test_generate_translation_rules_no_files(self):
        """
        测试没有提供文件的情况
        """
        result = generate_translation_rules_func(
            english_file="/invalid/path.yaml",
            chinese_file="/invalid/path.yaml",
            output_file="test_output.yaml"
        )
        assert result["status"] == "error"
    
    def test_generate_translation_rules_empty_files(self):
        """
        测试提供空文件的情况
        """
        # 创建临时YAML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f2:
            # 写入空内容
            f1.write("")
            f2.write("")
            en_file = f1.name
            zh_file = f2.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_translation_rules_func(
                english_file=en_file,
                chinese_file=zh_file,
                output_file=os.path.join(temp_dir, "test_rules.yaml")
            )
            assert result["status"] == "error"
        
        # 清理临时文件
        os.unlink(en_file)
        os.unlink(zh_file)
    
    def test_generate_translation_rules_valid(self):
        """
        测试从有效文件生成规则的功能
        """
        # 创建临时YAML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f2:
            f1.write("- id: test_1\n  original: test string\n")
            f2.write("- id: test_1\n  original: 测试字符串\n")
            en_file = f1.name
            zh_file = f2.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "test_rules.yaml")
            result = generate_translation_rules_func(
                english_file=en_file,
                chinese_file=zh_file,
                output_file=output_file
            )
            
            assert result["status"] == "success"
            assert "翻译规则生成完成" in result["message"]
            assert os.path.exists(output_file)
        
        # 清理临时文件
        os.unlink(en_file)
        os.unlink(zh_file)
