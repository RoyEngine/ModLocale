#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试脚本

该脚本包含对init_mode模块的单元测试
"""

import os
import sys
import tempfile
import shutil

# 添加项目根目录到Python搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pytest
from src.init_mode.core import (
    ModInfo,
    init_project_structure,
    build_group_mappings,
    get_group_by_id,
    get_group_path,
    run_parallel_processing
)

class TestModInfo:
    """
    测试ModInfo类
    """
    
    def test_mod_info_creation(self):
        """
        测试ModInfo对象创建
        """
        # 创建临时mod_info.json文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('''{
                "id": "test_mod",
                "name": "Test Mod",
                "version": "1.0.0",
                "author": "Test Author",
                "description": "Test Description"
            }''')
            temp_path = f.name
        
        try:
            # 创建ModInfo对象
            mod_info = ModInfo(temp_path)
            
            # 验证属性
            assert mod_info.mod_id == "test_mod"
            assert mod_info.name == "Test Mod"
            assert mod_info.version == "1.0.0"
            assert mod_info.author == "Test Author"
            assert mod_info.description == "Test Description"
            assert mod_info.valid == True
        finally:
            # 清理临时文件
            os.unlink(temp_path)
    
    def test_mod_info_to_dict(self):
        """
        测试ModInfo对象转换为字典
        """
        # 创建临时mod_info.json文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('''{
                "id": "test_mod",
                "name": "Test Mod",
                "version": "1.0.0"
            }''')
            temp_path = f.name
        
        try:
            # 创建ModInfo对象
            mod_info = ModInfo(temp_path)
            
            # 转换为字典
            mod_info_dict = mod_info.to_dict()
            
            # 验证字典内容
            assert mod_info_dict["id"] == "test_mod"
            assert mod_info_dict["name"] == "Test Mod"
            assert mod_info_dict["version"] == "1.0.0"
            assert mod_info_dict["valid"] == True
        finally:
            # 清理临时文件
            os.unlink(temp_path)

class TestInitFunctions:
    """
    测试初始化函数
    """
    
    def setup_method(self):
        """
        在每个测试方法前执行，创建临时目录
        """
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """
        在每个测试方法后执行，清理临时目录
        """
        shutil.rmtree(self.temp_dir)
    
    def test_init_project_structure(self):
        """
        测试文件夹结构创建功能
        """
        # 执行文件夹创建
        result = init_project_structure(self.temp_dir)
        
        # 验证结果
        assert result["status"] == "success"
        assert result["data"]["success_count"] > 0
        
        # 验证关键文件夹是否存在
        required_folders = [
            "File/source/Chinese",
            "File/source/English",
            "File/source_backup/Chinese",
            "File/source_backup/English",
            "File/output/Extract_Chinese",
            "File/output/Extract_English",
            "File/output/Extend_en2zh",
            "File/output/Extend_zh2en",
            "File/rule/Chinese",
            "File/rule/English"
        ]
        
        for folder in required_folders:
            folder_path = os.path.join(self.temp_dir, folder)
            assert os.path.exists(folder_path), f"文件夹 {folder} 未创建"

class TestGroupFunctions:
    """
    测试分组功能
    """
    
    def setup_method(self):
        """
        在每个测试方法前执行，创建临时目录结构
        """
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建必要的目录结构
        os.makedirs(os.path.join(self.temp_dir, "File", "source", "Chinese", "Test Mod 1.0.0"))
        os.makedirs(os.path.join(self.temp_dir, "File", "source", "English", "Test Mod 1.0.0"))
        os.makedirs(os.path.join(self.temp_dir, "File", "rule", "Chinese", "Test Mod 1.0.0"))
        os.makedirs(os.path.join(self.temp_dir, "File", "rule", "English", "Test Mod 1.0.0"))
        
        # 创建mod_info.json文件
        with open(os.path.join(self.temp_dir, "File", "source", "Chinese", "Test Mod 1.0.0", "mod_info.json"), "w") as f:
            f.write('''{
                "id": "test_mod",
                "name": "Test Mod",
                "version": "1.0.0"
            }''')
        
        with open(os.path.join(self.temp_dir, "File", "source", "English", "Test Mod 1.0.0", "mod_info.json"), "w") as f:
            f.write('''{
                "id": "test_mod",
                "name": "Test Mod",
                "version": "1.0.0"
            }''')
    
    def teardown_method(self):
        """
        在每个测试方法后执行，清理临时目录
        """
        shutil.rmtree(self.temp_dir)
    
    def test_build_group_mappings(self):
        """
        测试构建分组映射关系
        """
        from src.init_mode.core import mod_mappings
        
        # 先构建mod映射
        from src.init_mode.core import build_mod_mappings
        build_mod_mappings(os.path.join(self.temp_dir, "File"))
        
        # 构建分组映射
        result = build_group_mappings(os.path.join(self.temp_dir, "File"))
        
        # 验证结果
        assert result["status"] == "success"
        assert result["data"]["success_count"] > 0
    
    def test_get_group_by_id(self):
        """
        测试根据mod_id获取分组信息
        """
        from src.init_mode.core import mod_mappings
        
        # 先构建mod映射和分组映射
        from src.init_mode.core import build_mod_mappings
        build_mod_mappings(os.path.join(self.temp_dir, "File"))
        build_group_mappings(os.path.join(self.temp_dir, "File"))
        
        # 获取分组信息
        group_info = get_group_by_id("test_mod")
        
        # 验证分组信息
        assert "source_zh" in group_info
        assert "source_en" in group_info
        assert "rule_zh" in group_info
        assert "rule_en" in group_info
        
        assert os.path.exists(group_info["source_zh"])
        assert os.path.exists(group_info["source_en"])
        assert os.path.exists(group_info["rule_zh"])
        assert os.path.exists(group_info["rule_en"])
    
    def test_get_group_path(self):
        """
        测试根据mod_id、分组类型和语言获取文件夹路径
        """
        from src.init_mode.core import mod_mappings
        
        # 先构建mod映射和分组映射
        from src.init_mode.core import build_mod_mappings
        build_mod_mappings(os.path.join(self.temp_dir, "File"))
        build_group_mappings(os.path.join(self.temp_dir, "File"))
        
        # 测试获取source_zh路径
        source_zh_path = get_group_path("test_mod", "source", "Chinese")
        assert os.path.exists(source_zh_path)
        
        # 测试获取source_en路径
        source_en_path = get_group_path("test_mod", "source", "English")
        assert os.path.exists(source_en_path)
        
        # 测试获取rule_zh路径
        rule_zh_path = get_group_path("test_mod", "rule", "Chinese")
        assert os.path.exists(rule_zh_path)
        
        # 测试获取rule_en路径
        rule_en_path = get_group_path("test_mod", "rule", "English")
        assert os.path.exists(rule_en_path)

class TestParallelProcessing:
    """
    测试并行处理功能
    """
    
    def test_run_parallel_processing(self):
        """
        测试并行处理功能
        """
        # 定义测试函数
        def test_func(mod_id):
            return {
                "status": "success",
                "data": {
                    "total_count": 1,
                    "success_count": 1,
                    "fail_count": 0,
                    "fail_reasons": []
                }
            }
        
        # 测试并行处理
        mod_ids = [f"mod_{i}" for i in range(5)]
        result = run_parallel_processing(test_func, mod_ids, max_processes=2)
        
        # 验证结果
        assert result["status"] == "success"
        assert result["data"]["total_count"] == 5
        assert result["data"]["success_count"] == 5
        assert result["data"]["fail_count"] == 0
    
    def test_run_parallel_processing_with_timeout(self):
        """
        测试并行处理超时功能
        """
        # 定义测试函数，模拟长时间运行
        def test_func(mod_id):
            import time
            time.sleep(2)  # 休眠2秒
            return {
                "status": "success",
                "data": {
                    "total_count": 1,
                    "success_count": 1,
                    "fail_count": 0,
                    "fail_reasons": []
                }
            }
        
        # 测试并行处理，设置超时1秒
        mod_ids = [f"mod_{i}" for i in range(2)]
        result = run_parallel_processing(test_func, mod_ids, max_processes=2, timeout=1)
        
        # 验证结果
        assert result["status"] == "fail"
        assert result["data"]["total_count"] == 2
        assert result["data"]["success_count"] == 0
        assert result["data"]["fail_count"] == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
