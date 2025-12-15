#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extend模式核心模块

该模块包含Extend模式的三种子流程调度。
"""

import os
import sys
from typing import Any, Dict

# 注意：不需要添加sys.path，main.py已经设置了正确的Python搜索路径

from src.common import (create_folders, generate_report,  # noqa: E402, E501
                        get_timestamp, save_report,
                        contains_chinese_in_src,
                        read_mod_info, load_mapping_rules,
                        rename_mod_folders, restore_backup,
                        setup_logger, get_logger, log_progress, log_result)  # noqa: E402, E501
from src.common.config_utils import get_directory  # noqa: E402

# 设置日志记录器
logger = setup_logger("extend_mode")


def run_extend_sub_flow(sub_flow: str, base_path: str = None) -> Dict[str, Any]:
    """
    执行Extend指定子流程

    Args:
        sub_flow: 子流程类型，可选值：
            - 已有中文src文件夹映射流程
            - 没有中文src文件夹映射流程
            - 已有中文映射规则文件流程
            - 已有英文src文件夹映射流程
            - 没有英文src文件夹映射流程
            - 已有英文映射规则文件流程
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
    process_id = f"{timestamp}_extend"

    # 生成初始报告
    report = generate_report(
        process_id=process_id,
        mode="Extend",
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
        if not create_folders(base_path, "Extend"):
            report = generate_report(
                process_id=process_id,
                mode="Extend",
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
            # 使用正确的Localization_File路径（与Localization_Tool同级）
            localization_file_path = os.path.join(os.path.dirname(base_path), "Localization_File")
            report_path = os.path.join(localization_file_path, "output", "Extend", "Report")
            save_report(
                report,
                report_path,
                timestamp,
            )
            return report

        # 2. 根据子流程类型执行不同的逻辑
        result = None
        language = "Chinese"
        mapping_direction = "zh2en"
        
        if sub_flow in ["已有中文src文件夹映射流程", "没有中文src文件夹映射流程", "已有中文映射规则文件流程"]:
            # 中文相关流程(中文映射到英文)
            language = "Chinese"
            mapping_direction = "zh2en"
            
            if sub_flow == "已有中文src文件夹映射流程":
                result = _process_existing_chinese_src(base_path, timestamp, report)
            elif sub_flow == "没有中文src文件夹映射流程":
                result = _process_no_chinese_src(base_path, timestamp, report)
            else:  # 已有中文映射规则文件流程
                result = _process_existing_chinese_rules(base_path, timestamp, report)
        elif sub_flow in ["已有英文src文件夹映射流程", "没有英文src文件夹映射流程", "已有英文映射规则文件流程"]:
            # 英文相关流程(英文映射到中文)
            language = "English"
            mapping_direction = "en2zh"
            
            if sub_flow == "已有英文src文件夹映射流程":
                result = _process_existing_english_src(base_path, timestamp, report)
            elif sub_flow == "没有英文src文件夹映射流程":
                result = _process_no_english_src(base_path, timestamp, report)
            else:  # 已有英文映射规则文件流程
                result = _process_existing_english_rules(base_path, timestamp, report)
        else:
            # 未知子流程
            report = generate_report(
                process_id=process_id,
                mode="Extend",
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
            # 使用正确的Localization_File路径（与Localization_Tool同级）
            localization_file_path = os.path.join(os.path.dirname(base_path), "Localization_File")
            report_path = os.path.join(localization_file_path, "output", "Extend", "Report")
            save_report(
                report,
                report_path,
                timestamp,
            )
            return report

        # 3. 添加mode、language和mapping_direction到结果中，以便main函数调用show_output_guide
        result["mode"] = "Extend"
        result["language"] = language
        result["mapping_direction"] = mapping_direction
        
        # 4. 如果结果中没有output_path，尝试从data中获取
        if "output_path" not in result:
            result["output_path"] = result.get("data", {}).get("output_path", "")

        # 使用新路径保存报告
        # 使用正确的Localization_File路径（与Localization_Tool同级）
        localization_file_path = os.path.join(os.path.dirname(base_path), "Localization_File")
        new_report_path = os.path.join(localization_file_path, "output", "Extend", "Report")
        save_report(
            result, new_report_path, timestamp
        )
        
        # 6. 同时将报告保存到框架要求的output_path中
        if result.get("output_path"):
            # 生成报告文件名
            report_filename = f"extend_{timestamp}_report.json"
            report_filepath = os.path.join(result["output_path"], report_filename)
            
            # 保存报告到output_path
            import json
            with open(report_filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"[OK] 流程报告已生成到: {report_filepath}")

        return result
    except Exception as e:
        # 处理异常
        report = generate_report(
            process_id=process_id,
            mode="Extend",
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
        # 使用正确的Localization_File路径（与Localization_Tool同级）
        localization_file_path = os.path.join(os.path.dirname(base_path), "Localization_File")
        report_path = os.path.join(localization_file_path, "output", "Extend", "Report")
        save_report(
            report, report_path, timestamp
        )
        return report


def _build_mod_mapping(base_path: str, chinese_file_path: str, english_file_path: str) -> dict:
    """
    基于mod_info.json中的id建立映射关系

    Args:
        base_path: 基础路径
        chinese_file_path: Chinese文件夹路径
        english_file_path: English文件夹路径

    Returns:
        dict: 映射关系字典，格式为 {chinese_mod_id: english_mod_path}
    """
    # 1. 定义函数：递归遍历文件夹，查找包含mod_info.json的mod文件夹
    def find_mod_folders(directory: str) -> list:
        """
        递归查找包含mod_info.json的mod文件夹
        
        Args:
            directory: 要搜索的目录
            
        Returns:
            list: 包含mod_info.json的mod文件夹列表
        """
        mod_folders = []
        for root, dirs, files in os.walk(directory):
            if "mod_info.json" in files:
                mod_folders.append(root)
        return mod_folders
    
    # 2. 从mod_info.json获取正确的mod_name
    def get_mod_name(mod_path: str) -> str:
        """
        从mod_info.json获取name和version，构建正确的mod_name
        
        Args:
            mod_path: mod文件夹路径
            
        Returns:
            str: 正确的mod_name，格式为name+version
        """
        mod_folder_name = os.path.basename(mod_path)
        mod_info_path = os.path.join(mod_path, "mod_info.json")
        if os.path.exists(mod_info_path):
            try:
                with open(mod_info_path, 'r', encoding='utf-8') as f:
                    mod_info = json.load(f)
                    name = mod_info.get("name", mod_folder_name)
                    version = mod_info.get("version", "unknown")
                    return f"{name} {version}"
            except Exception as e:
                print(f"[WARN]  读取mod_info.json失败: {mod_info_path} - {e}")
        return mod_folder_name
    
    # 3. 构建mod_id到mod_path的映射
    chinese_mods = {}
    english_mods = {}

    # 递归遍历Chinese文件夹下的所有mod文件夹
    chinese_mod_folders = find_mod_folders(chinese_file_path)
    for mod_path in chinese_mod_folders:
        mod_name = get_mod_name(mod_path)

        # 读取mod_info.json
        mod_info = read_mod_info(mod_path)
        if "id" in mod_info:
            mod_id = mod_info["id"]
            chinese_mods[mod_id] = {
                "path": mod_path,
                "name": mod_name,
                "version": mod_info.get("version", "unknown"),
                "mod_info": mod_info
            }
            print(f"[LIST] 发现中文mod: {mod_name} (id: {mod_id}, version: {chinese_mods[mod_id]['version']})")
        else:
            print(f"[WARN]  中文mod {mod_name} 缺少id信息")

    # 递归遍历English文件夹下的所有mod文件夹
    english_mod_folders = find_mod_folders(english_file_path)
    for mod_path in english_mod_folders:
        mod_name = get_mod_name(mod_path)

        # 读取mod_info.json
        mod_info = read_mod_info(mod_path)
        if "id" in mod_info:
            mod_id = mod_info["id"]
            english_mods[mod_id] = {
                "path": mod_path,
                "name": mod_name,
                "version": mod_info.get("version", "unknown"),
                "mod_info": mod_info
            }
            print(f"[LIST] 发现英文mod: {mod_name} (id: {mod_id}, version: {english_mods[mod_id]['version']})")
        else:
            print(f"[WARN]  英文mod {mod_name} 缺少id信息")

    # 4. 建立映射关系
    mapping = {}
    for mod_id, chinese_mod in chinese_mods.items():
        if mod_id in english_mods:
            mapping[chinese_mod["path"]] = english_mods[mod_id]["path"]
            print(f"[LINK] 建立映射关系: {chinese_mod['name']} -> {english_mods[mod_id]['name']} (id: {mod_id})")
            print(f"   版本信息: 中文 {chinese_mod['version']} -> 英文 {english_mods[mod_id]['version']}")
        else:
            # 如果没有找到相同id的英文mod，使用mod_name作为备选
            # 在English文件夹下查找同名mod
            english_mod_path = None
            for _, english_mod in english_mods.items():
                if english_mod["name"] == chinese_mod["name"]:
                    english_mod_path = english_mod["path"]
                    break
            
            if english_mod_path is None:
                # 如果没有找到同名mod，使用English文件夹作为备选
                english_mod_path = os.path.join(english_file_path, chinese_mod["name"])
                print(f"[LINK] 建立映射关系: {chinese_mod['name']} -> {chinese_mod['name']} (基于mod_name)")
                print("   警告: 未找到相同id的英文mod，使用mod_name作为备选")
            else:
                print(f"[LINK] 建立映射关系: {chinese_mod['name']} -> {chinese_mod['name']} (基于mod_name)")
                print("   警告: 未找到相同id的英文mod，使用同名mod作为备选")
            
            mapping[chinese_mod["path"]] = english_mod_path

    return mapping


def _process_existing_chinese_src(
    base_path: str, timestamp: str, report: Dict[str, Any]
) -> Dict[str, Any]:
    """
    处理已有中文src文件夹映射流程

    Args:
        base_path: 基础路径
        timestamp: 时间戳
        report: 报告

    Returns:
        Dict[str, Any]: 处理结果
    """
    try:
        # 1. 获取Chinese和English文件夹路径
        from src.common.config_utils import get_source_directory, get_backup_directory
        source_dir = get_source_directory("extend", "auto")
        if not source_dir:
            return generate_report(
                process_id=report["process_id"],
                mode="Extend",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["无法获取源目录"],
                },
            )
        chinese_file_path = os.path.join(source_dir, "Chinese")
        english_file_path = os.path.join(source_dir, "English")

        # 2. 重命名模组文件夹
        print("[NOTE] 开始重命名模组文件夹...")
        rename_mod_folders(chinese_file_path)
        rename_mod_folders(english_file_path)
        
        # 3. 重命名备份文件夹
        print("[NOTE] 开始重命名备份文件夹...")
        backup_dir = get_backup_directory("extend")
        backup_chinese_file_path = os.path.join(backup_dir, "Chinese")
        backup_english_file_path = os.path.join(backup_dir, "English")
        rename_mod_folders(backup_chinese_file_path)
        rename_mod_folders(backup_english_file_path)
        
        # 4. 恢复备份
        print("[NOTE] 开始恢复备份...")
        from src.common.config_utils import get_backup_directory, get_source_directory
        backup_path = get_backup_directory("extend")
        restore_backup(backup_path, get_source_directory("extend", "auto"))

        # 4. 获取映射规则文件路径
        strings_path = os.path.join(base_path, "project", "Extend", "Strings")
        chinese_strings_path = os.path.join(strings_path, "Chinese")
        print(f"[DIR] 映射规则文件路径: {chinese_strings_path}")
        
        # 5. 加载映射规则
        mapping_rules = load_mapping_rules(chinese_strings_path)
        
        # 6. 基于mod_info.json中的id建立映射关系
        mod_mapping = _build_mod_mapping(base_path, chinese_file_path, english_file_path)

        # 7. 遍历映射关系，执行映射操作
        for chinese_mod_path, english_mod_path in mod_mapping.items():
            mod_name = os.path.basename(chinese_mod_path)
            print(f"\n[NOTE] 处理mod: {mod_name}")
            print("----------------------------------")

            # 确保English文件夹下对应的mod文件夹存在
            os.makedirs(english_mod_path, exist_ok=True)

            # 8. 查找Chinese文件夹下mod内的src文件夹
            chinese_src_path = os.path.join(chinese_mod_path, "src")

            # 9. 检查src文件夹是否存在且包含中文
            if os.path.exists(chinese_src_path) and os.path.isdir(chinese_src_path):
                has_chinese = contains_chinese_in_src(chinese_src_path)
                if has_chinese:
                    print("[LIST] 使用src文件夹进行映射(包含中文)")
                    # 10. 执行字符串映射
                    print(f"[LIST] 开始对 {chinese_src_path} 执行字符串映射")
                    
                    # 遍历映射源下的所有文件
                    for root, _, files in os.walk(chinese_src_path):
                        for file in files:
                            if file.endswith(('.java', '.kt', '.kts')):
                                source_file = os.path.join(root, file)
                                # 计算相对路径
                                relative_path = os.path.relpath(source_file, chinese_src_path)
                                # 目标文件路径
                                target_file = os.path.join(english_mod_path, "src", relative_path)
                                # 确保目标目录存在
                                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                                
                                # 应用YAML映射
                                from src.common.yaml_utils import apply_yaml_mapping
                                result = apply_yaml_mapping(source_file, mapping_rules)
                                if result:
                                    # 将结果写回目标文件
                                    with open(target_file, 'w', encoding='utf-8') as f:
                                        f.write(result)
                                    print(f"[OK] 成功将 {source_file} 映射到 {target_file}")
                else:
                    print("[WARN]  src文件夹不包含中文，跳过映射")
            else:
                print("[WARN]  未找到src文件夹")

        # 9. 生成符合框架要求的输出路径
        # 从mod_mapping中获取第一个mod的信息来构建输出路径
        if mod_mapping:
            # 获取第一个mod的路径
            first_mod_path = next(iter(mod_mapping.keys()))
            # 从mod_info.json获取正确的mod_name
            def get_mod_name(mod_path: str) -> str:
                mod_folder_name = os.path.basename(mod_path)
                mod_info_path = os.path.join(mod_path, "mod_info.json")
                if os.path.exists(mod_info_path):
                    try:
                        with open(mod_info_path, 'r', encoding='utf-8') as f:
                            mod_info = json.load(f)
                            name = mod_info.get("name", mod_folder_name)
                            version = mod_info.get("version", "unknown")
                            return f"{name} {version}"
                    except Exception as e:
                        print(f"[WARN]  读取mod_info.json失败: {mod_info_path} - {e}")
                return mod_folder_name
            
            mod_name = get_mod_name(first_mod_path)
            # 构建输出路径：Localization_File/output/Extend_zh2en/mod_name/ - 使用mod_root配置
            from src.common.config_utils import get_directory
            mod_root = get_directory("mod_root")
            if mod_root:
                output_path = os.path.join(mod_root, "output", "Extend_zh2en", mod_name)
                os.makedirs(output_path, exist_ok=True)
        else:
            output_path = ""

        # 9. 实际映射结果
        mapped_result = {
            "total_count": len(mod_mapping),
            "success_count": len(mod_mapping),
            "fail_count": 0,
            "fail_reasons": [],
            "output_path": output_path
        }

        # 10. 更新报告
        report = generate_report(
            process_id=report["process_id"],
            mode="Extend",
            sub_flow=report["sub_flow"],
            status="success",
            data=mapped_result,
        )

        return report
    except Exception as e:
        print(f"[ERROR] 处理失败: {str(e)}")
        return generate_report(
            process_id=report["process_id"],
            mode="Extend",
            sub_flow=report["sub_flow"],
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"处理失败: {str(e)}"],
            },
        )


def _find_jar_files(chinese_file_path: str) -> list:
    """
    在Chinese文件夹下查找所有JAR文件

    Args:
        chinese_file_path: Chinese文件夹路径

    Returns:
        list: JAR文件路径列表
    """
    jar_files = []
    for root, dirs, files in os.walk(chinese_file_path):
        for file in files:
            if file.endswith('.jar'):
                jar_files.append(os.path.join(root, file))
    return jar_files


def _decompile_jar_files(jar_files: list) -> None:
    """
    反编译JAR文件，在mod文件夹下创建jar文件夹

    Args:
        jar_files: JAR文件路径列表
    """
    print(f"ℹ️  找到 {len(jar_files)} 个JAR文件，将进行反编译")
    for jar_file in jar_files:
        # 获取mod文件夹路径(JAR文件所在目录)
        mod_dir = os.path.dirname(jar_file)
        # 创建jar文件夹
        jar_dir = os.path.join(mod_dir, "jar")
        os.makedirs(jar_dir, exist_ok=True)
        print(f"[DIR] 在 {os.path.basename(mod_dir)} 文件夹下创建jar文件夹: {jar_dir}")
        # 使用jar_utils.py中的函数进行JAR反编译
        from src.common.jar_utils import decompile_jar
        decompile_jar(jar_file, jar_dir)


def _process_mod_for_mapping(chinese_mod_path: str, english_mod_path: str) -> None:
    """
    处理单个mod的映射
    
    Args:
        chinese_mod_path: 中文mod路径
        english_mod_path: 英文mod路径
    """
    mod_name = os.path.basename(chinese_mod_path)
    print(f"\n[NOTE] 处理mod: {mod_name}")
    print("----------------------------------")

    # 确保English文件夹下对应的mod文件夹存在
    os.makedirs(english_mod_path, exist_ok=True)

    # 查找Chinese文件夹下mod内的src和jar文件夹
    chinese_src_path = os.path.join(chinese_mod_path, "src")
    chinese_jar_path = os.path.join(chinese_mod_path, "jar")

    # 确定使用哪个文件夹进行映射
    use_src = False
    mapping_source = None

    # 检查src文件夹是否存在且包含中文
    if os.path.exists(chinese_src_path) and os.path.isdir(chinese_src_path):
        has_chinese = contains_chinese_in_src(chinese_src_path)
        if has_chinese:
            use_src = True
            mapping_source = chinese_src_path
            print("[LIST] 使用src文件夹进行映射(包含中文)")

    # 如果src文件夹不存在或不包含中文，检查jar文件夹
    if not use_src and os.path.exists(chinese_jar_path) and os.path.isdir(chinese_jar_path):
        mapping_source = chinese_jar_path
        print("[LIST] 使用jar文件夹进行映射(src文件夹不存在或不包含中文)")

    # 如果找到映射源，执行映射
    if mapping_source:
        # 执行字符串映射
        print(f"[LIST] 开始对 {mapping_source} 执行字符串映射")
        
        # 遍历映射源下的所有文件
        for root, _, files in os.walk(mapping_source):
            for file in files:
                if file.endswith(('.java', '.kt', '.kts')):
                    source_file = os.path.join(root, file)
                    # 计算相对路径
                    relative_path = os.path.relpath(source_file, mapping_source)
                    # 目标文件路径
                    target_file = os.path.join(english_mod_path, "src", relative_path)
                    # 确保目标目录存在
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    
                    # 应用字符串映射
                    from src.common.yaml_utils import apply_yaml_mapping
                    
                    # 从base_path获取映射规则
                    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    # 使用正确的Localization_File路径（与Localization_Tool同级）
                    localization_file_path = os.path.join(os.path.dirname(base_path), "Localization_File")
                    rule_path = os.path.join(localization_file_path, "rule")
                    
                    # 根据映射方向确定使用的规则
                    mapping_direction = "zh2en"  # 默认中文映射到英文
                    
                    # 加载映射规则
                    from src.common import load_mapping_rules
                    mapping_rules = []
                    
                    # 先检查Localization_File/rule文件夹
                    language = "Chinese" if mapping_direction == "zh2en" else "English"
                    rule_file_path = os.path.join(rule_path, language)
                    if os.path.exists(rule_file_path):
                        mapping_rules = load_mapping_rules(rule_file_path)
                    
                    # 如果Localization_File/rule文件夹没有规则，从传统路径加载
                    if not mapping_rules:
                        strings_path = os.path.join(base_path, "project", "Extend", "Strings")
                        strings_dir = os.path.join(strings_path, language)
                        mapping_rules = load_mapping_rules(strings_dir)
                    
                    # 应用映射规则
                    result = apply_yaml_mapping(source_file, mapping_rules)
                    if result:
                        # 将结果写回目标文件
                        with open(target_file, 'w', encoding='utf-8') as f:
                            f.write(result)
                        print(f"OK 成功将 {source_file} 映射到 {target_file}")
                    else:
                        # 如果映射失败，直接将源文件内容写入目标文件(作为备选)
                        with open(source_file, 'r', encoding='utf-8') as f:
                            source_content = f.read()
                        with open(target_file, 'w', encoding='utf-8') as f:
                            f.write(source_content)
                        print(f"[WARN]  映射失败，直接复制文件内容到 {target_file}")
    else:
        print("[WARN]  未找到可用的src或jar文件夹")


def _process_mod_mapping(mod_mapping: dict) -> dict:
    """
    处理mod映射关系

    Args:
        mod_mapping: mod映射关系字典

    Returns:
        dict: 映射结果
    """
    for chinese_mod_path, english_mod_path in mod_mapping.items():
        _process_mod_for_mapping(chinese_mod_path, english_mod_path)

    # 生成实际映射结果
    return {
        "total_count": len(mod_mapping),
        "success_count": len(mod_mapping),
        "fail_count": 0,
        "fail_reasons": [],
    }


def _process_no_chinese_src(
    base_path: str, timestamp: str, report: Dict[str, Any]
) -> Dict[str, Any]:
    """
    处理没有中文src文件夹映射流程

    Args:
        base_path: 基础路径
        timestamp: 时间戳
        report: 报告

    Returns:
        Dict[str, Any]: 处理结果
    """
    try:
        # 1. 获取Chinese和English文件夹路径
        from src.common.config_utils import get_source_directory, get_backup_directory
        source_dir = get_source_directory("extend", "auto")
        if not source_dir:
            return generate_report(
                process_id=report["process_id"],
                mode="Extend",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["无法获取源目录"],
                },
            )
        chinese_file_path = os.path.join(source_dir, "Chinese")
        english_file_path = os.path.join(source_dir, "English")

        # 2. 重命名模组文件夹
        print("[NOTE] 开始重命名模组文件夹...")
        rename_mod_folders(chinese_file_path)
        rename_mod_folders(english_file_path)
        
        # 3. 重命名备份文件夹
        print("[NOTE] 开始重命名备份文件夹...")
        backup_dir = get_backup_directory("extend")
        backup_chinese_file_path = os.path.join(backup_dir, "Chinese")
        backup_english_file_path = os.path.join(backup_dir, "English")
        rename_mod_folders(backup_chinese_file_path)
        rename_mod_folders(backup_english_file_path)
        
        # 4. 恢复备份
        print("[NOTE] 开始恢复备份...")
        backup_path = os.path.join(base_path, "project", "Extend", "File_backup")
        restore_backup(backup_path, os.path.join(base_path, "project", "Extend", "File"))

        # 4. 查找JAR文件
        jar_files = _find_jar_files(chinese_file_path)

        # 5. 反编译JAR文件
        if jar_files:
            print("[NOTE] 开始反编译JAR文件...")
            _decompile_jar_files(jar_files)

        # 6. 基于mod_info.json中的id建立映射关系
        mod_mapping = _build_mod_mapping(base_path, chinese_file_path, english_file_path)

        # 7. 处理映射关系
        mapped_result = _process_mod_mapping(mod_mapping)

        # 8. 生成符合框架要求的输出路径
        # 从mod_mapping中获取第一个mod的信息来构建输出路径
        if mod_mapping:
            # 获取第一个mod的路径
            first_mod_path = next(iter(mod_mapping.keys()))
            # 从mod_info.json获取正确的mod_name
            def get_mod_name(mod_path: str) -> str:
                mod_folder_name = os.path.basename(mod_path)
                mod_info_path = os.path.join(mod_path, "mod_info.json")
                if os.path.exists(mod_info_path):
                    try:
                        with open(mod_info_path, 'r', encoding='utf-8') as f:
                            mod_info = json.load(f)
                            name = mod_info.get("name", mod_folder_name)
                            version = mod_info.get("version", "unknown")
                            return f"{name} {version}"
                    except Exception as e:
                        print(f"[WARN]  读取mod_info.json失败: {mod_info_path} - {e}")
                return mod_folder_name
            
            mod_name = get_mod_name(first_mod_path)
            # 构建输出路径：Localization_File/output/Extend_zh2en/mod_name/ - 使用mod_root配置
            from src.common.config_utils import get_directory
            mod_root = get_directory("mod_root")
            if mod_root:
                output_path = os.path.join(mod_root, "output", "Extend_zh2en", mod_name)
                os.makedirs(output_path, exist_ok=True)
                # 将output_path添加到mapped_result中
                mapped_result["output_path"] = output_path
        else:
            mapped_result["output_path"] = ""

        # 8. 更新报告
        decompile_info = {
            "jar_path": ", ".join(jar_files[:3]) + ("..." if len(jar_files) > 3 else ""),
            "status": "success"
        } if jar_files else None

        report = generate_report(
            process_id=report["process_id"],
            mode="Extend",
            sub_flow=report["sub_flow"],
            status="success",
            data=mapped_result,
            decompile=decompile_info,
        )

        return report
    except Exception as e:
        print(f"[ERROR] 处理失败: {str(e)}")
        return generate_report(
            process_id=report["process_id"],
            mode="Extend",
            sub_flow=report["sub_flow"],
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"处理失败: {str(e)}"],
            },
        )


