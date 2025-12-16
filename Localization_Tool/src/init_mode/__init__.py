# init_mode/__init__.py
"""
初始化模式包

该包包含程序启动时的初始化操作
"""

from .core import (
    init_project_structure,
    auto_rename_files_folders,
    run_init_tasks,
    build_mod_mappings,
    get_mod_mapping,
    get_mod_path_by_id,
    get_mod_info_by_path,
    build_group_mappings,
    get_group_mapping,
    get_group_by_id,
    get_group_path,
    run_extract_function,
    run_extend_function,
    run_decompile_function,
    run_decompile_and_extract,
    run_parallel_processing
)

__all__ = [
    "init_project_structure",
    "auto_rename_files_folders",
    "run_init_tasks",
    "build_mod_mappings",
    "get_mod_mapping",
    "get_mod_path_by_id",
    "get_mod_info_by_path",
    "build_group_mappings",
    "get_group_mapping",
    "get_group_by_id",
    "get_group_path",
    "run_extract_function",
    "run_extend_function",
    "run_decompile_function",
    "run_decompile_and_extract",
    "run_parallel_processing"
]
