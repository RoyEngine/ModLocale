#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试输出文件夹命名是否与源mod文件夹名称一致
"""

import os
import sys
import tempfile
import shutil

# 添加项目根目录到Python搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.init_mode.core import run_init_tasks
from src.extract_mode.core import _extract_strings_from_source

class TestOutputNaming:
    """
    测试输出文件夹命名是否与源mod文件夹名称一致
    """
    
    def setup_method(self):
        """
        在每个测试方法前执行，创建临时目录结构
        """
        # 创建临时根目录
        self.temp_root = tempfile.mkdtemp()
        
        # 创建必要的目录结构
        self.localization_file_path = os.path.join(self.temp_root, "File")
        self.source_path = os.path.join(self.localization_file_path, "source")
        self.output_path = os.path.join(self.localization_file_path, "output")
        
        # 创建英文源目录
        self.english_source_path = os.path.join(self.source_path, "English")
        os.makedirs(self.english_source_path, exist_ok=True)
        
        # 创建测试mod目录
        self.test_mod_name = "Test Mod 1.0.0"
        self.test_mod_path = os.path.join(self.english_source_path, self.test_mod_name)
        os.makedirs(self.test_mod_path, exist_ok=True)
        
        # 创建src目录
        self.test_src_path = os.path.join(self.test_mod_path, "src")
        os.makedirs(self.test_src_path, exist_ok=True)
        
        # 创建mod_info.json文件
        mod_info_path = os.path.join(self.test_mod_path, "mod_info.json")
        with open(mod_info_path, "w") as f:
            f.write('''{
                "id": "test_mod",
                "name": "Test Mod",
                "version": "1.0.0",
                "author": "Test Author",
                "description": "Test Description"
            }''')
        
        # 创建一个简单的Java文件用于测试提取
        java_file_path = os.path.join(self.test_src_path, "Test.java")
        with open(java_file_path, "w") as f:
            f.write('''public class Test {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        System.out.println("Test Message");
    }
}''')
    
    def teardown_method(self):
        """
        在每个测试方法后执行，清理临时目录
        """
        # 删除临时目录
        shutil.rmtree(self.temp_root)
    
    def test_extract_output_naming(self):
        """
        测试extract_mode输出文件夹命名是否与源mod文件夹名称一致
        """
        print("=== 测试extract_mode输出文件夹命名 ===")
        
        # 执行提取流程
        result = _extract_strings_from_source(
            self.test_src_path, 
            "English", 
            self.temp_root, 
            "test_timestamp"
        )
        
        # 检查结果
        assert result["success"] == True, f"提取失败: {result}"
        
        # 获取输出路径
        output_path = result["data"]["output_path"]
        print(f"输出路径: {output_path}")
        
        # 验证输出文件夹名称是否与源mod文件夹名称一致
        output_mod_name = os.path.basename(output_path)
        print(f"源mod文件夹名称: {self.test_mod_name}")
        print(f"输出文件夹名称: {output_mod_name}")
        
        assert output_mod_name == self.test_mod_name, f"输出文件夹名称与源mod文件夹名称不一致: {output_mod_name} != {self.test_mod_name}"
        
        print("✅ extract_mode输出文件夹命名测试通过")
        return True

if __name__ == "__main__":
    print("===========================================")
    print("           测试输出文件夹命名")
    print("===========================================")
    
    test = TestOutputNaming()
    test.setup_method()
    
    try:
        test.test_extract_output_naming()
        print("\n✅ 所有测试通过！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        test.teardown_method()
    
    print("\n===========================================")
    print("              测试完成")
    print("===========================================")
