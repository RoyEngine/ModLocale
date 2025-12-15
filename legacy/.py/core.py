#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract模式核心模块

该模块包含Extract模式的四种子流程调度。
"""

import os
import sys
import json
from typing import Any, Dict, List

# 注意：不需要添加sys.path，main.py已经设置了正确的Python搜索路径

from src.common import (
    create_folders, generate_report,  # noqa: E402, E501
    get_timestamp, save_report, contains_chinese_in_src, find_src_folders,
    decompile_jar, rename_mod_folders, restore_backup,
    setup_logger, get_logger, log_progress, log_result)  # noqa: E402, E501
from src.common.config_utils import get_directory  # noqa: E402
from src.extract_mode.extractor import extract_strings, save_extracted_strings

# 设置日志记录器
logger = setup_logger("extract_mode")


def _extract_strings_from_source(source_path: str, language: str, base_path: str, timestamp: str) -> Dict[str, Any]:
    """
    从指定源路径提取字符串
    
    Args:
        source_path: 源路径(src或jar文件夹)
        language: 语言类型(Chinese或English)
        base_path: 基础路径
        timestamp: 时间戳
    
    Returns:
        Dict[str, Any]: 提取结果，包含output_path
    """
    # 获取mod文件夹
    mod_folder = os.path.dirname(source_path)
    
    # 从mod_info.json读取name和version字段，构建正确的mod_name
    mod_info_path = os.path.join(mod_folder, "mod_info.json")
    mod_name = os.path.basename(mod_folder)  # 默认使用文件夹名
    version = "unknown"
    if os.path.exists(mod_info_path):
        try:
            with open(mod_info_path, 'r', encoding='utf-8') as f:
                mod_info = json.load(f)
                mod_name = mod_info.get("name", mod_name)
                version = mod_info.get("version", "unknown")
                # 按照文档要求，mod_name应为name+version
                mod_name = f"{mod_name} {version}"
        except Exception as e:
            print(f"[WARN]  读取mod_info.json失败: {mod_info_path} - {e}")
    
    # 提取AST映射
    from src.common.tree_sitter_utils import extract_ast_mappings
    ast_mappings = extract_ast_mappings(source_path)
    
    if not ast_mappings:
        return {
            "success": False,
            "data": {
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": ["未提取到任何字符串"],
            }
        }
    
    # 生成初始YAML映射，包含未映射标记
    from src.common.yaml_utils import generate_initial_yaml_mappings, save_yaml_mappings
    yaml_mappings = generate_initial_yaml_mappings(ast_mappings, mark_unmapped=True)
    
    # 构建输出文件夹路径(符合框架要求): Localization_File/output/Extract_English/mod_name/
    from src.common.config_utils import get_directory
    mod_root = get_directory("mod_root")
    output_path = os.path.join(mod_root, "output", f"Extract_{language}", mod_name)
    os.makedirs(output_path, exist_ok=True)
    
    # 保存YAML映射
    yaml_file_path = os.path.join(output_path, f"{language}_mappings.yaml")
    if not save_yaml_mappings(yaml_mappings, yaml_file_path):
        return {
            "success": False,
            "data": {
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": ["保存YAML映射失败"],
            }
        }
    
    # 同时保存为JSON格式，保持向后兼容
    json_file_path = os.path.join(output_path, f"{language}_mappings.json")
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(yaml_mappings, f, ensure_ascii=False, indent=2)
    
    # 复制mod_info.json到输出文件夹
    if os.path.exists(mod_info_path):
        import shutil
        shutil.copy(mod_info_path, os.path.join(output_path, "mod_info.json"))
    
    # 生成映射规则文件到rule文件夹
    generate_mapping_rules(yaml_mappings, base_path, language, mod_name, version, timestamp)
    
    # 提取结果统计
    extracted_result = {
        "total_count": len(ast_mappings),
        "success_count": len(yaml_mappings),
        "fail_count": 0,
        "fail_reasons": [],
        "unmapped_count": sum(1 for m in yaml_mappings if m["status"] == "unmapped"),
        "output_path": output_path
    }
    
    return {
        "success": True,
        "data": extracted_result
    }


def _process_extract_flow(language: str, base_path: str, timestamp: str, report: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理提取流程
    
    Args:
        language: 语言类型(Chinese或English)
        base_path: 基础路径
        timestamp: 时间戳
        report: 报告
    
    Returns:
        Dict[str, Any]: 处理结果
    """
    try:
        # 1. 构建语言文件路径
        from src.common.config_utils import get_source_directory
        source_dir = get_source_directory("extract", "auto")
        if not source_dir:
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": [f"无法获取源目录"],
                },
            )
        language_file_path = os.path.join(source_dir, language)
        if not os.path.exists(language_file_path):
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": [f"{language}文件目录不存在: {language_file_path}"],
                },
            )
        
        # 2. 重命名模组文件夹
        print("[NOTE] 开始重命名模组文件夹...")
        rename_mod_folders(language_file_path)
        
        # 3. 重命名备份文件夹
        print("[NOTE] 开始重命名备份文件夹...")
        from src.common.config_utils import get_backup_directory
        backup_dir = get_backup_directory("extract")
        backup_language_file_path = os.path.join(backup_dir, language)
        rename_mod_folders(backup_language_file_path)
        
        # 4. 恢复备份
        print("[NOTE] 开始恢复备份...")
        from src.common.config_utils import get_backup_directory
        backup_path = get_backup_directory("extract")
        restore_backup(backup_path, source_dir)
        
        # 4. 查找src文件夹
        src_folders = find_src_folders(language_file_path)
        
        # 5. 检测src文件夹是否包含目标语言内容
        extract_source = None
        has_target_language = False
        
        if src_folders:
            # 使用第一个找到的src文件夹
            src_folder = src_folders[0]
            # 获取包含src文件夹的模组文件夹
            extract_source = os.path.dirname(src_folder)
            print(f"[SEARCH] 找到 {len(src_folders)} 个src文件夹，将使用第一个进行提取：{src_folder}")
            print(f"[INFO] 使用模组文件夹作为提取源：{extract_source}")
            
            # 检测是否包含目标语言内容
            if language == "Chinese":
                has_target_language = contains_chinese_in_src(src_folder)
                if has_target_language:
                    print("[OK] 验证通过：src文件夹包含中文内容")
                else:
                    print("[WARN] src文件夹不包含中文内容")
            else:  # English
                # 对于英文，我们假设所有内容都是英文，所以直接提取
                has_target_language = True
                print("OK 验证通过：src文件夹包含英文内容")
        
        # 6. 多场景并行处理：处理所有找到的mod文件夹
        # 收集所有mod文件夹
        mod_folders = []
        for root, dirs, files in os.walk(language_file_path):
            # 检查是否是mod文件夹(包含src文件夹或mod_info.json)
            if os.path.basename(root) in ["src", "jar"]:
                continue
            
            # 检查是否包含src文件夹或mod_info.json
            has_src = "src" in dirs
            has_mod_info = "mod_info.json" in files
            has_src_in_subdirs = any(os.path.isdir(os.path.join(root, d)) and os.path.basename(os.path.join(root, d)) == "src" for d in dirs)
            
            # 如果包含src文件夹，或者包含mod_info.json，或者是直接的mod文件夹
            if has_src or has_mod_info or has_src_in_subdirs:
                mod_folders.append(root)
        
        if not mod_folders:
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["未找到可处理的mod文件夹"],
                },
            )
        
        # 处理每个mod文件夹
        results = []
        for mod_folder in mod_folders:
            print(f"\n[INFO] 处理mod文件夹: {os.path.basename(mod_folder)}")
            
            # 场景1：检查是否存在src文件夹
            src_folder = os.path.join(mod_folder, "src")
            has_src = os.path.exists(src_folder)
            
            # 场景2：检查是否存在jar文件
            jar_files = []
            for file in os.listdir(mod_folder):
                if file.endswith('.jar'):
                    jar_files.append(os.path.join(mod_folder, file))
            
            current_extract_source = None
            current_extraction_path = None
            current_has_target = False
            
            # 优先处理src文件夹
            if has_src:
                print(f"[INFO] 场景1：检测到src文件夹，直接提取")
                current_extract_source = mod_folder
                current_extraction_path = src_folder
                
                # 检测是否包含目标语言内容
                if language == "Chinese":
                    current_has_target = contains_chinese_in_src(src_folder)
                    if current_has_target:
                        print(f"[OK] 验证通过：src文件夹包含中文内容")
                    else:
                        print(f"[WARN] src文件夹不包含中文内容，将处理JAR文件")
                else:  # English
                    current_has_target = True
                    print(f"[OK] 验证通过：src文件夹包含英文内容")
            
            # 如果src文件夹不存在或不包含目标语言内容，处理JAR文件
            if not current_has_target or not has_src:
                print(f"[INFO] 场景2：处理JAR文件")
                
                if not jar_files:
                    print(f"[WARN] 未找到JAR文件，跳过该mod文件夹")
                    continue
                
                # 创建jar文件夹
                jar_dir = os.path.join(mod_folder, "jar")
                os.makedirs(jar_dir, exist_ok=True)
                print(f"[DIR] 在 {os.path.basename(mod_folder)} 下创建jar文件夹: {jar_dir}")
                
                # 反编译所有JAR文件
                for jar_file in jar_files:
                    print(f"[INFO] 反编译JAR文件: {os.path.basename(jar_file)}")
                    decompile_jar(jar_file, jar_dir)
                
                # 检测jar文件夹是否包含目标语言内容
                current_extract_source = mod_folder
                current_extraction_path = jar_dir
                
                if language == "Chinese":
                    current_has_target = contains_chinese_in_src(jar_dir)
                    if current_has_target:
                        print(f"[OK] 验证通过：{os.path.basename(jar_dir)} 包含中文内容")
                    else:
                        print(f"[WARN] jar文件夹不包含中文内容，跳过该mod文件夹")
                        continue
                else:  # English
                    current_has_target = True
                    print(f"[OK] 验证通过：{os.path.basename(jar_dir)} 包含英文内容")
            
            # 从提取源提取字符串
            if current_extract_source and current_extraction_path and current_has_target:
                extract_result = _extract_strings_from_source(current_extraction_path, language, base_path, timestamp)
                if extract_result["success"]:
                    results.append(extract_result["data"])
                    
                    # 将源文件夹移动到Complete目录
                    # 使用正确的Localization_File路径（与Localization_Tool同级）
                    localization_file_path = os.path.join(os.path.dirname(base_path), "Localization_File")
                    complete_path = os.path.join(localization_file_path, "output", "Extract_Complete")
                    from src.common.file_utils import move_to_complete
                    move_to_complete(current_extract_source, complete_path, language, timestamp)
                else:
                    results.append(extract_result["data"])
        
        # 汇总结果
        if not results:
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": len(mod_folders),
                    "fail_reasons": ["所有mod文件夹处理失败"],
                },
            )
        
        # 合并结果
        total_count = sum(r["total_count"] for r in results if "total_count" in r)
        success_count = sum(r["success_count"] for r in results if "success_count" in r)
        fail_count = sum(r["fail_count"] for r in results if "fail_count" in r)
        fail_reasons = [reason for r in results for reason in (r["fail_reasons"] if "fail_reasons" in r else [])]
        
        # 7. 更新报告
        report = generate_report(
            process_id=report["process_id"],
            mode="Extract",
            sub_flow=report["sub_flow"],
            status="success",
            data={
                "total_count": total_count,
                "success_count": success_count,
                "fail_count": fail_count,
                "fail_reasons": list(set(fail_reasons)),
            },
        )
        
        # 添加mode和language字段到report对象
        report["mode"] = "Extract"
        report["language"] = language
        
        # 添加output_path字段到report对象
        if results:
            # 如果有多个结果，使用第一个结果的output_path
            report["output_path"] = results[0].get("output_path", "")
        
        print(f"\nOK {language}提取完成，共处理 {total_count} 个文件")
        
        return report
        
        # 单mod处理逻辑(保留作为备用)
        # if not extract_source or not has_target_language:
        #     print("[PROCESS] 开始处理JAR文件...")
        #     
        #     # 查找JAR文件
        #     jar_files = []
        #     for root, dirs, files in os.walk(language_file_path):
        #         for file in files:
        #             if file.endswith('.jar'):
        #                 jar_files.append(os.path.join(root, file))
        #     
        #     if not jar_files:
        #         return generate_report(
        #             process_id=report["process_id"],
        #             mode="Extract",
        #             sub_flow=report["sub_flow"],
        #             status="fail",
        #             data={
        #                 "total_count": 0,
        #                 "success_count": 0,
        #                 "fail_count": 1,
        #                 "fail_reasons": ["未找到src文件夹或JAR文件"],
        #             },
        #         )
        #     
        #     # 反编译JAR文件
        #     print(f"[SEARCH] 找到 {len(jar_files)} 个JAR文件，将进行反编译")
        #     for jar_file in jar_files:
        #         # 获取mod文件夹路径(JAR文件所在目录)
        #         mod_dir = os.path.dirname(jar_file)
        #         # 创建jar文件夹
        #         jar_dir = os.path.join(mod_dir, "jar")
        #         os.makedirs(jar_dir, exist_ok=True)
        #         print(f"[DIR] 在 {os.path.basename(mod_dir)} 下创建jar文件夹: {jar_dir}")
        #         # 调用JAR反编译函数
        #         decompile_jar(jar_file, jar_dir)
        #     
        #     # 查找jar文件夹作为提取源
        #     jar_folders = []
        #     for root, dirs, files in os.walk(language_file_path):
        #         for dir_name in dirs:
        #             if dir_name == "jar":
        #                 jar_folders.append(os.path.join(root, dir_name))
        #     
        #     if not jar_folders:
        #         return generate_report(
        #             process_id=report["process_id"],
        #             mode="Extract",
        #             sub_flow=report["sub_flow"],
        #             status="fail",
        #             data={
        #                 "total_count": 0,
        #                 "success_count": 0,
        #                 "fail_count": 1,
        #                 "fail_reasons": ["未找到jar文件夹，JAR反编译可能失败"],
        #             },
        #         )
        #     
        #     jar_folder = jar_folders[0]
        #     # 使用包含jar文件夹的模组文件夹作为提取源
        #     extract_source = os.path.dirname(jar_folder)
        #     print(f"[LIST] 找到jar文件夹，将用于提取: {os.path.basename(jar_folder)}")
        #     print(f"[INFO] 使用模组文件夹作为提取源：{extract_source}")
        #     
        #     # 检测jar文件夹是否包含目标语言内容
        #     if language == "Chinese":
        #         has_target_language = contains_chinese_in_src(jar_folder)
        #         if not has_target_language:
        #             return generate_report(
        #                 process_id=report["process_id"],
        #                 mode="Extract",
        #                 sub_flow=report["sub_flow"],
        #                 status="fail",
        #                 data={
        #                     "total_count": 0,
        #                     "success_count": 0,
        #                     "fail_count": 1,
        #                     "fail_reasons": ["jar文件夹不包含中文"],
        #                 },
        #             )
        #         print(f"OK 验证通过：{os.path.basename(jar_folder)} 包含中文内容")
        
        # # 7. 从提取源提取字符串
        # # 如果是src文件夹情况，使用src_folder进行提取
        # # 如果是jar文件夹情况，使用jar_folder进行提取
        # extraction_path = src_folder if 'src_folder' in locals() else jar_folder
        # extract_result = _extract_strings_from_source(extraction_path, language, base_path, timestamp)
        # if not extract_result["success"]:
        #     return generate_report(
        #         process_id=report["process_id"],
        #         mode="Extract",
        #         sub_flow=report["sub_flow"],
        #         status="fail",
        #         data=extract_result["data"],
        #     )
        # 
        # # 8. 将源文件夹移动到Complete目录
        # complete_path = os.path.join(base_path, "project", "Extract", "Complete")
        # from src.common.file_utils import move_to_complete
        # move_to_complete(extract_source, complete_path, language, timestamp)
        # 
        # # 9. 更新报告
        # report = generate_report(
        #     process_id=report["process_id"],
        #     mode="Extract",
        #     sub_flow=report["sub_flow"],
        #     status="success",
        #     data=extract_result["data"],
        # )
        # 
        # print(f"OK {language}提取完成，共处理 {extract_result['data']['total_count']} 个文件")
        # 
        # return report
    except Exception as e:
        print(f"[ERROR] 处理{language}提取流程失败: {str(e)}")
        return generate_report(
            process_id=report["process_id"],
            mode="Extract",
            sub_flow=report["sub_flow"],
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"处理失败: {str(e)}"],
            },
        )


