#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rules子模块 - processor.py测试
"""

import os
import tempfile
import pytest

from src.extend_mode.rules.processor import process_unmapped_content

class TestProcessor:
    """
    测试未映射内容处理功能
    """
    
    def test_process_unmapped_content_no_rule_file(self):
        """
        测试没有提供规则文件的情况
        """
        result = process_unmapped_content(
            rule_file="/invalid/path.yaml"
        )
        assert result["status"] == "error"
        assert "未从文件" in result["message"]
    
    def test_process_unmapped_content_no_action(self):
        """
        测试没有指定任何操作的情况
        """
        # 创建临时YAML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("- id: test_1\n  original: test string\n  translated: \n  status: unmapped\n")
            temp_file = f.name
        
        result = process_unmapped_content(
            rule_file=temp_file
        )
        
        assert result["status"] == "error"
        assert "必须指定至少一个操作" in result["message"]
        
        # 清理临时文件
        os.unlink(temp_file)
    
    def test_process_unmapped_content_list(self):
        """
        测试列出未映射内容的功能
        """
        # 创建临时YAML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("- id: test_1\n  original: test string\n  translated: \n  status: unmapped\n")
            temp_file = f.name
        
        result = process_unmapped_content(
            rule_file=temp_file,
            list_unmapped=True
        )
        
        assert result["status"] == "success"
        assert "未映射内容处理完成" in result["message"]
        
        # 清理临时文件
        os.unlink(temp_file)
    
    def test_process_unmapped_content_report(self):
        """
        测试生成未映射内容报告的功能
        """
        # 创建临时YAML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("- id: test_1\n  original: test string\n  translated: \n  status: unmapped\n")
            temp_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            report_file = f.name
        
        result = process_unmapped_content(
            rule_file=temp_file,
            report_file=report_file
        )
        
        assert result["status"] == "success"
        assert "未映射内容处理完成" in result["message"]
        assert os.path.exists(report_file)
        
        # 清理临时文件
        os.unlink(temp_file)
        os.unlink(report_file)
