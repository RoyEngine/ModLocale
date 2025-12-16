#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本，用于验证 Localization_Tool 是否正确识别外部的 Localization_File 文件夹
"""

import os
import sys

# 添加项目根目录到Python搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.common.config_utils import load_config, get_all_directories, get_directory
from src.common.file_utils import check_source_folders

def test_localization_file_path():
    """
    测试 Localization_File 路径是否正确识别
    """
    print("==========================================")
    print("           Localization_File 路径测试")
    print("==========================================")
    
    # 加载配置
    print("1. 加载配置文件...")
    if not load_config():
        print("[ERROR] 加载配置文件失败")
        return False
    
    # 获取所有目录配置
    print("2. 获取目录配置...")
    directories = get_all_directories()
    print(f"   配置的目录：")
    for key, value in directories.items():
        print(f"   {key}: {value}")
    
    # 检查 mod_root 是否指向外部的 Localization_File
    mod_root = get_directory("mod_root")
    print(f"\n3. 检查 mod_root 路径：")
    print(f"   mod_root: {mod_root}")
    
    # 检查是否包含 "Localization_Tool/Localization_File"（内部路径）
    if "Localization_Tool\\Localization_File" in mod_root or "Localization_Tool/Localization_File" in mod_root:
        print("   [ERROR] mod_root 指向了内部的 Localization_File 文件夹")
        return False
    else:
        print("   [OK] mod_root 正确指向了外部的 Localization_File 文件夹")
    
    # 检查 source 路径
    source_path = get_directory("source")
    print(f"\n4. 检查 source 路径：")
    print(f"   source: {source_path}")
    
    # 检查 output 路径
    output_path = get_directory("output")
    print(f"\n5. 检查 output 路径：")
    print(f"   output: {output_path}")
    
    # 检查 source 文件夹结构
    print(f"\n6. 检查 source 文件夹结构...")
    detection_result = check_source_folders()
    print(f"   检测结果：")
    print(f"   - 英文src: {'✅' if detection_result['english_src'] else '❌'}")
    print(f"   - 英文jar: {'✅' if detection_result['english_jar'] else '❌'}")
    print(f"   - 中文src: {'✅' if detection_result['chinese_src'] else '❌'}")
    print(f"   - 中文jar: {'✅' if detection_result['chinese_jar'] else '❌'}")
    
    # 检查 Localization_Tool 目录下是否存在内部的 Localization_File 文件夹
    print(f"\n7. 检查 Localization_Tool 目录下是否存在内部的 Localization_File 文件夹...")
    tool_root = get_directory("tool_root")
    internal_localization_file = os.path.join(tool_root, "Localization_File")
    if os.path.exists(internal_localization_file):
        print(f"   [WARNING] Localization_Tool 目录下存在内部的 Localization_File 文件夹: {internal_localization_file}")
        print(f"   虽然当前代码不会使用它，但建议删除以避免混淆")
    else:
        print(f"   [OK] Localization_Tool 目录下不存在内部的 Localization_File 文件夹")
    
    print("\n==========================================")
    print("           测试完成")
    print("==========================================")
    
    return True

if __name__ == "__main__":
    test_localization_file_path()
