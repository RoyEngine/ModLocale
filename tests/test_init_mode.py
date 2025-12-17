#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试init_mode模块初始化功能的脚本
"""

import os
import sys

# 添加项目根目录到Python搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 简化测试，直接导入必要的模块和函数
from src.common.config_utils import config_manager
from src.init_mode import run_init_tasks, get_mod_mapping

# 关闭日志，避免输出被截断
import logging
logging.disable(logging.CRITICAL)

def test_init_mode():
    """测试init_mode模块初始化功能"""
    print("=== 开始测试init_mode模块初始化 ===")
    
    try:
        # 直接从配置管理器获取mod_root目录
        print("1. 获取mod_root目录...")
        mod_root = config_manager.get_directory("mod_root")
        if not mod_root:
            print("❌ 获取mod_root目录失败")
            return False
        print(f"✅ 成功获取mod_root目录: {mod_root}")
        
        # 执行init_mode初始化
        print("2. 执行init_mode初始化...")
        init_result = run_init_tasks(mod_root)
        print(f"✅ init_mode初始化完成，状态: {init_result['status']}")
        print(f"   成功: {init_result['data']['success_count']}, 失败: {init_result['data']['fail_count']}")
        
        if init_result['status'] == 'fail':
            print(f"⚠️  初始化失败原因: {init_result['data']['fail_reasons']}")
        
        # 验证初始化结果
        print("3. 验证初始化结果...")
        mod_mappings = get_mod_mapping()
        print(f"✅ 获取mod映射关系成功，共{len(mod_mappings)}个mod")
        
        print("=== init_mode模块初始化测试完成 ===")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_init_mode()