def generate_mapping_rules(yaml_mappings: List[Dict[str, Any]], base_path: str, language: str, mod_name: str, version: str, timestamp: str) -> None:
    """
    生成映射规则文件并保存到rule文件夹
    
    Args:
        yaml_mappings: 映射规则列表
        base_path: 基础路径
        language: 语言类型
        mod_name: 模组名称(从mod_info.json中提取的name+version)
        version: 版本号
        timestamp: 时间戳
    """
    from src.common.yaml_utils import save_yaml_mappings
    import os
    
    # 创建rule文件夹路径(在Localization_File目录下，符合框架要求) - 使用mod_root配置
    from src.common.config_utils import get_directory
    mod_root = get_directory("mod_root")
    rule_path = os.path.join(mod_root, "rule", language, mod_name)
    os.makedirs(rule_path, exist_ok=True)
    
    # 生成规则文件名(简化文件名，符合框架要求)
    rule_filename = f"{language}_mappings.yaml"
    rule_filepath = os.path.join(rule_path, rule_filename)
    
    # 同时保存为JSON格式
    json_filename = f"{language}_mappings.json"
    json_filepath = os.path.join(rule_path, json_filename)
    
    # 保存映射规则到rule文件夹
    if save_yaml_mappings(yaml_mappings, rule_filepath):
        print(f"[OK] 映射规则文件已生成到: {rule_filepath}")
        print(f"[INFO] 规则文件包含 {len(yaml_mappings)} 个条目，其中 {sum(1 for m in yaml_mappings if m['status'] == 'unmapped')} 个未映射")
    else:
        print(f"[ERROR] 保存YAML映射规则文件失败: {rule_filepath}")
    
    # 保存为JSON格式
    import json
    try:
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(yaml_mappings, f, ensure_ascii=False, indent=2)
        print(f"[OK] JSON映射规则文件已生成到: {json_filepath}")
    except Exception as e:
        print(f"[ERROR] 保存JSON映射规则文件失败: {json_filepath} - {e}")