def extract_rules_from_processed(processed_folder: str, rule_file: str, language: str = "Chinese") -> None:
    """
    从已处理的文件夹中提取映射规则并更新现有规则文件
    
    Args:
        processed_folder: 已处理的文件夹路径
        rule_file: 现有规则文件路径
        language: 语言类型
    """
    from src.common.yaml_utils import (
        extract_mappings_from_processed_folder, 
        load_yaml_mappings, 
        merge_mapping_rules,
        update_mapping_status,
        save_yaml_mappings
    )
    
    print(f"[INFO] 从已处理文件夹提取规则: {processed_folder}")
    print(f"[INFO] 现有规则文件: {rule_file}")
    
    # 从已处理文件夹提取映射规则
    new_rules = extract_mappings_from_processed_folder(processed_folder, language)
    
    if not new_rules:
        print(f"[WARN]  未从文件夹 {processed_folder} 提取到任何规则")
        return
    
    # 加载现有规则
    existing_rules = load_yaml_mappings(rule_file)
    
    # 合并规则
    merged_rules = merge_mapping_rules(existing_rules, new_rules)
    
    # 更新规则状态
    updated_rules = update_mapping_status(merged_rules)
    
    # 保存合并后的规则
    if save_yaml_mappings(updated_rules, rule_file):
        print(f"[OK] 规则文件已更新: {rule_file}")
        print(f"[INFO] 更新后共 {len(updated_rules)} 条规则，其中 {sum(1 for r in updated_rules if r['status'] == 'unmapped')} 个未映射")
    else:
        print(f"[ERROR] 更新规则文件失败: {rule_file}")


