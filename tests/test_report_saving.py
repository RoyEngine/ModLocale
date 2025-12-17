#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试报告文件保存位置
"""

import os
import sys

# 添加项目根目录到Python搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.common.report_utils import generate_report, save_report
from src.common.timestamp_utils import get_timestamp

def test_report_saving():
    """测试报告文件保存位置"""
    print("=== 开始测试报告文件保存位置 ===")
    
    # 获取时间戳
    timestamp = get_timestamp()
    print(f"时间戳: {timestamp}")
    
    # 获取output目录路径
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "File", "output")
    print(f"输出目录: {output_dir}")
    
    # 1. 测试单个文件处理报告
    print("\n1. 测试单个文件处理报告...")
    single_report = generate_report(
        process_id=f"single_test_{timestamp}",
        mode="Test",
        sub_flow="测试单个文件",
        status="success",
        data={
            "total_count": 1,
            "success_count": 1,
            "fail_count": 0,
            "fail_reasons": []
        }
    )
    
    save_result = save_report(single_report, output_dir, timestamp)
    if save_result:
        print("✅ 单个文件报告保存成功")
    else:
        print("❌ 单个文件报告保存失败")
    
    # 2. 测试多个文件处理报告
    print("\n2. 测试多个文件处理报告...")
    multiple_report = generate_report(
        process_id=f"multiple_test_{timestamp}",
        mode="Test",
        sub_flow="测试多个文件",
        status="success",
        data={
            "total_count": 3,
            "success_count": 3,
            "fail_count": 0,
            "fail_reasons": []
        }
    )
    
    save_result = save_report(multiple_report, output_dir, timestamp)
    if save_result:
        print("✅ 多个文件报告保存成功")
    else:
        print("❌ 多个文件报告保存失败")
    
    # 3. 测试反编译多个JAR文件报告
    print("\n3. 测试反编译多个JAR文件报告...")
    decompile_report = generate_report(
        process_id=f"decompile_test_{timestamp}",
        mode="Decompile",
        sub_flow="反编译目录中所有JAR文件",
        status="success",
        data={
            "total_count": 2,
            "success_count": 2,
            "fail_count": 0,
            "fail_reasons": []
        }
    )
    
    save_result = save_report(decompile_report, os.path.join(output_dir, "Decompile_Test"), timestamp)
    if save_result:
        print("✅ 反编译报告保存成功")
    else:
        print("❌ 反编译报告保存失败")
    
    print("\n=== 测试完成 ===")
    print("\n请检查以下位置的报告文件:")
    print(f"1. 单个文件报告应保存在: {output_dir}")
    print(f"2. 多个文件报告应保存在: {os.path.join(output_dir, 'Report')}")
    print(f"3. 反编译报告应保存在: {os.path.join(output_dir, 'Decompile_Test', 'Report')}")

if __name__ == "__main__":
    test_report_saving()