def run_extract_sub_flow(sub_flow: str, base_path: str = None) -> Dict[str, Any]:
    """
    执行Extract指定子流程

    Args:
        sub_flow: 子流程类型，可选值：
            - 已有英文src文件夹提取流程
            - 没有英文src文件夹提取流程
            - 已有中文src文件夹提取流程
            - 没有中文src文件夹提取流程
            - 英文提取流程(兼容旧版)
            - 中文提取流程(兼容旧版)
        base_path: 基础路径，默认从配置获取

    Returns:
        Dict[str, Any]: 执行结果，包含output_path、mode和language
    """
    # 如果没有提供base_path，从配置中获取
    if base_path is None:
        # 使用当前脚本的项目根目录作为默认值
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 获取时间戳
    timestamp = get_timestamp()
    process_id = f"{timestamp}_extract"

    # 生成初始报告
    report = generate_report(
        process_id=process_id,
        mode="Extract",
        sub_flow=sub_flow,
        status="running",
        data={
            "total_count": 0,
            "success_count": 0,
            "fail_count": 0,
            "fail_reasons": [],
        },
    )

    try:
        # 1. 创建必要的文件夹
        if not create_folders(base_path, "Extract"):
            report = generate_report(
                process_id=process_id,
                mode="Extract",
                sub_flow=sub_flow,
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["创建文件夹失败"],
                },
            )
            # 使用新路径保存报告
            report_path = os.path.join(base_path, "Localization_File", "output", "Extract", "Report")
            save_report(
                report,
                report_path,
                timestamp,
            )
            return report

        # 2. 根据子流程类型执行不同的逻辑
        if sub_flow in ["已有英文src文件夹提取流程", "没有英文src文件夹提取流程", "英文提取流程"]:
            # 英文相关流程
            language = "English"
            if sub_flow == "已有英文src文件夹提取流程":
                result = _process_existing_english_src(base_path, timestamp, report)
            elif sub_flow == "没有英文src文件夹提取流程":
                result = _process_no_english_src(base_path, timestamp, report)
            else:  # 英文提取流程
                result = _process_extract_flow("English", base_path, timestamp, report)
        elif sub_flow in ["已有中文src文件夹提取流程", "没有中文src文件夹提取流程", "中文提取流程"]:
            # 中文相关流程
            language = "Chinese"
            if sub_flow == "已有中文src文件夹提取流程":
                result = _process_existing_chinese_src(base_path, timestamp, report)
            elif sub_flow == "没有中文src文件夹提取流程":
                result = _process_no_chinese_src(base_path, timestamp, report)
            else:  # 中文提取流程
                result = _process_extract_flow("Chinese", base_path, timestamp, report)
        else:
            # 未知子流程
            report = generate_report(
                process_id=process_id,
                mode="Extract",
                sub_flow=sub_flow,
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": [f"未知子流程: {sub_flow}"],
                },
            )
            # 使用新路径保存报告
            report_path = os.path.join(base_path, "Localization_File", "output", "Extract", "Report")
            save_report(
                report,
                report_path,
                timestamp,
            )
            return report
        
        # 3. 添加mode和language到结果中，以便main函数调用show_output_guide
        result["mode"] = "Extract"
        result["language"] = language
        
        # 4. 如果结果中没有output_path，尝试从data中获取
        if "output_path" not in result:
            result["output_path"] = result.get("data", {}).get("output_path", "")

        # 使用新路径保存报告
        new_report_path = os.path.join(base_path, "Localization_File", "output", "Extract", "Report")
        save_report(
            result, new_report_path, timestamp
        )
        
        # 4. 同时将报告保存到框架要求的output_path中
        if result.get("output_path"):
            # 生成报告文件名
            report_filename = f"extract_{timestamp}_report.json"
            report_filepath = os.path.join(result["output_path"], report_filename)
            
            # 保存报告到output_path
            with open(report_filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"[OK] 流程报告已生成到: {report_filepath}")

        return result
    except Exception as e:
        # 处理异常
        report = generate_report(
            process_id=process_id,
            mode="Extract",
            sub_flow=sub_flow,
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"执行过程中发生异常: {str(e)}"],
            },
        )
        # 使用新路径保存报告
        report_path = os.path.join(base_path, "Localization_File", "output", "Extract", "Report")
        save_report(
            report, report_path, timestamp
        )
        return report


