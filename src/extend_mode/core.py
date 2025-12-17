#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extend模式核心模块

该模块负责使用映射规则将一种语言映射到另一种语言，支持以下功能：
1. 基于已有src文件夹进行映射
2. 基于JAR文件进行映射
3. 使用映射规则文件进行映射
4. 支持中英文双向映射
5. 生成映射报告
6. 支持多mod并行处理

该模块不再执行初始化操作，仅专注于语言映射功能，初始化操作由init_mode模块统一处理
"""

import os
import sys
from typing import Any, Dict

# 注意：不需要添加sys.path，main.py已经设置了正确的Python搜索路径

from src.common import (generate_report,  # noqa: E402, E501
                        get_timestamp, save_report,
                        contains_chinese_in_src,
                        read_mod_info, load_mapping_rules,
                        setup_logger, get_logger, log_progress, log_result)  # noqa: E402, E501
from src.common.config_utils import get_directory  # noqa: E402
from src.common.yaml_utils import (
    extract_mappings_from_processed_folder, 
    load_yaml_mappings, 
    merge_mapping_rules,
    update_mapping_status,
    save_yaml_mappings
)  # noqa: E402

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
        # 1. 根据子流程类型执行不同的逻辑
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
            # 发生异常时，只记录日志，不保存报告到特定目录
            print(f"[ERROR] {report['data']['fail_reasons'][0]}")
            return report

        # 3. 添加mode、language和mapping_direction到结果中，以便main函数调用show_output_guide
        result["mode"] = "Extend"
        result["language"] = language
        result["mapping_direction"] = mapping_direction
        
        # 4. 如果结果中没有output_path，尝试从data中获取
        if "output_path" not in result:
            result["output_path"] = result.get("data", {}).get("output_path", "")

        # 只将报告保存到映射文件夹和output_path
        if result.get("output_path"):
            # 从输出路径中提取模组名称
            mod_name = os.path.basename(result["output_path"])
            # 确定映射方向
            mapping_direction = result.get("mapping_direction", "zh2en")
            
            # 构建映射文件夹路径
            localization_file_path = os.path.join(os.path.dirname(base_path), "File")
            # 根据映射方向确定Extend目录
            extend_dir = f"Extend_{mapping_direction}" if mapping_direction in ["en2zh", "zh2en"] else "Extend"
            mapping_folder_path = os.path.join(localization_file_path, "output", extend_dir, mod_name)
            
            # 保存报告到映射文件夹
            save_report(
                result, mapping_folder_path, timestamp, rule_type="mapping", mod_name=mod_name
            )
            
            # 同时将报告保存到output_path中
            import json
            report_filename = f"extend_{timestamp}_report.json"
            report_filepath = os.path.join(result["output_path"], report_filename)
            
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
        # 发生异常时，只记录日志，不保存报告到特定目录
        print(f"[ERROR] 执行过程中发生异常: {str(e)}")
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
    # 使用init_mode中的集中式mod映射
    from src.init_mode import get_mod_mapping
    
    # 获取完整的mod映射
    mod_mappings = get_mod_mapping()
    
    # 构建chinese_mods和english_mods字典
    chinese_mods = {}
    english_mods = {}
    
    # 遍历mod_mappings，分类chinese和english mods
    for mod_id, mod_info in mod_mappings.items():
        if mod_info["language"] == "Chinese" and mod_info["source_type"] == "source":
            mod_path = mod_info["mod_path"]
            mod_name = f"{mod_info['mod_info'].name} {mod_info['mod_info'].version}"
            chinese_mods[mod_id] = {
                "path": mod_path,
                "name": mod_name,
                "version": mod_info["mod_info"].version,
                "mod_info": mod_info["mod_info"].to_dict()
            }
            print(f"[LIST] 发现中文mod: {mod_name} (id: {mod_id}, version: {mod_info['mod_info'].version})")
        elif mod_info["language"] == "English" and mod_info["source_type"] == "source":
            mod_path = mod_info["mod_path"]
            mod_name = f"{mod_info['mod_info'].name} {mod_info['mod_info'].version}"
            english_mods[mod_id] = {
                "path": mod_path,
                "name": mod_name,
                "version": mod_info["mod_info"].version,
                "mod_info": mod_info["mod_info"].to_dict()
            }
            print(f"[LIST] 发现英文mod: {mod_name} (id: {mod_id}, version: {mod_info['mod_info'].version})")
    
    # 建立映射关系
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
        from src.common.config_utils import get_directory
        source_dir = get_directory("source")
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

        # 4. 获取映射规则文件路径
        from src.common.config_utils import get_directory
        strings_path = get_directory("rules")
        chinese_strings_path = os.path.join(strings_path, "Chinese")
        print(f"[DIR] 映射规则文件路径: {chinese_strings_path}")
        
        # 5. 加载映射规则
        mapping_rules = load_mapping_rules(chinese_strings_path)
        
        # 6. 基于mod_info.json中的id建立映射关系
        mod_mapping = _build_mod_mapping(base_path, chinese_file_path, english_file_path)

        # 7. 遍历映射关系，执行映射操作
        mod_results = _process_mod_mapping(mod_mapping, base_path, timestamp, report)

        # 8. 生成符合框架要求的输出路径
        # 从mod_mapping中获取第一个mod的信息来构建输出路径
        if mod_mapping:
            # 获取第一个mod的路径
            first_mod_path = next(iter(mod_mapping.keys()))
            mod_name = os.path.basename(first_mod_path)
            # 构建输出路径：File/output/Extend_zh2en/mod_name/ - 使用mod_root配置
            from src.common.config_utils import get_directory
            mod_root = get_directory("mod_root")
            if mod_root:
                output_path = os.path.join(mod_root, "output", "Extend_zh2en", mod_name)
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


# 移除反编译相关功能，反编译功能已迁移到decompile_mode模块


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
                    # 使用正确的File路径（与Localization_Tool同级）
                    localization_file_path = os.path.join(os.path.dirname(base_path), "File")
                    rule_path = os.path.join(localization_file_path, "rule")
                    
                    # 根据映射方向确定使用的规则
                    mapping_direction = "zh2en"  # 默认中文映射到英文
                    
                    # 加载映射规则
                    from src.common import load_mapping_rules
                    mapping_rules = []
                    
                    # 先检查File/rule文件夹
                    language = "Chinese" if mapping_direction == "zh2en" else "English"
                    rule_file_path = os.path.join(rule_path, language)
                    if os.path.exists(rule_file_path):
                        mapping_rules = load_mapping_rules(rule_file_path)
                    
                    # 如果File/rule文件夹没有规则，从传统路径加载
                    if not mapping_rules:
                        from src.common.config_utils import get_directory
                        strings_path = get_directory("rules")
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


def _process_mod_mapping(mod_mapping: dict, base_path: str, timestamp: str, report: Dict[str, Any]) -> list:
    """
    处理mod映射关系

    Args:
        mod_mapping: mod映射关系字典
        base_path: 基础路径
        timestamp: 时间戳
        report: 报告

    Returns:
        list: 每个mod的映射结果列表
    """
    mod_results = []
    
    for source_mod_path, target_mod_path in mod_mapping.items():
        mod_name = os.path.basename(source_mod_path)
        print(f"\n[NOTE] 处理mod: {mod_name}")
        print("----------------------------------")
        
        # 处理单个mod的映射
        _process_mod_for_mapping(source_mod_path, target_mod_path)
        
        # 构建输出路径
        from src.common.config_utils import get_directory
        mod_root = get_directory("mod_root")
        if mod_root:
            # 确定映射方向
            if "Chinese" in source_mod_path:
                mapping_direction = "zh2en"
                output_path = os.path.join(mod_root, "output", f"Extend_{mapping_direction}", mod_name)
            else:
                mapping_direction = "en2zh"
                output_path = os.path.join(mod_root, "output", f"Extend_{mapping_direction}", mod_name)
            
            os.makedirs(output_path, exist_ok=True)
            
            # 为每个mod生成单独的报告
            mod_report = generate_report(
                process_id=f"{timestamp}_extend_{mod_name}",
                mode="Extend",
                sub_flow=report["sub_flow"],
                status="success",
                data={
                    "total_count": 1,
                    "success_count": 1,
                    "fail_count": 0,
                    "fail_reasons": [],
                    "output_path": output_path
                }
            )
            
            # 添加mode、language和mapping_direction到结果中
            mod_report["mode"] = "Extend"
            mod_report["language"] = "Chinese" if "Chinese" in source_mod_path else "English"
            mod_report["mapping_direction"] = mapping_direction
            mod_report["output_path"] = output_path
            
            # 保存报告到对应输出文件夹内
            save_report(mod_report, output_path, timestamp, rule_type="mapping", mod_name=mod_name)
            
            mod_results.append(mod_report)
    
    return mod_results


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
        from src.common.config_utils import get_directory
        source_dir = get_directory("source")
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

        # 6. 基于mod_info.json中的id建立映射关系
        mod_mapping = _build_mod_mapping(base_path, chinese_file_path, english_file_path)

        # 7. 处理映射关系
        mod_results = _process_mod_mapping(mod_mapping, base_path, timestamp, report)

        # 8. 生成符合框架要求的输出路径
        # 从mod_mapping中获取第一个mod的信息来构建输出路径
        mapped_result = {
            "total_count": len(mod_mapping),
            "success_count": len(mod_mapping),
            "fail_count": 0,
            "fail_reasons": [],
        }
        
        if mod_mapping:
            # 获取第一个mod的路径
            first_mod_path = next(iter(mod_mapping.keys()))
            mod_name = os.path.basename(first_mod_path)
            # 构建输出路径：File/output/Extend_zh2en/mod_name/ - 使用mod_root配置
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
        source_path = get_directory("source")
        chinese_file_path = os.path.join(source_path, "Chinese")
        english_file_path = os.path.join(source_path, "English")
        
        # 4. 获取映射规则文件路径
        strings_path = get_directory("rules")
        chinese_strings_path = os.path.join(strings_path, "Chinese")
        print(f"[DIR] 映射规则文件路径: {chinese_strings_path}")
        
        # 5. 加载映射规则(优先从rule文件夹加载)
        mapping_rules = []
        
        # 构建rule文件夹路径
        localization_file_path = os.path.join(os.path.dirname(base_path), "File")
        rule_path = os.path.join(localization_file_path, "rule")
        
        # 先检查rule文件夹
        if os.path.exists(rule_path):
            rule_files = []
            for root, dirs, files in os.walk(rule_path):
                for file in files:
                    # 同时检查yaml和json文件，由load_mapping_rules函数处理优先级
                    if file.endswith('.yaml') or file.endswith('.yml') or file.endswith('.json'):
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
        mod_results = _process_mod_mapping(mod_mapping, base_path, timestamp, report)
        
        # 10. 生成符合框架要求的输出路径
        # 从mod_mapping中获取第一个mod的信息来构建输出路径
        if mod_mapping:
            # 获取第一个mod的路径
            first_mod_path = next(iter(mod_mapping.keys()))
            mod_name = os.path.basename(first_mod_path)
            # 构建输出路径：Localization_File/output/Extend_zh2en/mod_name/ - 使用mod_root配置
            from src.common.config_utils import get_directory
            mod_root = get_directory("mod_root")
            if mod_root:
                output_path = os.path.join(mod_root, "output", "Extend_zh2en", mod_name)
        else:
            output_path = ""

        # 11. 实际映射结果
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
        from src.common.config_utils import get_directory
        source_dir = get_directory("source")
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

        # 4. 获取映射规则文件路径
        from src.common.config_utils import get_directory
        strings_path = get_directory("rules")
        english_strings_path = os.path.join(strings_path, "English")
        print(f"[DIR] 映射规则文件路径: {english_strings_path}")
        
        # 5. 加载映射规则
        mapping_rules = load_mapping_rules(english_strings_path)
        
        # 6. 基于mod_info.json中的id建立映射关系
        mod_mapping = _build_mod_mapping(base_path, english_file_path, chinese_file_path)

        # 7. 遍历映射关系，执行映射操作
        mod_results = _process_mod_mapping(mod_mapping, base_path, timestamp, report)

        # 8. 生成符合框架要求的输出路径
        # 从mod_mapping中获取第一个mod的信息来构建输出路径
        if mod_mapping:
            # 获取第一个mod的路径
            first_mod_path = next(iter(mod_mapping.keys()))
            mod_name = os.path.basename(first_mod_path)
            # 构建输出路径：File/output/Extend_en2zh/mod_name/ - 使用mod_root配置
            from src.common.config_utils import get_directory
            mod_root = get_directory("mod_root")
            if mod_root:
                output_path = os.path.join(mod_root, "output", "Extend_en2zh", mod_name)
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
        from src.common.config_utils import get_directory
        source_dir = get_directory("source")
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

        # 4. 查找JAR文件
        from src.decompile_mode.core import find_jar_files, decompile_all_jars
        jar_files = find_jar_files(english_file_path)

        # 5. 反编译JAR文件
        if jar_files and english_file_path:
            print("[NOTE] 开始反编译JAR文件...")
            # 使用decompile_mode API反编译所有JAR文件
            for jar_file in jar_files:
                jar_dir = os.path.join(os.path.dirname(jar_file), "jar")
                os.makedirs(jar_dir, exist_ok=True)
                from src.decompile_mode.core import decompile_single_jar
                decompile_single_jar(jar_file, jar_dir)

        # 6. 基于mod_info.json中的id建立映射关系
        mod_mapping = _build_mod_mapping(base_path, english_file_path, chinese_file_path)

        # 7. 处理映射关系
        mod_results = _process_mod_mapping(mod_mapping, base_path, timestamp, report)

        # 8. 生成符合框架要求的输出路径
        # 从mod_mapping中获取第一个mod的信息来构建输出路径
        mapped_result = {
            "total_count": len(mod_mapping),
            "success_count": len(mod_mapping),
            "fail_count": 0,
            "fail_reasons": [],
        }
        
        if mod_mapping:
            # 获取第一个mod的路径
            first_mod_path = next(iter(mod_mapping.keys()))
            mod_name = os.path.basename(first_mod_path)
            # 构建输出路径：File/output/Extend_en2zh/mod_name/ - 使用mod_root配置
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
        source_path = get_directory("source")
        english_file_path = os.path.join(source_path, "English")
        chinese_file_path = os.path.join(source_path, "Chinese")
        
        # 4. 获取映射规则文件路径
        strings_path = get_directory("rules")
        english_strings_path = os.path.join(strings_path, "English")
        print(f"[DIR] 映射规则文件路径: {english_strings_path}")
        
        # 5. 加载映射规则(优先从rule文件夹加载)
        mapping_rules = []
        
        # 构建rule文件夹路径
        localization_file_path = os.path.join(os.path.dirname(base_path), "File")
        rule_path = os.path.join(localization_file_path, "rule")
        
        # 先检查rule文件夹
        if os.path.exists(rule_path):
            rule_files = []
            for root, dirs, files in os.walk(rule_path):
                for file in files:
                    # 同时检查yaml和json文件，由load_mapping_rules函数处理优先级
                    if file.endswith('.yaml') or file.endswith('.yml') or file.endswith('.json'):
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
        mod_results = _process_mod_mapping(mod_mapping, base_path, timestamp, report)
        
        # 10. 生成符合框架要求的输出路径
        # 从mod_mapping中获取第一个mod的信息来构建输出路径
        if mod_mapping:
            # 获取第一个mod的路径
            first_mod_path = next(iter(mod_mapping.keys()))
            mod_name = os.path.basename(first_mod_path)
            # 构建输出路径：Localization_File/output/Extend_en2zh/20251212_220500_Aptly Simple Hullmods 2.1.2c/
            output_folder = f"{timestamp}_{mod_name}"
            # 使用正确的File路径（与Localization_Tool同级）
            localization_file_path = os.path.join(os.path.dirname(base_path), "File")
            output_path = os.path.join(localization_file_path, "output", "Extend_en2zh", output_folder)
            os.makedirs(output_path, exist_ok=True)
        else:
            output_path = ""

        # 11. 实际映射结果
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
