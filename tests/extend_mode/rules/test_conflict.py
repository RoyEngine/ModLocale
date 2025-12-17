#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rules子模块 - conflict.py测试
"""

import os
import tempfile
import pytest

from src.extend_mode.rules.conflict import detect_and_resolve_conflicts

class TestConflict:
    """
    测试冲突检测和解决功能
    """
    
    def test_detect_and_resolve_conflicts_no_rule_file(self):
        """
        测试没有提供规则文件的情况
        """
        result = detect_and_resolve_conflicts(
            rule_file="/invalid/path.yaml"
        )
        assert result["status"] == "error"
        assert "未从文件" in result["message"]
    
    def test_detect_and_resolve_conflicts_no_conflict(self):
        """
        测试检测没有冲突的情况
        """
        # 创建临时YAML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("- id: test_1\n  original: test string\n  translated: test translation\n  status: translated\n")
            temp_file = f.name
        
        result = detect_and_resolve_conflicts(
            rule_file=temp_file
        )
        
        assert result["status"] == "success"
        assert "冲突检测完成" in result["message"]
        assert result["total_conflicts"] == 0
        
        # 清理临时文件
        os.unlink(temp_file)
    
    def test_detect_and_resolve_conflicts_with_report(self):
        """
        测试生成冲突报告的功能
        """
        # 创建临时YAML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("- id: test_1\n  original: test string\n  translated: test translation\n  status: translated\n")
            temp_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            report_file = f.name
        
        result = detect_and_resolve_conflicts(
            rule_file=temp_file,
            generate_report=True,
            report_file=report_file
        )
        
        assert result["status"] == "success"
        assert "冲突检测完成" in result["message"]
        assert os.path.exists(report_file)
        
        # 清理临时文件
        os.unlink(temp_file)
        os.unlink(report_file)
    
    def test_detect_and_resolve_conflicts_resolve(self):
        """
        测试解决冲突的功能
        """
        # 创建临时YAML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("- id: test_1\n  original: test string\n  translated: test translation\n  status: translated\n")
            temp_file = f.name
        
        result = detect_and_resolve_conflicts(
            rule_file=temp_file,
            resolve=True,
            resolve_strategy="latest"
        )
        
        assert result["status"] == "success"
        assert "冲突检测完成" in result["message"]
        
        # 清理临时文件
        os.unlink(temp_file)
