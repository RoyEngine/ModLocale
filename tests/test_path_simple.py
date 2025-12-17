#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本，用于验证 Localization_File 路径是否正确
"""

import os
import json

def test_simple_localization_file_path():
    """
    简单测试 Localization_File 路径
    """
    print("==========================================")
    print("           Localization_File 路径测试")
    print("==========================================")
    
    # 获取当前脚本的路径
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    
    print(f"1. 当前脚本路径：{script_path}")
    print(f"2. 当前脚本目录：{script_dir}")
    
    # 计算 tool_root 和 main_root
    tool_root = script_dir
    main_root = os.path.dirname(tool_root)
    
    print(f"3. 工具根目录(tool_root)：{tool_root}")
    print(f"4. 主目录(main_root)：{main_root}")
    
    # 计算外部 Localization_File 路径
    expected_localization_file = os.path.join(main_root, "Localization_File")
    print(f"5. 期望的外部 Localization_File 路径：{expected_localization_file}")
    
    # 检查外部 Localization_File 是否存在
    if os.path.exists(expected_localization_file):
        print(f"   [OK] 外部 Localization_File 文件夹存在")
    else:
        print(f"   [ERROR] 外部 Localization_File 文件夹不存在")
    
    # 检查内部 Localization_File 是否存在
    internal_localization_file = os.path.join(tool_root, "Localization_File")
    print(f"6. 检查内部 Localization_File 路径：{internal_localization_file}")
    
    if os.path.exists(internal_localization_file):
        print(f"   [WARNING] 内部 Localization_File 文件夹存在")
    else:
        print(f"   [OK] 内部 Localization_File 文件夹不存在")
    
    # 读取目录配置文件
    print(f"\n7. 读取目录配置文件...")
    config_file = os.path.join(script_dir, "config", "directory_config.json")
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"   配置文件中的 mod_root：{config['directories']['mod_root']}")
        print(f"   配置文件中的 source：{config['directories']['source']}")
        print(f"   配置文件中的 output：{config['directories']['output']}")
    else:
        print(f"   [ERROR] 目录配置文件不存在：{config_file}")
    
    print("\n==========================================")
    print("           测试完成")
    print("==========================================")

if __name__ == "__main__":
    test_simple_localization_file_path()
