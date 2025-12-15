#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查原始文件夹是否被修改
"""

import os
import time

def check_modification_time(directory):
    """
    检查目录下文件的修改时间
    """
    print(f"检查 {directory} 目录文件修改时间：")
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.java', '.kt', '.kts')):
                file_path = os.path.join(root, file)
                mod_time = os.path.getmtime(file_path)
                print(f"{file_path}: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))}")
                return  # 只显示第一个文件
    
    print(f"{directory} 目录下没有找到Java/Kotlin文件")

# 检查source目录
check_modification_time(r'D:/Poki/Tool/Localization_File/source/English')
check_modification_time(r'D:/Poki/Tool/Localization_File/source/Chinese')

print("\n检查规则文件目录：")
check_modification_time(r'D:/Poki/Tool/Localization_File/rule/English')
check_modification_time(r'D:/Poki/Tool/Localization_File/rule/Chinese')