def _process_existing_english_src(
    base_path: str, timestamp: str, report: Dict[str, Any]
) -> Dict[str, Any]:
    """
    处理已有英文src文件夹提取流程

    Args:
        base_path: 基础路径
        timestamp: 时间戳
        report: 报告

    Returns:
        Dict[str, Any]: 处理结果
    """
    try:
        # 1. 输入验证
        if not isinstance(base_path, str) or not os.path.exists(base_path):
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["无效的基础路径"],
                },
            )

        # 2. 英文文件路径构建
        english_file_path = os.path.join(base_path, "project", "Extract", "File", "English")
        if not os.path.exists(english_file_path):
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["English文件目录不存在"],
                },
            )
        
        # 3. 重命名模组文件夹
        print("[NOTE] 开始重命名模组文件夹...")
        rename_mod_folders(english_file_path)
        
        # 4. 重命名备份文件夹
        print("[NOTE] 开始重命名备份文件夹...")
        backup_english_file_path = os.path.join(base_path, "project", "Extract", "File_backup", "English")
        rename_mod_folders(backup_english_file_path)
        
        # 5. 恢复备份
        print("[NOTE] 开始恢复备份...")
        backup_path = os.path.join(base_path, "project", "Extract", "File_backup")
        restore_backup(backup_path, os.path.join(base_path, "project", "Extract", "File"))
        
        # 5. 查找src文件夹
        src_folders = find_src_folders(english_file_path)
        if not src_folders:
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["未找到src文件夹"],
                },
            )
        
        print(f"[SEARCH] 找到 {len(src_folders)} 个src文件夹，将使用第一个进行提取")
        
        # 6. 获取mod文件夹信息
        src_folder = src_folders[0]
        # 使用mod文件夹作为提取源，而不是src文件夹本身
        extract_source = os.path.dirname(src_folder)
        mod_folder = extract_source
        mod_folder_name = os.path.basename(mod_folder)
        
        # 读取mod_info.json获取版本号
        mod_info_path = os.path.join(mod_folder, "mod_info.json")
        version = "unknown"
        if os.path.exists(mod_info_path):
            try:
                with open(mod_info_path, 'r', encoding='utf-8') as f:
                    mod_info = json.load(f)
                    version = mod_info.get("version", "unknown")
            except Exception as e:
                print(f"[WARN]  读取mod_info.json失败: {mod_info_path} - {e}")
        
        # 8. 提取字符串(使用第一个找到的src文件夹)
        extracted_data = extract_strings(src_folder, "English", base_path)
        if not extracted_data or "metadata" not in extracted_data:
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["字符串提取失败"],
                },
            )
        
        # 8. 保存提取的字符串到规则文件
        strings_output_path = os.path.join(base_path, "project", "Extract", "Strings", "English")
        if not save_extracted_strings(extracted_data, strings_output_path, "English", mod_folder_name=mod_folder_name, version=version, timestamp=timestamp):
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["保存提取的字符串失败"],
                },
            )
        
        # 8. 提取结果统计
        extracted_result = {
            "total_count": extracted_data["metadata"]["total_count"],
            "success_count": extracted_data["metadata"]["success_count"],
            "fail_count": extracted_data["metadata"]["fail_count"],
            "fail_reasons": extracted_data["metadata"]["fail_reasons"],
        }

        # 9. 将源文件夹移动到Complete目录
        complete_path = os.path.join(base_path, "project", "Extract", "Complete")
        from src.common.file_utils import move_to_complete
        move_to_complete(extract_source, complete_path, "English", timestamp)
        
        # 10. 更新报告
        report = generate_report(
            process_id=report["process_id"],
            mode="Extract",
            sub_flow=report["sub_flow"],
            status="success",
            data=extracted_result,
        )
        
        print(f"OK 已有英文src文件夹提取完成，共处理 {extracted_result['total_count']} 个文件")
        
        return report
    except Exception as e:
        print(f"[ERROR] 处理已有英文src文件夹失败: {str(e)}")
        return generate_report(
            process_id=report["process_id"],
            mode="Extract",
            sub_flow=report["sub_flow"],
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"处理失败: {str(e)}"],
            },
        )


