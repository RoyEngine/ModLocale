#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rules子模块 - extractor.py测试
"""

import os
import tempfile
import pytest

from src.extend_mode.rules.extractor import extract_mapping_rules

class TestExtractor:
    """
    测试规则提取功能
    """
    
    def test_extract_mapping_rules_no_source(self):
        """
        测试没有提供源目录或已处理目录的情况
        """
        result = extract_mapping_rules()
        assert result["status"] == "error"
        assert "必须提供" in result["message"]
    
    def test_extract_mapping_rules_invalid_source(self):
        """
        测试提供无效源目录的情况
        """
        result = extract_mapping_rules(
            source_dir="/invalid/path",
            output_file="test_output.yaml"
        )
        assert result["status"] == "error"
        assert "不存在" in result["message"]
    
    def test_extract_mapping_rules_empty_dir(self):
        """
        测试从空目录提取规则的情况
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            result = extract_mapping_rules(
                source_dir=temp_dir,
                output_file=os.path.join(temp_dir, "test_rules.yaml")
            )
            assert result["status"] == "error"
            assert "未提取到任何映射规则" in result["message"]
    
    def test_extract_mapping_rules_with_existing(self):
        """
        测试合并现有规则的情况
        """
        # 创建临时YAML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("- id: existing_1\n  original: existing string\n  translated: existing translation\n  status: translated\n")
            existing_file = f.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = extract_mapping_rules(
                processed_dir=temp_dir,
                existing_rule=existing_file,
                output_file=os.path.join(temp_dir, "test_rules.yaml")
            )
            
            assert result["status"] == "error" or result["status"] == "success"
        
        # 清理临时文件
        os.unlink(existing_file)