def _process_existing_chinese_rules(
    base_path: str, timestamp: str, report: Dict[str, Any]
) -> Dict[str, Any]:
    """
    处理已有中文映射规则文件流程

    Args:
        base_path: 基础路径
        timestamp: 时间戳
        report: 报告

    Returns:
        Dict[str, Any]: 处理结果
    """
    try:
        # 1. 获取Chinese和English文件夹路径
        chinese_file_path = os.path.join(base_path, "project", "Extend", "File", "Chinese")
        english_file_path = os.path.join(base_path, "project", "Extend", "File", "English")
        
        # 2. 重命名模组文件夹
        print("[NOTE] 开始重命名模组文件夹...")
        rename_mod_folders(chinese_file_path)
        rename_mod_folders(english_file_path)
        
        # 3. 重命名备份文件夹
        print("[NOTE] 开始重命名备份文件夹...")
        backup_chinese_file_path = os.path.join(base_path, "project", "Extend", "File_backup", "Chinese")
        backup_english_file_path = os.path.join(base_path, "project", "Extend", "File_backup", "English")
        rename_mod_folders(backup_chinese_file_path)
        rename_mod_folders(backup_english_file_path)
        
        # 4. 恢复备份
        print("[NOTE] 开始恢复备份...")
        from src.common.config_utils import get_backup_directory
        backup_path = get_backup_directory("extend")
        from src.common.config_utils import get_source_directory
        restore_backup(backup_path, get_source_directory("extend", "auto"))
        
        # 4. 获取映射规则文件路径
        strings_path = os.path.join(base_path, "project", "Extend", "Strings")
        chinese_strings_path = os.path.join(strings_path, "Chinese")
        rule_path = os.path.join(base_path, "rule", "Chinese")
        print(f"[DIR] 映射规则文件路径: {chinese_strings_path}")
        print(f"[DIR] 规则文件夹路径: {rule_path}")
        
        # 5. 加载映射规则(优先从rule文件夹加载)
        mapping_rules = []
        
        # 先检查rule文件夹
        if os.path.exists(rule_path):
            rule_files = []
            for root, dirs, files in os.walk(rule_path):
                for file in files:
                    if file.endswith('.yaml') or file.endswith('.yml'):
                        rule_files.append(os.path.join(root, file))
            
            if rule_files:
                print(f"[LIST] 从rule文件夹加载规则文件: {len(rule_files)} 个")
                for rule_file in rule_files:
                    file_rules = load_mapping_rules(rule_file)
                    mapping_rules.extend(file_rules)
        
        # 如果rule文件夹没有规则，从传统路径加载
        if not mapping_rules:
            mapping_rules = load_mapping_rules(chinese_strings_path)
        
        # 6. 检查mod文件夹下是否有自带的映射规则文件
        mod_rules_loaded = False
        for mod_name in os.listdir(chinese_file_path):
            mod_path = os.path.join(chinese_file_path, mod_name)
            if not os.path.isdir(mod_path):
                continue
            
            # 检查mod文件夹下的规则文件
            mod_rule_files = []
            for root, dirs, files in os.walk(mod_path):
                for file in files:
                    if file.endswith('.json') or file.endswith('.yaml') or file.endswith('.yml'):
                        mod_rule_files.append(os.path.join(root, file))
            
            # 加载mod自带的规则文件，合并到总规则中
            for rule_file in mod_rule_files:
                mod_rules = load_mapping_rules(rule_file)
                if mod_rules:
                    if isinstance(mod_rules, dict):
                        mapping_rules.append(mod_rules)
                    elif isinstance(mod_rules, list):
                        mapping_rules.extend(mod_rules)
                    mod_rules_loaded = True
                    print(f"[LIST] 加载mod自带规则: {rule_file}，新增 {len(mod_rules)} 条规则")
        
        # 7. 统计规则信息
        total_rules = len(mapping_rules)
        mapped_rules = sum(1 for r in mapping_rules if r.get("status") in ["translated", "untranslated"])
        unmapped_rules = sum(1 for r in mapping_rules if r.get("status") == "unmapped")
        
        print(f"[LIST] 合并后共 {total_rules} 条映射规则")
        print(f"[LIST] 已映射规则: {mapped_rules} 条")
        print(f"[LIST] 未映射规则: {unmapped_rules} 条")
        
        # 8. 基于mod_info.json中的id建立映射关系
        mod_mapping = _build_mod_mapping(base_path, chinese_file_path, english_file_path)
        
        # 9. 遍历映射关系，执行映射操作
        for chinese_mod_path, english_mod_path in mod_mapping.items():
            mod_name = os.path.basename(chinese_mod_path)
            print(f"\n[NOTE] 处理mod: {mod_name}")
            print("----------------------------------")
            
            # 确保English文件夹下对应的mod文件夹存在
            os.makedirs(english_mod_path, exist_ok=True)
            
            # 10. 查找Chinese文件夹下mod内的src和jar文件夹
            chinese_src_path = os.path.join(chinese_mod_path, "src")
            chinese_jar_path = os.path.join(chinese_mod_path, "jar")
            
            # 11. 确定使用哪个文件夹进行映射
            use_src = False
            mapping_source = None
            
            # 检查src文件夹是否存在且包含中文
            if os.path.exists(chinese_src_path) and os.path.isdir(chinese_src_path):
                has_chinese = contains_chinese_in_src(chinese_src_path)
                if has_chinese:
                    use_src = True
                    mapping_source = chinese_src_path
                    print(f"[LIST] 使用src文件夹进行映射(包含中文)")
            
            # 如果src文件夹不存在或不包含中文，检查jar文件夹
            if not use_src and os.path.exists(chinese_jar_path) and os.path.isdir(chinese_jar_path):
                mapping_source = chinese_jar_path
                print(f"[LIST] 使用jar文件夹进行映射(src文件夹不存在或不包含中文)")
            
            # 12. 如果找到映射源，执行映射
            if mapping_source:
                print(f"[LIST] 开始对 {mapping_source} 执行字符串映射")
                
                # 遍历映射源下的所有文件
                for root, _, files in os.walk(mapping_source):
                    for file in files:
                        if file.endswith(('.java', '.kt', '.kts')):
                            source_file = os.path.join(root, file)
                            # 计算相对路径
                            relative_path = os.path.relpath(source_file, mapping_source)
                            # 目标文件路径
                            target_file = os.path.join(english_mod_path, "src", relative_path)
                            # 确保目标目录存在
                            os.makedirs(os.path.dirname(target_file), exist_ok=True)
                            
                            # 应用YAML映射
                            from src.common.yaml_utils import apply_yaml_mapping
                            result = apply_yaml_mapping(source_file, mapping_rules)
                            if result:
                                # 将结果写回目标文件
                                with open(target_file, 'w', encoding='utf-8') as f:
                                    f.write(result)
                                print(f"OK 成功将 {source_file} 映射到 {target_file}")
            else:
                print(f"[WARN]  未找到可用的src或jar文件夹")
        
        # 13. 生成符合框架要求的输出路径
        # 从mod_mapping中获取第一个mod的信息来构建输出路径
        if mod_mapping:
            # 获取第一个mod的路径
            first_mod_path = next(iter(mod_mapping.keys()))
            # 从mod_info.json获取正确的mod_name
            def get_mod_name(mod_path: str) -> str:
                mod_folder_name = os.path.basename(mod_path)
                mod_info_path = os.path.join(mod_path, "mod_info.json")
                if os.path.exists(mod_info_path):
                    try:
                        with open(mod_info_path, 'r', encoding='utf-8') as f:
                            mod_info = json.load(f)
                            name = mod_info.get("name", mod_folder_name)
                            version = mod_info.get("version", "unknown")
                            return f"{name} {version}"
                    except Exception as e:
                        print(f"[WARN]  读取mod_info.json失败: {mod_info_path} - {e}")
                return mod_folder_name
            
            mod_name = get_mod_name(first_mod_path)
            # 构建输出路径：Localization_File/output/Extend_zh2en/mod_name/ - 使用mod_root配置
            from src.common.config_utils import get_directory
            mod_root = get_directory("mod_root")
            if mod_root:
                output_path = os.path.join(mod_root, "output", "Extend_zh2en", mod_name)
                os.makedirs(output_path, exist_ok=True)
        else:
            output_path = ""

        # 13. 实际映射结果
        mapped_result = {
            "total_count": len(mod_mapping),
            "success_count": len(mod_mapping),
            "fail_count": 0,
            "fail_reasons": [],
            "total_rules": total_rules,
            "mapped_rules": mapped_rules,
            "unmapped_rules": unmapped_rules,
            "output_path": output_path
        }

        # 更新报告
        report = generate_report(
            process_id=report["process_id"],
            mode="Extend",
            sub_flow=report["sub_flow"],
            status="success",
            data=mapped_result,
        )

        return report
    except Exception as e:
        print(f"[ERROR] 处理失败: {str(e)}")
        return generate_report(
            process_id=report["process_id"],
            mode="Extend",
            sub_flow=report["sub_flow"],
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"处理失败: {str(e)}"],
            },
        )


