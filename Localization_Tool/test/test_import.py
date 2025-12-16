#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入功能
"""

import os
import sys

# 添加项目根目录到Python搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=== 测试导入功能 ===")

try:
    from src.common import rename_mod_folders, restore_backup
    print("✓ 成功导入rename_mod_folders和restore_backup函数")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 测试完成 ===")