def _process_no_english_src(
    base_path: str, timestamp: str, report: Dict[str, Any]
) -> Dict[str, Any]:
    """
    处理没有英文src文件夹提取流程

    Args:
        base_path: 基础路径
        timestamp: 时间戳
        report: 报告

    Returns:
        Dict[str, Any]: 处理结果
    """
    try:
        # 1. 输入验证
        if not isinstance(base_path, str) or not os.path.exists(base_path):
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["无效的基础路径"],
                },
            )

        # 2. 英文文件路径构建
        english_file_path = os.path.join(base_path, "project", "Extract", "File", "English")
        if not os.path.exists(english_file_path):
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["English文件目录不存在"],
                },
            )
        
        # 3. 重命名模组文件夹
        print("[NOTE] 开始重命名模组文件夹...")
        rename_mod_folders(english_file_path)
        
        # 4. 重命名备份文件夹
        print("[NOTE] 开始重命名备份文件夹...")
        backup_english_file_path = os.path.join(base_path, "project", "Extract", "File_backup", "English")
        rename_mod_folders(backup_english_file_path)
        
        # 5. 恢复备份
        print("[NOTE] 开始恢复备份...")
        backup_path = os.path.join(base_path, "project", "Extract", "File_backup")
        restore_backup(backup_path, os.path.join(base_path, "project", "Extract", "File"))
        
        # 5. 查找JAR文件
        jar_files = []
        for root, dirs, files in os.walk(english_file_path):
            for file in files:
                if file.endswith('.jar'):
                    jar_files.append(os.path.join(root, file))
        
        if jar_files:
            # 6. 在mod文件夹下创建jar文件夹并反编译
            print(f"[SEARCH] 找到 {len(jar_files)} 个JAR文件，将进行反编译")
            for jar_file in jar_files:
                # 获取mod文件夹路径(JAR文件所在目录)
                mod_dir = os.path.dirname(jar_file)
                # 创建jar文件夹
                jar_dir = os.path.join(mod_dir, "jar")
                os.makedirs(jar_dir, exist_ok=True)
                print(f"[DIR] 在 {os.path.basename(mod_dir)} 下创建jar文件夹: {jar_dir}")
                # 调用JAR反编译函数
                decompile_jar(jar_file, jar_dir)
        
        # 7. 查找可用的提取源(src或jar文件夹)
        extract_source = None
        extraction_path = None
        
        # 先查找src文件夹(包括可能反编译生成的)
        src_folders = find_src_folders(english_file_path)
        if src_folders:
            src_folder = src_folders[0]
            # 使用包含src文件夹的模组文件夹作为提取源
            extract_source = os.path.dirname(src_folder)
            extraction_path = src_folder
            print(f"[LIST] 找到src文件夹，将用于提取: {os.path.basename(src_folder)}")
            print(f"[INFO] 使用模组文件夹作为提取源：{extract_source}")
        else:
            # 如果没有src文件夹，查找jar文件夹
            jar_folders = []
            for root, dirs, files in os.walk(english_file_path):
                for dir_name in dirs:
                    if dir_name == "jar":
                        jar_folders.append(os.path.join(root, dir_name))
            
            if jar_folders:
                jar_folder = jar_folders[0]
                # 使用包含jar文件夹的模组文件夹作为提取源
                extract_source = os.path.dirname(jar_folder)
                extraction_path = jar_folder
                print(f"[LIST] 找到jar文件夹，将用于提取: {os.path.basename(jar_folder)}")
                print(f"[INFO] 使用模组文件夹作为提取源：{extract_source}")
            else:
                return generate_report(
                    process_id=report["process_id"],
                    mode="Extract",
                    sub_flow=report["sub_flow"],
                    status="fail",
                    data={
                        "total_count": 0,
                        "success_count": 0,
                        "fail_count": 1,
                        "fail_reasons": ["未找到src文件夹或jar文件夹，JAR反编译可能失败"],
                    },
                )
        
        # 8. 获取mod文件夹信息
        mod_folder = extract_source
        mod_folder_name = os.path.basename(mod_folder)
        
        # 读取mod_info.json获取版本号
        mod_info_path = os.path.join(mod_folder, "mod_info.json")
        version = "unknown"
        if os.path.exists(mod_info_path):
            try:
                with open(mod_info_path, 'r', encoding='utf-8') as f:
                    mod_info = json.load(f)
                    version = mod_info.get("version", "unknown")
            except Exception as e:
                print(f"[WARN]  读取mod_info.json失败: {mod_info_path} - {e}")
        
        # 9. 提取字符串
        extracted_data = extract_strings(extraction_path, "English", base_path)
        if not extracted_data or "metadata" not in extracted_data:
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["字符串提取失败"],
                },
            )
        
        # 10. 保存提取的字符串
        strings_output_path = os.path.join(base_path, "project", "Extract", "Strings", "English")
        if not save_extracted_strings(extracted_data, strings_output_path, "English", mod_folder_name=mod_folder_name, version=version, timestamp=timestamp):
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["保存提取的字符串失败"],
                },
            )
        
        # 10. 提取结果统计
        extracted_result = {
            "total_count": extracted_data["metadata"]["total_count"],
            "success_count": extracted_data["metadata"]["success_count"],
            "fail_count": extracted_data["metadata"]["fail_count"],
            "fail_reasons": extracted_data["metadata"]["fail_reasons"],
        }

        # 11. 将源文件夹移动到Complete目录
        complete_path = os.path.join(base_path, "project", "Extract", "Complete")
        from src.common.file_utils import move_to_complete
        move_to_complete(extract_source, complete_path, "English", timestamp)
        
        # 12. 更新报告
        decompile_info = None
        if jar_files:
            decompile_info = {
                "jar_path": (", ".join([os.path.basename(f) for f in jar_files[:3]]) +
                              ("..." if len(jar_files) > 3 else "")),
                "status": "success",
                "count": len(jar_files)
            }

        report = generate_report(
            process_id=report["process_id"],
            mode="Extract",
            sub_flow=report["sub_flow"],
            status="success",
            data=extracted_result,
            decompile=decompile_info
        )
        
        print(f"OK 没有英文src文件夹提取完成，共处理 {extracted_result['total_count']} 个文件")
        
        return report
    except Exception as e:
        print(f"[ERROR] 处理没有英文src文件夹失败: {str(e)}")
        return generate_report(
            process_id=report["process_id"],
            mode="Extract",
            sub_flow=report["sub_flow"],
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"处理失败: {str(e)}"],
            },
        )


