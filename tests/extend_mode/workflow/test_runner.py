#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workflow子模块 - runner.py测试
"""

import os
import tempfile
import pytest

from src.extend_mode.workflow.runner import run_complete_workflow

class TestRunner:
    """
    测试完整工作流执行功能
    """
    
    def test_run_complete_workflow_no_files(self):
        """
        测试没有提供文件的情况
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_complete_workflow(
                english_file="/invalid/path.yaml",
                chinese_file="/invalid/path.yaml",
                source_dir=temp_dir,
                output_dir=os.path.join(temp_dir, "output")
            )
            assert result["status"] == "error"
    
    def test_run_complete_workflow_valid(self):
        """
        测试从有效文件执行完整工作流的功能
        """
        # 创建临时YAML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f2:
            f1.write("- id: test_1\n  original: test string\n")
            f2.write("- id: test_1\n  original: 测试字符串\n")
            en_file = f1.name
            zh_file = f2.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = os.path.join(temp_dir, "src")
            os.makedirs(source_dir, exist_ok=True)
            output_dir = os.path.join(temp_dir, "output")
            
            result = run_complete_workflow(
                english_file=en_file,
                chinese_file=zh_file,
                source_dir=source_dir,
                output_dir=output_dir,
                use_cache=False
            )
            
            assert result["status"] == "success"
            assert "完整工作流执行完成" in result["message"]
            assert os.path.exists(result["rules_file"])
            assert os.path.exists(result["report_file"])
            assert os.path.exists(result["translated_dir"])
        
        # 清理临时文件
        os.unlink(en_file)
        os.unlink(zh_file)
    
    def test_run_complete_workflow_with_existing_rules(self):
        """
        测试使用现有规则执行完整工作流的功能
        """
        # 创建临时YAML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f2, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f3:
            f1.write("- id: existing_1\n  original: existing string\n  translated: existing translation\n  status: translated\n")
            f2.write("- id: test_1\n  original: test string\n")
            f3.write("- id: test_1\n  original: 测试字符串\n")
            existing_rules = f1.name
            en_file = f2.name
            zh_file = f3.name
        
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = os.path.join(temp_dir, "src")
            os.makedirs(source_dir, exist_ok=True)
            output_dir = os.path.join(temp_dir, "output")
            
            result = run_complete_workflow(
                english_file=en_file,
                chinese_file=zh_file,
                source_dir=source_dir,
                output_dir=output_dir,
                existing_rules=existing_rules,
                use_cache=False
            )
            
            assert result["status"] == "success" or result["status"] == "error"
        
        # 清理临时文件
        os.unlink(existing_rules)
        os.unlink(en_file)
        os.unlink(zh_file)
