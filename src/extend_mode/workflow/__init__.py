#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workflow子模块，包含翻译工作流管理功能
"""

from .generator import generate_translation_rules_func as generate_translation_rules
from .updater import update_translation_rules_func as update_translation_rules
from .runner import run_complete_workflow

__all__ = [
    "generate_translation_rules",
    "update_translation_rules",
    "run_complete_workflow",
]