def _process_existing_chinese_src(
    base_path: str, timestamp: str, report: Dict[str, Any]
) -> Dict[str, Any]:
    """
    处理已有中文src文件夹提取流程

    Args:
        base_path: 基础路径
        timestamp: 时间戳
        report: 报告

    Returns:
        Dict[str, Any]: 处理结果
    """
    try:
        # 1. 输入验证
        if not isinstance(base_path, str) or not os.path.exists(base_path):
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["无效的基础路径"],
                },
            )

        # 2. 中文文件路径构建
        chinese_file_path = os.path.join(base_path, "project", "Extract", "File", "Chinese")
        if not os.path.exists(chinese_file_path):
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["Chinese文件目录不存在"],
                },
            )
        
        # 3. 重命名模组文件夹
        print("[NOTE] 开始重命名模组文件夹...")
        rename_mod_folders(chinese_file_path)
        
        # 4. 重命名备份文件夹
        print("[NOTE] 开始重命名备份文件夹...")
        backup_chinese_file_path = os.path.join(base_path, "project", "Extract", "File_backup", "Chinese")
        rename_mod_folders(backup_chinese_file_path)
        
        # 5. 恢复备份
        print("[NOTE] 开始恢复备份...")
        backup_path = os.path.join(base_path, "project", "Extract", "File_backup")
        restore_backup(backup_path, os.path.join(base_path, "project", "Extract", "File"))
        
        # 5. 查找src文件夹
        src_folders = find_src_folders(chinese_file_path)
        if not src_folders:
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["未找到src文件夹"],
                },
            )
        
        print(f"[SEARCH] 找到 {len(src_folders)} 个src文件夹，将使用第一个进行提取")
        
        # 6. 检查src文件夹是否包含中文
        target_src_folder = src_folders[0]
        has_chinese = contains_chinese_in_src(target_src_folder)
        if not has_chinese:
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["src文件夹不包含中文"],
                },
            )
        
        print("OK 验证通过：src文件夹包含中文内容")
        
        # 7. 获取mod文件夹信息
        mod_folder = os.path.dirname(target_src_folder)
        mod_folder_name = os.path.basename(mod_folder)
        # 使用mod文件夹作为提取源，而不是src文件夹本身
        extract_source = mod_folder
        
        # 读取mod_info.json获取版本号
        mod_info_path = os.path.join(mod_folder, "mod_info.json")
        version = "unknown"
        if os.path.exists(mod_info_path):
            try:
                with open(mod_info_path, 'r', encoding='utf-8') as f:
                    mod_info = json.load(f)
                    version = mod_info.get("version", "unknown")
            except Exception as e:
                print(f"[WARN]  读取mod_info.json失败: {mod_info_path} - {e}")
        
        # 8. 提取字符串
        extracted_data = extract_strings(target_src_folder, "Chinese", base_path)
        if not extracted_data or "metadata" not in extracted_data:
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["字符串提取失败"],
                },
            )
        
        # 9. 保存提取的字符串到规则文件
        strings_output_path = os.path.join(base_path, "project", "Extract", "Strings", "Chinese")
        if not save_extracted_strings(extracted_data, strings_output_path, "Chinese", mod_folder_name=mod_folder_name, version=version, timestamp=timestamp):
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["保存提取的字符串失败"],
                },
            )
        
        # 9. 提取结果统计
        extracted_result = {
            "total_count": extracted_data["metadata"]["total_count"],
            "success_count": extracted_data["metadata"]["success_count"],
            "fail_count": extracted_data["metadata"]["fail_count"],
            "fail_reasons": extracted_data["metadata"]["fail_reasons"],
        }

        # 10. 将源文件夹移动到Complete目录
        complete_path = os.path.join(base_path, "project", "Extract", "Complete")
        from src.common.file_utils import move_to_complete
        move_to_complete(extract_source, complete_path, "Chinese", timestamp)
        
        # 11. 更新报告
        report = generate_report(
            process_id=report["process_id"],
            mode="Extract",
            sub_flow=report["sub_flow"],
            status="success",
            data=extracted_result,
        )
        
        print(f"OK 已有中文src文件夹提取完成，共处理 {extracted_result['total_count']} 个文件")
        
        return report
    except Exception as e:
        print(f"[ERROR] 处理已有中文src文件夹失败: {str(e)}")
        return generate_report(
            process_id=report["process_id"],
            mode="Extract",
            sub_flow=report["sub_flow"],
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"处理失败: {str(e)}"],
            },
        )


