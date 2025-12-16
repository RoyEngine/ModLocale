#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地化工具命令行入口脚本

该脚本是本地化工具的命令行入口，用于调用src.common.localization_tool中的main函数
"""

import os
import sys

# 添加项目根目录到Python搜索路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入localization_tool的main函数
from src.common.localization_tool import main

if __name__ == "__main__":
    sys.exit(main())
