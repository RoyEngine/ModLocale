#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行界面测试脚本

该脚本用于测试ModLocale工具的命令行界面功能，包括所有核心功能和边缘情况。
"""

import os
import sys
import subprocess
import time
import tempfile
import json
import shutil
from datetime import datetime

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 测试结果记录
TEST_RESULTS = {
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "test_cases": []
}

def run_test_case(test_name, test_description, command, expected_output=None, expected_files=None, expected_exit_code=0):
    """
    运行单个测试用例
    
    Args:
        test_name: 测试用例名称
        test_description: 测试用例描述
        command: 要执行的命令
        expected_output: 预期输出内容（可选）
        expected_files: 预期生成的文件列表（可选）
        expected_exit_code: 预期退出码（默认0）
    """
    global TEST_RESULTS
    
    print(f"\n=== 测试用例: {test_name} ===")
    print(f"描述: {test_description}")
    print(f"命令: {command}")
    
    TEST_RESULTS["total_tests"] += 1
    
    try:
        # 执行命令
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        # 记录测试结果
        test_result = {
            "name": test_name,
            "description": test_description,
            "command": command,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "status": "passed" if result.returncode == expected_exit_code else "failed"
        }
        
        # 检查预期输出
        if expected_output and expected_output not in result.stdout:
            test_result["status"] = "failed"
            test_result["error"] = f"预期输出 '{expected_output}' 未在实际输出中找到"
        
        # 检查预期文件
        if expected_files:
            missing_files = []
            for file_path in expected_files:
                full_path = os.path.join(PROJECT_ROOT, file_path)
                if not os.path.exists(full_path):
                    missing_files.append(file_path)
            
            if missing_files:
                test_result["status"] = "failed"
                test_result["error"] = f"预期文件未找到: {missing_files}"
        
        # 更新测试结果统计
        if test_result["status"] == "passed":
            TEST_RESULTS["passed_tests"] += 1
        else:
            TEST_RESULTS["failed_tests"] += 1
        
        TEST_RESULTS["test_cases"].append(test_result)
        
        print(f"结果: {test_result['status']}")
        if test_result["status"] == "failed":
            print(f"错误: {test_result.get('error', '未知错误')}")
            print(f"退出码: {result.returncode}")
            print(f"标准输出: {result.stdout}")
            print(f"标准错误: {result.stderr}")
            
    except Exception as e:
        TEST_RESULTS["failed_tests"] += 1
        test_result = {
            "name": test_name,
            "description": test_description,
            "command": command,
            "status": "failed",
            "error": str(e)
        }
        TEST_RESULTS["test_cases"].append(test_result)
        print(f"结果: failed")
        print(f"错误: {str(e)}")

def generate_test_report():
    """
    生成测试报告
    """
    global TEST_RESULTS
    
    # 生成报告文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.json"
    report_file_md = f"test_report_{timestamp}.md"
    
    # 保存JSON格式报告
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(TEST_RESULTS, f, indent=4, ensure_ascii=False)
    
    # 生成Markdown格式报告
    with open(report_file_md, "w", encoding="utf-8") as f:
        f.write("# ModLocale 命令行界面测试报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## 测试摘要\n\n")
        f.write(f"- 总测试用例数: {TEST_RESULTS['total_tests']}\n")
        f.write(f"- 通过测试数: {TEST_RESULTS['passed_tests']}\n")
        f.write(f"- 失败测试数: {TEST_RESULTS['failed_tests']}\n")
        f.write(f"- 通过率: {TEST_RESULTS['passed_tests'] / TEST_RESULTS['total_tests'] * 100:.2f}%\n\n")
        
        f.write("## 测试用例详情\n\n")
        for test_case in TEST_RESULTS['test_cases']:
            f.write(f"### {test_case['name']}\n")
            f.write(f"**描述**: {test_case['description']}\n")
            f.write(f"**命令**: `{test_case['command']}`\n")
            f.write(f"**结果**: {test_case['status']}\n")
            
            if test_case['status'] == "failed":
                f.write(f"**错误**: {test_case.get('error', '未知错误')}\n")
                
                if 'exit_code' in test_case:
                    f.write(f"**退出码**: {test_case['exit_code']}\n")
                
                if 'stderr' in test_case and test_case['stderr']:
                    f.write(f"**标准错误**:\n```\n{test_case['stderr']}\n```\n")
            
            f.write("\n")
    
    print(f"\n=== 测试完成 ===")
    print(f"测试报告已生成: {report_file}")
    print(f"Markdown报告已生成: {report_file_md}")
    print(f"总测试用例数: {TEST_RESULTS['total_tests']}")
    print(f"通过测试数: {TEST_RESULTS['passed_tests']}")
    print(f"失败测试数: {TEST_RESULTS['failed_tests']}")
    print(f"通过率: {TEST_RESULTS['passed_tests'] / TEST_RESULTS['total_tests'] * 100:.2f}%")

def main():
    """
    主函数，执行所有测试用例
    """
    print("ModLocale 命令行界面测试")
    print(f"项目根目录: {PROJECT_ROOT}")
    print("=" * 50)
    
    # 测试用例1: 显示帮助信息
    run_test_case(
        "显示帮助信息",
        "测试使用 -h 参数显示帮助信息",
        "python src/main.py -h",
        expected_output="ModLocale 主入口"
    )
    
    # 测试用例2: 显示Extract模式帮助信息
    run_test_case(
        "显示Extract模式帮助信息",
        "测试显示Extract模式的帮助信息",
        "python src/main.py extract -h",
        expected_output="Extract模式用于从src目录提取字符串"
    )
    
    # 测试用例3: 显示Extend模式帮助信息
    run_test_case(
        "显示Extend模式帮助信息",
        "测试显示Extend模式的帮助信息",
        "python src/main.py extend -h",
        expected_output="Extend模式用于使用映射规则将一种语言映射到另一种语言"
    )
    
    # 测试用例4: 显示Decompile模式帮助信息
    run_test_case(
        "显示Decompile模式帮助信息",
        "测试显示Decompile模式的帮助信息",
        "python src/main.py decompile -h",
        expected_output="Decompile模式用于反编译或提取JAR文件"
    )
    
    # 测试用例5: 显示映射规则管理帮助信息
    run_test_case(
        "显示映射规则管理帮助信息",
        "测试显示映射规则管理的帮助信息",
        "python src/main.py localization -h",
        expected_output="映射规则管理，用于处理翻译规则的提取、更新、冲突检测和解决"
    )
    
    # 测试用例6: 显示完整工作流帮助信息
    run_test_case(
        "显示完整工作流帮助信息",
        "测试显示完整工作流的帮助信息",
        "python src/main.py workflow -h",
        expected_output="完整工作流，用于执行从双语数据到翻译回写的完整流程"
    )
    
    # 测试用例7: 测试无效模式
    run_test_case(
        "测试无效模式",
        "测试使用无效模式名称",
        "python src/main.py invalid_mode",
        expected_exit_code=2
    )
    
    # 测试用例8: 测试无效子命令
    run_test_case(
        "测试无效子命令",
        "测试使用无效子命令",
        "python src/main.py workflow invalid_subcommand",
        expected_exit_code=2
    )
    
    # 测试用例9: 测试测试模式
    run_test_case(
        "测试测试模式",
        "测试使用--test-mode参数",
        "python src/main.py --test-mode '1,0'",
        expected_output="请选择提取语言"
    )
    
    # 生成测试报告
    generate_test_report()

if __name__ == "__main__":
    main()
