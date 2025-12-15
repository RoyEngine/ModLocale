#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Localization_File目录结构测试脚本

功能：测试Localization_File目录结构的完整性和权限
测试项目：
1. 源代码目录测试
2. JAR文件测试
3. JAR反编译输出目录测试
4. 规则文件目录测试
5. 输出目录测试

执行方式：直接运行脚本，无需参数
输出：测试结果报告
"""

import os
import json
import tempfile
from typing import Dict, List, Tuple

# 测试目录
TEST_ROOT = "D:\\Poki\\Tool\\Localization_File"

# 测试文件内容
TEST_CONTENT = "This is a test file for permission verification."

# 测试结果结构
class TestResult:
    def __init__(self):
        self.success = 0
        self.failed = 0
        self.results: List[Dict[str, any]] = []
    
    def add_result(self, test_name: str, status: bool, message: str):
        """添加测试结果"""
        self.results.append({
            "test_name": test_name,
            "status": "PASS" if status else "FAIL",
            "message": message
        })
        if status:
            self.success += 1
        else:
            self.failed += 1
    
    def get_summary(self) -> str:
        """获取测试结果摘要"""
        total = self.success + self.failed
        return f"测试完成：共 {total} 项，成功 {self.success} 项，失败 {self.failed} 项"
    
    def get_detailed_results(self) -> str:
        """获取详细测试结果"""
        result_str = "\n详细测试结果：\n"
        for result in self.results:
            status = "✅" if result["status"] == "PASS" else "❌"
            result_str += f"{status} {result['test_name']}: {result['message']}\n"
        return result_str

def test_directory_read_write(path: str) -> Tuple[bool, str]:
    """测试目录读写权限"""
    try:
        # 检查目录是否存在
        if not os.path.exists(path):
            return False, f"目录不存在: {path}"
        
        # 检查读权限
        if not os.access(path, os.R_OK):
            return False, f"目录无读权限: {path}"
        
        # 检查写权限
        if not os.access(path, os.W_OK):
            return False, f"目录无写权限: {path}"
        
        # 创建临时测试文件
        temp_file = os.path.join(path, "temp_test_file.txt")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(TEST_CONTENT)
        
        # 验证文件创建成功
        if not os.path.exists(temp_file):
            return False, f"无法在目录创建文件: {path}"
        
        # 读取临时文件内容
        with open(temp_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        if content != TEST_CONTENT:
            os.remove(temp_file)  # 清理临时文件
            return False, f"文件读写不一致: {path}"
        
        # 删除临时文件
        os.remove(temp_file)
        
        return True, f"目录读写权限正常: {path}"
    except Exception as e:
        return False, f"目录测试失败: {path}, 错误: {str(e)}"

def test_file_read(path: str) -> Tuple[bool, str]:
    """测试文件读取权限和完整性"""
    try:
        # 检查文件是否存在
        if not os.path.exists(path):
            return False, f"文件不存在: {path}"
        
        # 检查读权限
        if not os.access(path, os.R_OK):
            return False, f"文件无读权限: {path}"
        
        # 打开文件验证完整性
        with open(path, "rb") as f:
            content = f.read()
        
        # 检查文件大小
        if len(content) == 0:
            return False, f"文件为空: {path}"
        
        return True, f"文件读取正常: {path}"
    except Exception as e:
        return False, f"文件测试失败: {path}, 错误: {str(e)}"

def test_json_file(path: str) -> Tuple[bool, str]:
    """测试JSON文件格式正确性"""
    try:
        # 先测试文件读取
        read_result, read_message = test_file_read(path)
        if not read_result:
            return read_result, read_message
        
        # 测试JSON格式
        with open(path, "r", encoding="utf-8") as f:
            json.load(f)
        
        return True, f"JSON文件格式正确: {path}"
    except json.JSONDecodeError as e:
        return False, f"JSON文件格式错误: {path}, 错误: {str(e)}"
    except Exception as e:
        return False, f"JSON文件测试失败: {path}, 错误: {str(e)}"

def test_directory_structure(expected_structure: List[str]) -> List[Tuple[bool, str]]:
    """测试目录结构完整性"""
    results = []
    for path in expected_structure:
        full_path = os.path.join(TEST_ROOT, path)
        if os.path.exists(full_path):
            results.append((True, f"目录存在: {full_path}"))
        else:
            results.append((False, f"目录缺失: {full_path}"))
    return results

def main():
    """主函数"""
    print("==========================================")
    print("Localization_File目录结构测试脚本")
    print("==========================================")
    
    # 初始化测试结果
    test_result = TestResult()
    
    # 1. 测试Localization_File根目录存在性
    if not os.path.exists(TEST_ROOT):
        print(f"❌ 错误：Localization_File目录不存在: {TEST_ROOT}")
        return
    
    # 2. 定义测试目录结构
    expected_directories = [
        # 源代码目录
        "source/English",
        "source/Chinese",
        "source_backup/English",
        "source_backup/Chinese",
        
        # 规则文件目录
        "rule/English",
        "rule/Chinese",
        
        # 输出目录
        "output"
    ]
    
    # 3. 测试目录结构完整性
    print("\n1. 测试目录结构完整性...")
    structure_results = test_directory_structure(expected_directories)
    for status, message in structure_results:
        test_result.add_result("目录结构测试", status, message)
    
    # 4. 测试各目录读写权限
    print("\n2. 测试目录读写权限...")
    
    # 源代码根目录测试
    source_root_dirs = [
        "source/English",
        "source/Chinese",
        "source_backup/English",
        "source_backup/Chinese"
    ]
    
    for dir_path in source_root_dirs:
        full_path = os.path.join(TEST_ROOT, dir_path)
        status, message = test_directory_read_write(full_path)
        test_result.add_result("目录读写测试", status, message)
    
    # 规则文件目录测试
    rule_dirs = [
        "rule/English",
        "rule/Chinese"
    ]
    
    for dir_path in rule_dirs:
        full_path = os.path.join(TEST_ROOT, dir_path)
        status, message = test_directory_read_write(full_path)
        test_result.add_result("规则目录测试", status, message)
    
    # 输出目录测试
    output_dirs = [
        "output",
        "output/Extend_en2zh",
        "output/Extend_zh2en"
    ]
    
    for dir_path in output_dirs:
        full_path = os.path.join(TEST_ROOT, dir_path)
        # 如果目录不存在，先创建
        if not os.path.exists(full_path):
            try:
                os.makedirs(full_path, exist_ok=True)
            except Exception as e:
                test_result.add_result("输出目录测试", False, f"无法创建输出目录: {full_path}, 错误: {str(e)}")
                continue
        
        status, message = test_directory_read_write(full_path)
        test_result.add_result("输出目录测试", status, message)
    
    # 5. 测试实际存在的mod文件夹
    print("\n3. 测试实际存在的mod文件夹...")
    
    # 检测实际存在的mod文件夹
    mod_folders = []
    
    # 检查source/English目录下的实际mod文件夹
    english_source_path = os.path.join(TEST_ROOT, "source", "English")
    if os.path.exists(english_source_path):
        for item in os.listdir(english_source_path):
            item_path = os.path.join(english_source_path, item)
            if os.path.isdir(item_path):
                mod_folders.append(item)
    
    # 如果没有检测到mod文件夹，使用默认测试文件夹
    if not mod_folders:
        mod_folders = ["test_mod"]
    
    print(f"检测到 {len(mod_folders)} 个mod文件夹: {', '.join(mod_folders)}")
    
    # 测试每个mod文件夹的权限
    for mod_folder in mod_folders:
        # 测试mod文件夹本身的权限
        mod_path = os.path.join(TEST_ROOT, "source", "English", mod_folder)
        status, message = test_directory_read_write(mod_path)
        test_result.add_result(f"mod文件夹测试", status, message)
        
        # 测试mod文件夹下的src目录权限
        src_path = os.path.join(mod_path, "src")
        if os.path.exists(src_path):
            status, message = test_directory_read_write(src_path)
            test_result.add_result(f"mod src目录测试", status, message)
        
        # 测试mod文件夹下的jar目录权限
        jar_path = os.path.join(mod_path, "jar")
        if os.path.exists(jar_path):
            status, message = test_directory_read_write(jar_path)
            test_result.add_result(f"mod jar目录测试", status, message)
    
    # 6. 测试规则文件目录权限
    print("\n4. 测试规则文件目录权限...")
    rule_dirs = [
        "rule/English",
        "rule/Chinese"
    ]
    
    for dir_path in rule_dirs:
        full_path = os.path.join(TEST_ROOT, dir_path)
        status, message = test_directory_read_write(full_path)
        test_result.add_result("规则文件目录测试", status, message)
    
    # 7. 测试输出目录权限
    print("\n5. 测试输出目录权限...")
    output_dirs = [
        "output",
        "output/Extend_en2zh",
        "output/Extend_zh2en"
    ]
    
    for dir_path in output_dirs:
        full_path = os.path.join(TEST_ROOT, dir_path)
        status, message = test_directory_read_write(full_path)
        test_result.add_result("输出目录测试", status, message)
    
    # 7. 输出测试结果
    print("\n" + "="*50)
    print(test_result.get_summary())
    print(test_result.get_detailed_results())
    print("="*50)
    
    # 8. 生成测试报告文件
    report_file = os.path.join(TEST_ROOT, "localization_file_test_report.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("Localization_File目录结构测试报告\n")
        f.write("="*50 + "\n")
        f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(test_result.get_summary() + "\n")
        f.write(test_result.get_detailed_results() + "\n")
    
    print(f"\n测试报告已保存至: {report_file}")
    print("==========================================")

if __name__ == "__main__":
    import time
    main()