def _process_no_chinese_src(
    base_path: str, timestamp: str, report: Dict[str, Any]
) -> Dict[str, Any]:
    """
    处理没有中文src文件夹提取流程

    Args:
        base_path: 基础路径
        timestamp: 时间戳
        report: 报告

    Returns:
        Dict[str, Any]: 处理结果
    """
    try:
        # 1. 输入验证
        if not isinstance(base_path, str) or not os.path.exists(base_path):
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["无效的基础路径"],
                },
            )

        # 2. 中文文件路径构建
        chinese_file_path = os.path.join(base_path, "project", "Extract", "File", "Chinese")
        if not os.path.exists(chinese_file_path):
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["Chinese文件目录不存在"],
                },
            )
        
        # 3. 重命名模组文件夹
        print("[NOTE] 开始重命名模组文件夹...")
        rename_mod_folders(chinese_file_path)
        
        # 4. 重命名备份文件夹
        print("[NOTE] 开始重命名备份文件夹...")
        backup_chinese_file_path = os.path.join(base_path, "project", "Extract", "File_backup", "Chinese")
        rename_mod_folders(backup_chinese_file_path)
        
        # 5. 恢复备份
        print("[NOTE] 开始恢复备份...")
        backup_path = os.path.join(base_path, "project", "Extract", "File_backup")
        restore_backup(backup_path, os.path.join(base_path, "project", "Extract", "File"))
        
        # 5. 查找JAR文件
        jar_files = []
        for root, dirs, files in os.walk(chinese_file_path):
            for file in files:
                if file.endswith('.jar'):
                    jar_files.append(os.path.join(root, file))
        
        if jar_files:
            # 6. 在mod文件夹下创建jar文件夹并反编译
            print(f"[SEARCH] 找到 {len(jar_files)} 个JAR文件，将进行反编译")
            for jar_file in jar_files:
                # 获取mod文件夹路径(JAR文件所在目录)
                mod_dir = os.path.dirname(jar_file)
                # 创建jar文件夹
                jar_dir = os.path.join(mod_dir, "jar")
                os.makedirs(jar_dir, exist_ok=True)
                print(f"[DIR] 在 {os.path.basename(mod_dir)} 下创建jar文件夹: {jar_dir}")
                # 调用JAR反编译函数
                decompile_jar(jar_file, jar_dir)
        
        # 7. 查找可用的提取源(src或jar文件夹)
        extract_source = None
        extraction_path = None
        has_chinese = False
        
        # 先查找src文件夹(包括可能反编译生成的)
        src_folders = find_src_folders(chinese_file_path)
        if src_folders:
            src_folder = src_folders[0]
            # 使用包含src文件夹的模组文件夹作为提取源
            extract_source = os.path.dirname(src_folder)
            extraction_path = src_folder
            print(f"[LIST] 找到src文件夹，将用于提取: {os.path.basename(src_folder)}")
            print(f"[INFO] 使用模组文件夹作为提取源：{extract_source}")
            # 检查src文件夹是否包含中文
            has_chinese = contains_chinese_in_src(src_folder)
        else:
            # 如果没有src文件夹，查找jar文件夹
            jar_folders = []
            for root, dirs, files in os.walk(chinese_file_path):
                for dir_name in dirs:
                    if dir_name == "jar":
                        jar_folders.append(os.path.join(root, dir_name))
            
            if jar_folders:
                jar_folder = jar_folders[0]
                # 使用包含jar文件夹的模组文件夹作为提取源
                extract_source = os.path.dirname(jar_folder)
                extraction_path = jar_folder
                print(f"[LIST] 找到jar文件夹，将用于提取: {os.path.basename(jar_folder)}")
                print(f"[INFO] 使用模组文件夹作为提取源：{extract_source}")
                # 检查jar文件夹是否包含中文
                has_chinese = contains_chinese_in_src(jar_folder)
            else:
                return generate_report(
                    process_id=report["process_id"],
                    mode="Extract",
                    sub_flow=report["sub_flow"],
                    status="fail",
                    data={
                        "total_count": 0,
                        "success_count": 0,
                        "fail_count": 1,
                        "fail_reasons": ["未找到src文件夹或jar文件夹，JAR反编译可能失败"],
                    },
                )
        
        # 8. 验证提取源是否包含中文
        if not has_chinese:
            source_type = "src" if "src" in extraction_path else "jar"
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": [f"{source_type}文件夹不包含中文"],
                },
            )
        
        print(f"OK 验证通过：{os.path.basename(extraction_path)} 包含中文内容")
        
        # 9. 获取mod文件夹信息
        mod_folder = extract_source
        mod_folder_name = os.path.basename(mod_folder)
        
        # 读取mod_info.json获取版本号
        mod_info_path = os.path.join(mod_folder, "mod_info.json")
        version = "unknown"
        if os.path.exists(mod_info_path):
            try:
                with open(mod_info_path, 'r', encoding='utf-8') as f:
                    mod_info = json.load(f)
                    version = mod_info.get("version", "unknown")
            except Exception as e:
                print(f"[WARN]  读取mod_info.json失败: {mod_info_path} - {e}")
        
        # 10. 提取字符串
        extracted_data = extract_strings(extraction_path, "Chinese", base_path)
        if not extracted_data or "metadata" not in extracted_data:
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["字符串提取失败"],
                },
            )
        
        # 11. 保存提取的字符串
        strings_output_path = os.path.join(base_path, "project", "Extract", "Strings", "Chinese")
        if not save_extracted_strings(extracted_data, strings_output_path, "Chinese", mod_folder_name=mod_folder_name, version=version, timestamp=timestamp):
            return generate_report(
                process_id=report["process_id"],
                mode="Extract",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["保存提取的字符串失败"],
                },
            )
        
        # 11. 提取结果统计
        extracted_result = {
            "total_count": extracted_data["metadata"]["total_count"],
            "success_count": extracted_data["metadata"]["success_count"],
            "fail_count": extracted_data["metadata"]["fail_count"],
            "fail_reasons": extracted_data["metadata"]["fail_reasons"],
        }

        # 12. 将源文件夹移动到Complete目录
        complete_path = os.path.join(base_path, "project", "Extract", "Complete")
        from src.common.file_utils import move_to_complete
        move_to_complete(extract_source, complete_path, "Chinese", timestamp)
        
        # 13. 更新报告
        decompile_info = None
        if jar_files:
            decompile_info = {
                "jar_path": ", ".join([os.path.basename(f) for f in jar_files[:3]]) + ("..." if len(jar_files) > 3 else ""),
                "status": "success",
                "count": len(jar_files)
            }

        report = generate_report(
            process_id=report["process_id"],
            mode="Extract",
            sub_flow=report["sub_flow"],
            status="success",
            data=extracted_result,
            decompile=decompile_info
        )
        
        print(f"OK 没有中文src文件夹提取完成，共处理 {extracted_result['total_count']} 个文件")
        
        return report
    except Exception as e:
        print(f"[ERROR] 处理没有中文src文件夹失败: {str(e)}")
        return generate_report(
            process_id=report["process_id"],
            mode="Extract",
            sub_flow=report["sub_flow"],
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"处理失败: {str(e)}"],
            },
        )
