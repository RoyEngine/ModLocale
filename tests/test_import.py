#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的导入测试脚本
"""

import os
import sys

print("当前工作目录:", os.getcwd())
print("Python路径:", sys.path)

# 尝试导入Localization_Tool模块
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    print("添加到Python路径:", os.path.dirname(os.path.abspath(__file__)))
    
    from Localization_Tool.src.common.yaml_utils import load_yaml_mappings
    print("成功导入load_yaml_mappings")
    
    from Localization_Tool.src.common.yaml_utils import generate_translation_rules
    print("成功导入generate_translation_rules")
    
    from Localization_Tool.src.common.yaml_utils import update_translation_rules
    print("成功导入update_translation_rules")
    
    print("所有导入成功!")
except Exception as e:
    print(f"导入错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
