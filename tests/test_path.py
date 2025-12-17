#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本，用于验证 Localization_File 路径是否正确
"""

import os

def main():
    print("Testing Localization_File path recognition...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tool_root = script_dir
    main_root = os.path.dirname(tool_root)
    expected_path = os.path.join(main_root, 'Localization_File')
    print(f'Expected external Localization_File path: {expected_path}')
    print(f'External Localization_File exists: {os.path.exists(expected_path)}')
    internal_path = os.path.join(tool_root, 'Localization_File')
    print(f'Internal Localization_File exists: {os.path.exists(internal_path)}')
    print('Test completed.')

if __name__ == '__main__':
    main()