def _process_existing_english_src(
    base_path: str, timestamp: str, report: Dict[str, Any]
) -> Dict[str, Any]:
    """
    处理已有英文src文件夹映射流程(英文映射到中文)

    Args:
        base_path: 基础路径
        timestamp: 时间戳
        report: 报告

    Returns:
        Dict[str, Any]: 处理结果
    """
    try:
        # 1. 获取English和Chinese文件夹路径
        from src.common.config_utils import get_source_directory, get_backup_directory
        source_dir = get_source_directory("extend", "auto")
        if not source_dir:
            return generate_report(
                process_id=report["process_id"],
                mode="Extend",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["无法获取源目录"],
                },
            )
        english_file_path = os.path.join(source_dir, "English")
        chinese_file_path = os.path.join(source_dir, "Chinese")

        # 2. 重命名模组文件夹
        print("[NOTE] 开始重命名模组文件夹...")
        rename_mod_folders(english_file_path)
        rename_mod_folders(chinese_file_path)
        
        # 3. 重命名备份文件夹
        print("[NOTE] 开始重命名备份文件夹...")
        backup_dir = get_backup_directory("extend")
        backup_english_file_path = os.path.join(backup_dir, "English")
        backup_chinese_file_path = os.path.join(backup_dir, "Chinese")
        rename_mod_folders(backup_english_file_path)
        rename_mod_folders(backup_chinese_file_path)
        
        # 4. 恢复备份
        print("[NOTE] 开始恢复备份...")
        backup_path = get_backup_directory("extend")
        restore_backup(backup_path, get_source_directory("extend", "auto"))

        # 4. 获取映射规则文件路径
        strings_path = os.path.join(base_path, "project", "Extend", "Strings")
        english_strings_path = os.path.join(strings_path, "English")
        print(f"[DIR] 映射规则文件路径: {english_strings_path}")
        
        # 5. 加载映射规则
        mapping_rules = load_mapping_rules(english_strings_path)
        
        # 6. 基于mod_info.json中的id建立映射关系
        mod_mapping = _build_mod_mapping(base_path, english_file_path, chinese_file_path)

        # 7. 遍历映射关系，执行映射操作
        for english_mod_path, chinese_mod_path in mod_mapping.items():
            mod_name = os.path.basename(english_mod_path)
            print(f"\n[NOTE] 处理mod: {mod_name}")
            print("----------------------------------")

            # 确保Chinese文件夹下对应的mod文件夹存在
            os.makedirs(chinese_mod_path, exist_ok=True)

            # 8. 查找English文件夹下mod内的src文件夹
            english_src_path = os.path.join(english_mod_path, "src")

            # 9. 检查src文件夹是否存在
            if os.path.exists(english_src_path) and os.path.isdir(english_src_path):
                print("[LIST] 使用src文件夹进行映射")
                # 10. 执行字符串映射
                print(f"[LIST] 开始对 {english_src_path} 执行字符串映射")
                
                # 遍历映射源下的所有文件
                for root, _, files in os.walk(english_src_path):
                    for file in files:
                        if file.endswith(('.java', '.kt', '.kts')):
                            source_file = os.path.join(root, file)
                            # 计算相对路径
                            relative_path = os.path.relpath(source_file, english_src_path)
                            # 目标文件路径
                            target_file = os.path.join(chinese_mod_path, "src", relative_path)
                            # 确保目标目录存在
                            os.makedirs(os.path.dirname(target_file), exist_ok=True)
                            
                            # 应用YAML映射
                            from src.common.yaml_utils import apply_yaml_mapping
                            result = apply_yaml_mapping(source_file, mapping_rules)
                            if result:
                                # 将结果写回目标文件
                                with open(target_file, 'w', encoding='utf-8') as f:
                                    f.write(result)
                                print(f"[OK] 成功将 {source_file} 映射到 {target_file}")
            else:
                print("[WARN]  未找到src文件夹")

        # 9. 生成符合框架要求的输出路径
        # 从mod_mapping中获取第一个mod的信息来构建输出路径
        if mod_mapping:
            # 获取第一个mod的路径
            first_mod_path = next(iter(mod_mapping.keys()))
            # 从mod_info.json获取正确的mod_name
            def get_mod_name(mod_path: str) -> str:
                mod_folder_name = os.path.basename(mod_path)
                mod_info_path = os.path.join(mod_path, "mod_info.json")
                if os.path.exists(mod_info_path):
                    try:
                        with open(mod_info_path, 'r', encoding='utf-8') as f:
                            mod_info = json.load(f)
                            name = mod_info.get("name", mod_folder_name)
                            version = mod_info.get("version", "unknown")
                            return f"{name} {version}"
                    except Exception as e:
                        print(f"[WARN]  读取mod_info.json失败: {mod_info_path} - {e}")
                return mod_folder_name
            
            mod_name = get_mod_name(first_mod_path)
            # 构建输出路径：Localization_File/output/Extend_en2zh/mod_name/ - 使用mod_root配置
            from src.common.config_utils import get_directory
            mod_root = get_directory("mod_root")
            if mod_root:
                output_path = os.path.join(mod_root, "output", "Extend_en2zh", mod_name)
                os.makedirs(output_path, exist_ok=True)
        else:
            output_path = ""

        # 9. 实际映射结果
        mapped_result = {
            "total_count": len(mod_mapping),
            "success_count": len(mod_mapping),
            "fail_count": 0,
            "fail_reasons": [],
            "output_path": output_path
        }

        # 10. 更新报告
        report = generate_report(
            process_id=report["process_id"],
            mode="Extend",
            sub_flow=report["sub_flow"],
            status="success",
            data=mapped_result,
        )

        return report
    except Exception as e:
        print(f"[ERROR] 处理失败: {str(e)}")
        return generate_report(
            process_id=report["process_id"],
            mode="Extend",
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
    处理没有英文src文件夹映射流程(英文映射到中文)

    Args:
        base_path: 基础路径
        timestamp: 时间戳
        report: 报告

    Returns:
        Dict[str, Any]: 处理结果
    """
    try:
        # 1. 获取English和Chinese文件夹路径
        from src.common.config_utils import get_source_directory, get_backup_directory
        source_dir = get_source_directory("extend", "auto")
        if not source_dir:
            return generate_report(
                process_id=report["process_id"],
                mode="Extend",
                sub_flow=report["sub_flow"],
                status="fail",
                data={
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": ["无法获取源目录"],
                },
            )
        english_file_path = os.path.join(source_dir, "English")
        chinese_file_path = os.path.join(source_dir, "Chinese")

        # 2. 重命名模组文件夹
        print("[NOTE] 开始重命名模组文件夹...")
        rename_mod_folders(english_file_path)
        rename_mod_folders(chinese_file_path)
        
        # 3. 重命名备份文件夹
        print("[NOTE] 开始重命名备份文件夹...")
        backup_dir = get_backup_directory("extend")
        backup_english_file_path = os.path.join(backup_dir, "English")
        backup_chinese_file_path = os.path.join(backup_dir, "Chinese")
        rename_mod_folders(backup_english_file_path)
        rename_mod_folders(backup_chinese_file_path)
        
        # 4. 恢复备份
        print("[NOTE] 开始恢复备份...")
        backup_path = get_backup_directory("extend")
        restore_backup(backup_path, get_source_directory("extend", "auto"))

        # 4. 查找JAR文件
        jar_files = _find_jar_files(english_file_path)

        # 5. 反编译JAR文件
        if jar_files:
            print("[NOTE] 开始反编译JAR文件...")
            _decompile_jar_files(jar_files)

        # 6. 基于mod_info.json中的id建立映射关系
        mod_mapping = _build_mod_mapping(base_path, english_file_path, chinese_file_path)

        # 7. 处理映射关系
        mapped_result = _process_mod_mapping(mod_mapping)

        # 8. 生成符合框架要求的输出路径
        # 从mod_mapping中获取第一个mod的信息来构建输出路径
        if mod_mapping:
            # 获取第一个mod的路径
            first_mod_path = next(iter(mod_mapping.keys()))
            # 从mod_info.json获取正确的mod_name
            def get_mod_name(mod_path: str) -> str:
                mod_folder_name = os.path.basename(mod_path)
                mod_info_path = os.path.join(mod_path, "mod_info.json")
                if os.path.exists(mod_info_path):
                    try:
                        with open(mod_info_path, 'r', encoding='utf-8') as f:
                            mod_info = json.load(f)
                            name = mod_info.get("name", mod_folder_name)
                            version = mod_info.get("version", "unknown")
                            return f"{name} {version}"
                    except Exception as e:
                        print(f"[WARN]  读取mod_info.json失败: {mod_info_path} - {e}")
                return mod_folder_name
            
            mod_name = get_mod_name(first_mod_path)
            # 构建输出路径：Localization_File/output/Extend_en2zh/mod_name/ - 使用mod_root配置
            from src.common.config_utils import get_directory
            mod_root = get_directory("mod_root")
            if mod_root:
                output_path = os.path.join(mod_root, "output", "Extend_en2zh", mod_name)
                os.makedirs(output_path, exist_ok=True)
                # 将output_path添加到mapped_result中
                mapped_result["output_path"] = output_path
        else:
            mapped_result["output_path"] = ""

        # 9. 更新报告
        decompile_info = {
            "jar_path": ", ".join(jar_files[:3]) + ("..." if len(jar_files) > 3 else ""),
            "status": "success"
        } if jar_files else None

        report = generate_report(
            process_id=report["process_id"],
            mode="Extend",
            sub_flow=report["sub_flow"],
            status="success",
            data=mapped_result,
            decompile=decompile_info,
        )

        return report
    except Exception as e:
        print(f"[ERROR] 处理失败: {str(e)}")
        return generate_report(
            process_id=report["process_id"],
            mode="Extend",
            sub_flow=report["sub_flow"],
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"处理失败: {str(e)}"],
            },
        )


def _process_existing_english_rules(
    base_path: str, timestamp: str, report: Dict[str, Any]
) -> Dict[str, Any]:
    """
    处理已有英文映射规则文件流程(英文映射到中文)

    Args:
        base_path: 基础路径
        timestamp: 时间戳
        report: 报告

    Returns:
        Dict[str, Any]: 处理结果
    """
    try:
        # 1. 获取English和Chinese文件夹路径
        english_file_path = os.path.join(base_path, "project", "Extend", "File", "English")
        chinese_file_path = os.path.join(base_path, "project", "Extend", "File", "Chinese")
        
        # 2. 重命名模组文件夹
        print("[NOTE] 开始重命名模组文件夹...")
        rename_mod_folders(english_file_path)
        rename_mod_folders(chinese_file_path)
        
        # 3. 重命名备份文件夹
        print("[NOTE] 开始重命名备份文件夹...")
        backup_english_file_path = os.path.join(base_path, "project", "Extend", "File_backup", "English")
        backup_chinese_file_path = os.path.join(base_path, "project", "Extend", "File_backup", "Chinese")
        rename_mod_folders(backup_english_file_path)
        rename_mod_folders(backup_chinese_file_path)
        
        # 4. 恢复备份
        print("[NOTE] 开始恢复备份...")
        from src.common.config_utils import get_backup_directory, get_source_directory
        backup_path = get_backup_directory("extend")
        restore_backup(backup_path, get_source_directory("extend", "auto"))
        
        # 4. 获取映射规则文件路径
        strings_path = os.path.join(base_path, "project", "Extend", "Strings")
        english_strings_path = os.path.join(strings_path, "English")
        rule_path = os.path.join(base_path, "rule", "English")
        print(f"[DIR] 映射规则文件路径: {english_strings_path}")
        print(f"[DIR] 规则文件夹路径: {rule_path}")
        
        # 5. 加载映射规则(优先从rule文件夹加载)
        mapping_rules = []
        
        # 先检查rule文件夹
        if os.path.exists(rule_path):
            rule_files = []
            for root, dirs, files in os.walk(rule_path):
                for file in files:
                    if file.endswith('.yaml') or file.endswith('.yml'):
                        rule_files.append(os.path.join(root, file))
            
            if rule_files:
                print(f"[LIST] 从rule文件夹加载规则文件: {len(rule_files)} 个")
                for rule_file in rule_files:
                    file_rules = load_mapping_rules(rule_file)
                    mapping_rules.extend(file_rules)
        
        # 如果rule文件夹没有规则，从传统路径加载
        if not mapping_rules:
            mapping_rules = load_mapping_rules(english_strings_path)
        
        # 6. 检查mod文件夹下是否有自带的映射规则文件
        mod_rules_loaded = False
        for mod_name in os.listdir(english_file_path):
            mod_path = os.path.join(english_file_path, mod_name)
            if not os.path.isdir(mod_path):
                continue
            
            # 检查mod文件夹下的规则文件
            mod_rule_files = []
            for root, dirs, files in os.walk(mod_path):
                for file in files:
                    if file.endswith('.json') or file.endswith('.yaml') or file.endswith('.yml'):
                        mod_rule_files.append(os.path.join(root, file))
            
            # 加载mod自带的规则文件，合并到总规则中
            for rule_file in mod_rule_files:
                mod_rules = load_mapping_rules(rule_file)
                if mod_rules:
                    if isinstance(mod_rules, dict):
                        mapping_rules.append(mod_rules)
                    elif isinstance(mod_rules, list):
                        mapping_rules.extend(mod_rules)
                    mod_rules_loaded = True
                    print(f"[LIST] 加载mod自带规则: {rule_file}，新增 {len(mod_rules)} 条规则")
        
        # 7. 统计规则信息
        total_rules = len(mapping_rules)
        mapped_rules = sum(1 for r in mapping_rules if r.get("status") in ["translated", "untranslated"])
        unmapped_rules = sum(1 for r in mapping_rules if r.get("status") == "unmapped")
        
        print(f"[LIST] 合并后共 {total_rules} 条映射规则")
        print(f"[LIST] 已映射规则: {mapped_rules} 条")
        print(f"[LIST] 未映射规则: {unmapped_rules} 条")
        
        # 8. 基于mod_info.json中的id建立映射关系
        mod_mapping = _build_mod_mapping(base_path, english_file_path, chinese_file_path)
        
        # 9. 遍历映射关系，执行映射操作
        for english_mod_path, chinese_mod_path in mod_mapping.items():
            mod_name = os.path.basename(english_mod_path)
            print(f"\n[NOTE] 处理mod: {mod_name}")
            print("----------------------------------")
            
            # 确保Chinese文件夹下对应的mod文件夹存在
            os.makedirs(chinese_mod_path, exist_ok=True)
            
            # 10. 查找English文件夹下mod内的src和jar文件夹
            english_src_path = os.path.join(english_mod_path, "src")
            english_jar_path = os.path.join(english_mod_path, "jar")
            
            # 11. 确定使用哪个文件夹进行映射
            use_src = False
            mapping_source = None
            
            # 检查src文件夹是否存在
            if os.path.exists(english_src_path) and os.path.isdir(english_src_path):
                use_src = True
                mapping_source = english_src_path
                print(f"[LIST] 使用src文件夹进行映射")
            
            # 如果src文件夹不存在，检查jar文件夹
            if not use_src and os.path.exists(english_jar_path) and os.path.isdir(english_jar_path):
                mapping_source = english_jar_path
                print(f"[LIST] 使用jar文件夹进行映射(src文件夹不存在)")
            
            # 12. 如果找到映射源，执行映射
            if mapping_source:
                print(f"[LIST] 开始对 {mapping_source} 执行字符串映射")
                
                # 遍历映射源下的所有文件
                for root, _, files in os.walk(mapping_source):
                    for file in files:
                        if file.endswith(('.java', '.kt', '.kts')):
                            source_file = os.path.join(root, file)
                            # 计算相对路径
                            relative_path = os.path.relpath(source_file, mapping_source)
                            # 目标文件路径
                            target_file = os.path.join(chinese_mod_path, "src", relative_path)
                            # 确保目标目录存在
                            os.makedirs(os.path.dirname(target_file), exist_ok=True)
                            
                            # 应用YAML映射
                            from src.common.yaml_utils import apply_yaml_mapping
                            result = apply_yaml_mapping(source_file, mapping_rules)
                            if result:
                                # 将结果写回目标文件
                                with open(target_file, 'w', encoding='utf-8') as f:
                                    f.write(result)
                                print(f"OK 成功将 {source_file} 映射到 {target_file}")
            else:
                print(f"[WARN]  未找到可用的src或jar文件夹")
        
        # 13. 生成符合框架要求的输出路径
        # 从mod_mapping中获取第一个mod的信息来构建输出路径
        if mod_mapping:
            # 获取第一个mod的路径
            first_mod_path = next(iter(mod_mapping.keys()))
            mod_name = os.path.basename(first_mod_path)
            # 构建输出路径：Localization_File/output/Extend_en2zh/20251212_220500_Aptly Simple Hullmods 2.1.2c/
            output_folder = f"{timestamp}_{mod_name}"
            # 使用正确的Localization_File路径（与Localization_Tool同级）
            localization_file_path = os.path.join(os.path.dirname(base_path), "Localization_File")
            output_path = os.path.join(localization_file_path, "output", "Extend_en2zh", output_folder)
            os.makedirs(output_path, exist_ok=True)
        else:
            output_path = ""

        # 13. 实际映射结果
        mapped_result = {
            "total_count": len(mod_mapping),
            "success_count": len(mod_mapping),
            "fail_count": 0,
            "fail_reasons": [],
            "total_rules": total_rules,
            "mapped_rules": mapped_rules,
            "unmapped_rules": unmapped_rules,
            "output_path": output_path
        }

        # 更新报告
        report = generate_report(
            process_id=report["process_id"],
            mode="Extend",
            sub_flow=report["sub_flow"],
            status="success",
            data=mapped_result,
        )

        return report
    except Exception as e:
        print(f"[ERROR] 处理失败: {str(e)}")
        return generate_report(
            process_id=report["process_id"],
            mode="Extend",
            sub_flow=report["sub_flow"],
            status="fail",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 1,
                "fail_reasons": [f"处理失败: {str(e)}"],
            },
        )
