#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extend_mode模块，包含字符串映射功能

该模块负责使用映射规则将一种语言映射到另一种语言，支持以下功能：
1. 基于已有src文件夹进行映射
2. 基于JAR文件进行映射
3. 使用映射规则文件进行映射
4. 支持中英文双向映射
5. 生成映射报告
6. 支持多mod并行处理
7. 映射规则管理
8. 工作流管理

该模块不再执行初始化操作，仅专注于语言映射功能，初始化操作由init_mode模块统一处理
"""

from .core import run_extend_sub_flow
from .rules import (
    extract_mapping_rules,
    process_unmapped_content,
    detect_and_resolve_conflicts,
    auto_generate_rules,
    manage_rules
)
from .workflow import (
    generate_translation_rules,
    update_translation_rules,
    run_complete_workflow
)

__all__ = [
    "run_extend_sub_flow",
    "extract_mapping_rules",
    "process_unmapped_content",
    "detect_and_resolve_conflicts",
    "auto_generate_rules",
    "manage_rules",
    "generate_translation_rules",
    "update_translation_rules",
    "run_complete_workflow",
]
