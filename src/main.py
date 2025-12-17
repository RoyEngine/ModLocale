#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ModLocale 主入口

提供Extract、Extend和Decompile三种模式的选择和执行，以及映射规则管理和完整工作流功能。

使用方法：
python main.py [模块名称] [参数]

模块列表：
- extract: 执行Extract模式，用于提取字符串
- extend: 执行Extend模式，用于映射字符串
- decompile: 执行Decompile模式，用于反编译或提取JAR文件
- localization: 执行映射规则管理（生成/更新/冲突检测）
- workflow: 执行完整工作流

详细帮助：
python main.py -h
python main.py [模块名称] -h

版本：1.0.0
"""

import argparse
import os
import sys

# 添加项目根目录到Python搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.logger_utils import setup_logger, get_logger, log_exception  # noqa: E402
from src.common.config_utils import load_config, get_directory, validate_directories  # noqa: E402
from src.extend_mode.core import run_extend_sub_flow  # noqa: E402
from src.extract_mode.core import run_extract_sub_flow  # noqa: E402
from src.decompile_mode.core import run_decompile_sub_flow  # noqa: E402

# 添加新的模块导入
from src.extend_mode import (
    extract_mapping_rules,
    process_unmapped_content,
    detect_and_resolve_conflicts,
    generate_translation_rules,
    update_translation_rules,
    run_complete_workflow,
    auto_generate_rules,
    manage_rules
)  # noqa: E402

# 设置全局日志记录器
logger = setup_logger("modlocale")


# 修改select_main_mode函数，移除高级模式的重复选项
def select_main_mode() -> str:
    """
    让用户选择主模式(Extract或Extend或Decompile或文件管理模式或映射规则管理或完整工作流)

    Returns:
        str: 选择的模式编号("1"、"2"、"3"、"4"、"5"或"6")
    """
    print("===========================================")
    print("               ModLocale")
    print("===========================================")
    print("请选择操作模式：")
    print("1. Extract模式(仅提取字符串，默认简洁模式)")
    print("2. Extend模式(执行映射流程，默认简洁模式)")
    print("3. Decompile模式(执行JAR文件反编译/提取)")
    print("4. 文件管理模式(文件夹创建、重命名、备份恢复)")
    print("5. 映射规则管理（生成/更新/冲突检测）")
    print("6. 运行完整工作流")
    print("===========================================")

    while True:
        choice = input("输入数字(1/2/3/4/5/6，直接回车默认选1)：").strip()
        if not choice:  # 直接回车，默认选1
            return "1"
        elif choice in ["1", "2", "3", "4", "5", "6"]:
            return choice
        print(f"输入无效，请输入正确的数字(1/2/3/4/5/6)！")


# 简化select_extract_sub_flow函数，确保输出路径正确
def select_extract_sub_flow() -> str:
    """
    让用户选择Extract模式的子流程

    Returns:
        str: 选择的子流程
    """
    # 检测source文件夹
    detection_result = check_source_folders()
    
    # 二级菜单：直接进入简洁模式的语言选择
    print("\n==========================================")
    print("        Extract模式 - 简洁模式(自动检测)")
    print("==========================================")
    
    # 显示检测结果
    print("🔍 正在检测主目录下的source文件夹...")
    if detection_result["english_src"]:
        print("✅ 检测到source/English/src文件夹(含英文文本)，将优先提取此处内容")
    elif detection_result["english_jar"]:
        print("✅ 检测到source/English/jars文件夹，将反编译未汉化jar包")
    else:
        print("❌ 未检测到source/English/src或jars文件夹，请先准备源文件")
    
    from src.common.config_utils import get_directory
    output_root = get_directory("output")
    if output_root:
        print(f"📤 提取结果将保存到：{output_root}/Extract_English/")
    else:
        print("📤 提取结果将保存到：主目录/File/output/Extract_English/")
    print("   包含：字符串映射规则文件 + 流程报告 + mod_info.json")
    print("==========================================")
    print("请选择提取语言：")
    print("1. 提取英文(优先检测src/无则反编译未汉化jar)")
    print("2. 提取中文(优先检测src/无则反编译已汉化jar)")
    print("0. 返回上一级菜单")
    print("==========================================")

    while True:
        lang_choice = input("输入数字(1/2/0，直接回车默认选1)：").strip()
        if not lang_choice:  # 直接回车，默认选1
            return "英文提取流程"
        elif lang_choice == "1":
            return "英文提取流程"
        elif lang_choice == "2":
            return "中文提取流程"
        elif lang_choice == "0":
            return "return_to_previous"
        print(f"输入无效，请输入正确的数字(1/2/0)！")


# 简化select_extend_sub_flow函数，确保输出路径正确
def select_extend_sub_flow() -> str:
    """
    让用户选择Extend模式的子流程

    Returns:
        str: 选择的子流程
    """
    # 检测source文件夹
    detection_result = check_source_folders()
    
    # 二级菜单：直接进入简洁模式的映射方向选择
    print("\n==========================================")
    print("        Extend模式 - 简洁模式")
    print("==========================================")
    
    # 显示检测结果
    print("🔍 正在检测主目录下的source和rule文件夹...")
    from src.common.config_utils import get_directory
    rule_path = get_directory("rules")
    if rule_path and os.path.exists(rule_path):
        print(f"✅ 检测到rule文件夹，将优先使用映射规则文件：{rule_path}")
    else:
        print("❌ 未检测到rule文件夹，将直接检测src/jars文件夹")
    
    if detection_result["chinese_src"] or detection_result["chinese_jar"]:
        print("✅ 检测到source/Chinese文件夹，可进行中文相关映射")
    if detection_result["english_src"] or detection_result["english_jar"]:
        print("✅ 检测到source/English文件夹，可进行英文相关映射")
    
    output_root = get_directory("output")
    if output_root:
        print(f"📤 映射结果将保存到：{output_root}/Extend_xxx/")
    else:
        print("📤 映射结果将保存到：主目录/File/output/Extend_xxx/")
    print("   包含：映射后的源文件夹 + 字符串映射规则文件 + 流程报告 + mod_info.json")
    print("==========================================")
    
    print("请选择映射方向：")
    print("1. 中文映射到英文(优先检测映射规则/无则自动检测src/jars)")
    print("2. 英文映射到中文(优先检测映射规则/无则自动检测src/jars)")
    print("0. 返回上一级菜单")
    print("==========================================")
    
    while True:
        direction_choice = input("输入数字(1/2/0，直接回车默认选1)：").strip()
        if not direction_choice:  # 直接回车，默认选1
            return "已有中文src文件夹映射流程"
        elif direction_choice == "1":
            mapping_direction = "中文→英文"
            
            # 显示执行信息
            print(f"\n==========================================")
            print(f"        Extend模式 - [{mapping_direction}] 简洁模式")
            print("==========================================")
            print("正在执行：优先检测映射规则文件夹→检测src/jars文件夹→映射字符串")
            print("流程步骤：创建文件夹→重命名模组→恢复备份→字符串映射...")
            
            return "已有中文src文件夹映射流程"
        elif direction_choice == "2":
            mapping_direction = "英文→中文"
            
            # 显示执行信息
            print(f"\n==========================================")
            print(f"        Extend模式 - [{mapping_direction}] 简洁模式")
            print("==========================================")
            print("正在执行：优先检测映射规则文件夹→检测src/jars文件夹→映射字符串")
            print("流程步骤：创建文件夹→重命名模组→恢复备份→字符串映射...")
            
            return "已有英文src文件夹映射流程"
        elif direction_choice == "0":
            return "return_to_previous"
        print(f"输入无效，请输入正确的数字(1/2/0)！")


# 简化select_decompile_sub_flow函数，确保逻辑清晰
def select_decompile_sub_flow() -> str:
    """
    让用户选择Decompile模式的子流程

    Returns:
        str: 选择的子流程
    """
    # 二级菜单：直接进入Decompile模式的子流程选择
    print("\n==========================================")
    print("        Decompile模式 - 操作选择")
    print("==========================================")
    
    print("📋 反编译模式支持以下操作：")
    print("1. 反编译单个JAR文件")
    print("2. 反编译目录中所有JAR文件")
    print("3. 提取单个JAR文件内容")
    print("4. 提取目录中所有JAR文件内容")
    print("0. 返回上一级菜单")
    print("===========================================")
    
    while True:
        decompile_choice = input("输入数字(0-4，直接回车默认选1)：").strip()
        if not decompile_choice:  # 直接回车，默认选1
            decompile_choice = "1"
        
        if decompile_choice == "0":
            return "return_to_previous"
        elif decompile_choice in ["1", "2", "3", "4"]:
            sub_flows = {
                "1": "反编译单个JAR文件",
                "2": "反编译目录中所有JAR文件",
                "3": "提取单个JAR文件内容",
                "4": "提取目录中所有JAR文件内容"
            }
            selected_sub_flow = sub_flows[decompile_choice]
            
            # 显示执行信息
            print(f"\n执行配置：")
            print(f"模式：Decompile")
            print(f"流程：{selected_sub_flow}")
            print("===========================================")
            
            return selected_sub_flow
        else:
            print(f"输入无效，请输入正确的数字(0-4)！")


# 移除toggle_advanced_mode函数，简化代码


# 移除set_main_language函数，简化代码


# 移除toggle_process_granularity函数，简化代码


# 移除toggle_precheck_mechanism函数，简化代码


# 移除advanced_settings函数，简化代码


# 移除select_cli_settings函数，简化代码


# 修改check_project_structure函数，确保目录结构符合配置
def check_project_structure() -> bool:
    """
    检查并创建必要的项目结构，严格按照框架文档生成目录

    Returns:
        bool: 项目结构检查结果
    """
    logger.info("检查项目结构...")
    
    # 获取工具根目录
    tool_root = get_directory("tool_root")
    if not tool_root:
        # 回退到当前脚本的项目根目录
        tool_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 定义 File 目录路径(在工具根目录下)
    localization_file_path = os.path.join(tool_root, "File")
    
    # 定义 File 下的必要文件夹结构 - 严格按照框架文档
    localization_folders = [
        # 源文件目录结构
        os.path.join(localization_file_path, "source"),
        os.path.join(localization_file_path, "source", "English"),
        os.path.join(localization_file_path, "source", "Chinese"),
        # 源文件备份目录结构
        os.path.join(localization_file_path, "source_backup"),
        os.path.join(localization_file_path, "source_backup", "English"),
        os.path.join(localization_file_path, "source_backup", "Chinese"),
        # 映射规则目录结构
        os.path.join(localization_file_path, "rule"),
        os.path.join(localization_file_path, "rule", "English"),
        os.path.join(localization_file_path, "rule", "Chinese"),
        # 输出目录结构
        os.path.join(localization_file_path, "output"),
        # Extract输出目录
        os.path.join(localization_file_path, "output", "Extract_Chinese"),
        os.path.join(localization_file_path, "output", "Extract_English"),
        # Extend输出目录
        os.path.join(localization_file_path, "output", "Extend_en2zh"),
        os.path.join(localization_file_path, "output", "Extend_zh2en"),
        # 映射后mod文件夹
        os.path.join(localization_file_path, "mapped_mods"),
    ]
    
    try:
        # 创建 Localization_File 目录结构
        for folder in localization_folders:
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
                logger.info(f"创建文件夹: {folder}")
        
        logger.info("项目结构检查完成，严格按照框架文档生成目录")
        return True
    except Exception as e:
        logger.error(f"项目结构检查失败: {str(e)}")
        print(f"[ERROR] 项目结构检查失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# 修改show_welcome_guide函数，确保路径正确
def show_welcome_guide():
    """
    显示欢迎信息和文件夹结构引导
    """
    print("==========================================")
    print("                ModLocale")
    print("==========================================")
    print("📌 【前置检查】请确认已按以下结构存放文件：")
    print("ModLocale/File/")
    print("├─ source/English/(src/jars) ｜ 英文源文件")
    print("├─ source/Chinese/(src/jars) ｜ 中文源文件")
    print("├─ rule/(可选)               ｜ 映射规则文件")
    print("└─ output/(自动生成)         ｜ 结果输出区")
    print("💡 忘记结构？输入「help」查看详细引导，输入「start」进入主菜单")
    print("==========================================")
    print("输入指令(help/start)：")
    
    # 处理用户输入
    while True:
        choice = input().strip().lower()
        if choice == "start":
            break
        elif choice == "help":
            show_detailed_guide()
        else:
            print("输入无效，请输入「help」或「start」：")


# 简化show_detailed_guide函数，确保路径正确
def show_detailed_guide():
    """
    显示详细的用户引导
    """
    print("\n# ModLocale - 友好用户引导手册")
    print("(适配终端交互，全程嵌入式引导，通俗易懂+步骤化，降低操作门槛)")
    print("\n## 🌟 欢迎使用ModLocale！")
    print("在开始操作前，请先完成「文件夹准备」(30秒即可搞定)，工具会严格按照你存放的文件夹结构识别文件，")
    print("输出内容也会统一整理到指定文件夹，全程无需手动翻找～")
    print("\n## 📂 第一步：主目录结构准备(必看！)")
    print("请先在ModLocale目录下创建「File」文件夹，并按以下结构存放文件夹，")
    print("**命名必须严格一致**(工具自动识别，错字会导致检测失败)：")
    print("""```
ModLocale/ (工具主目录)
├─ File/ (源文件存放区，工具自动创建！)
│  ├─ source/ (源文件存放区)
│  │  ├─ English/ (英文源文件)
│  │  │  ├─ src/ (可选：已有英文源码文件夹，放待提取的英文文本文件)
│  │  │  └─ jars/ (可选：待反编译的英文jar包，未汉化版)
│  │  └─ Chinese/ (中文源文件)
│  │     ├─ src/ (可选：已有中文化源码文件夹，放待提取/映射的中文文本文件)
│  │     └─ jars/ (可选：待反编译的中文jar包，已汉化版)
│  ├─ rule/ (映射规则存放区，Extend模式专属，可选)
│  │  ├─ English/ (英文映射规则文件)
│  │  └─ Chinese/ (中文映射规则文件)
│  └─ output/ (工具自动生成，无需创建！所有提取/映射结果+报告都在这里)
└─ src/ (工具源代码)
   ├─ common/ (通用模块)
   ├─ decompile_mode/ (反编译模式)
   ├─ extract_mode/ (提取模式)
   ├─ extend_mode/ (映射模式)
   └─ init_mode/ (初始化模式)
```""")
    print("\n### ✨ 核心引导：不同模式对应哪些文件夹？")
    print("| 操作模式       | 需准备的源文件夹       | 工具会自动处理什么？|")
    print("|----------------|------------------------|---------------------------------------------|")
    print("| Extract-提取英文 | ModLocale/File/source/English/src 或 ModLocale/File/source/English/jars | 优先读src，无则反编译jar，结果存到ModLocale/File/output/Extract_English |")
    print("| Extract-提取中文 | ModLocale/File/source/Chinese/src 或 ModLocale/File/source/Chinese/jars | 优先读src，无则反编译jar，结果存到ModLocale/File/output/Extract_Chinese |")
    print("| Extend-中映射英 | ModLocale/File/source/Chinese/xxx + ModLocale/File/rule/Chinese/xxx | 优先读映射规则，无则读src/jars，结果存到ModLocale/File/output/Extend_Zh2En |")
    print("| Extend-英映射中 | ModLocale/File/source/English/xxx + ModLocale/File/rule/English/xxx | 优先读映射规则，无则读src/jars，结果存到ModLocale/File/output/Extend_En2Zh |")
    print("\n💡 提示：ModLocale/File 目录会在工具启动时自动创建！")
    print("\n输入「start」进入主菜单，输入「help」重新查看引导：")


# 修改check_source_folders函数，确保路径正确
def check_source_folders() -> dict:
    """
    检查source文件夹下的src和jars子文件夹

    Returns:
        dict: 检测结果
    """
    result = {
        "english_src": False,
        "english_jar": False,
        "chinese_src": False,
        "chinese_jar": False
    }
    
    # 从配置中获取source目录路径
    source_path = get_directory("source")
    if not source_path:
        logger.error("获取source目录路径失败")
        return result
    
    # 检查英文源文件夹
    english_path = os.path.join(source_path, "English")
    if os.path.exists(english_path):
        if os.path.exists(os.path.join(english_path, "src")):
            result["english_src"] = True
        if os.path.exists(os.path.join(english_path, "jars")):
            result["english_jar"] = True
    
    # 检查中文源文件夹
    chinese_path = os.path.join(source_path, "Chinese")
    if os.path.exists(chinese_path):
        if os.path.exists(os.path.join(chinese_path, "src")):
            result["chinese_src"] = True
        if os.path.exists(os.path.join(chinese_path, "jars")):
            result["chinese_jar"] = True
    
    return result


# 简化show_output_guide函数，确保路径正确
# 添加文件管理模式的子流程选择函数
def select_file_management_sub_flow() -> str:
    """
    让用户选择文件管理模式的子流程

    Returns:
        str: 选择的子流程
    """
    print("\n==========================================")
    print("        文件管理模式 - 操作选择")
    print("==========================================")
    print("请选择文件管理操作：")
    print("1. 初始化项目文件夹结构")
    print("2. 重命名模组文件夹")
    print("3. 恢复备份")
    print("4. 执行完整文件管理流程")
    print("0. 返回上一级菜单")
    print("===========================================")

    while True:
        choice = input("输入数字(0-4，直接回车默认选4)：").strip()
        if not choice:
            choice = "4"
        if choice == "0":
            return "return_to_previous"
        elif choice in ["1", "2", "3", "4"]:
            sub_flows = {
                "1": "初始化项目文件夹结构",
                "2": "重命名模组文件夹",
                "3": "恢复备份",
                "4": "执行完整文件管理流程"
            }
            return sub_flows[choice]
        print(f"输入无效，请输入正确的数字(0-4)！")

# 添加文件管理模式的执行函数
def run_file_management_sub_flow(sub_flow: str, base_path: str) -> dict:
    """
    运行文件管理子流程

    Args:
        sub_flow: 子流程类型
        base_path: 基础路径

    Returns:
        dict: 处理结果
    """
    logger.info(f"执行文件管理子流程：{sub_flow}")
    
    # 导入必要的模块
    from src.init_mode import run_init_tasks
    from src.common.file_utils import rename_mod_folders, restore_backup
    from src.common.config_utils import get_directory
    
    result = {
        "status": "success",
        "data": {
            "total_count": 0,
            "success_count": 0,
            "fail_count": 0,
            "fail_reasons": []
        }
    }
    
    try:
        # 获取必要的目录路径
        tool_root = get_directory("tool_root")
        source_path = get_directory("source")
        backup_path = get_directory("source_backup")
        
        if sub_flow == "初始化项目文件夹结构" or sub_flow == "执行完整文件管理流程":
            # 执行初始化任务，包括创建项目结构
            logger.info("执行初始化任务，创建项目文件夹结构")
            init_result = run_init_tasks(tool_root)
            if init_result['status'] == 'fail':
                result['status'] = 'fail'
                result['data']['fail_count'] += 1
                result['data']['fail_reasons'].append("初始化项目结构失败")
            else:
                result['data']['success_count'] += 1
        
        if sub_flow == "重命名模组文件夹" or sub_flow == "执行完整文件管理流程":
            # 重命名模组文件夹
            logger.info("重命名模组文件夹")
            if rename_mod_folders(source_path):
                result['data']['success_count'] += 1
            else:
                result['status'] = 'fail'
                result['data']['fail_count'] += 1
                result['data']['fail_reasons'].append("重命名模组文件夹失败")
            
            if rename_mod_folders(backup_path):
                result['data']['success_count'] += 1
            else:
                result['status'] = 'fail'
                result['data']['fail_count'] += 1
                result['data']['fail_reasons'].append("重命名备份文件夹失败")
        
        if sub_flow == "恢复备份":
            # 恢复备份
            logger.info("恢复备份")
            if restore_backup(backup_path, source_path):
                result['data']['success_count'] += 1
            else:
                result['status'] = 'fail'
                result['data']['fail_count'] += 1
                result['data']['fail_reasons'].append("恢复备份失败")
        
        result['data']['total_count'] = result['data']['success_count'] + result['data']['fail_count']
        
        print(f"\n文件管理操作完成！")
        print(f"总计：{result['data']['total_count']} 项操作")
        print(f"成功：{result['data']['success_count']} 项")
        print(f"失败：{result['data']['fail_count']} 项")
        if result['data']['fail_reasons']:
            print(f"失败原因：")
            for reason in result['data']['fail_reasons']:
                print(f"  - {reason}")
        
        return result
    except Exception as e:
        logger.exception(f"执行文件管理子流程时发生异常: {e}")
        result['status'] = 'fail'
        result['data']['fail_count'] = 1
        result['data']['fail_reasons'].append(str(e))
        result['data']['total_count'] = 1
        return result

# 添加选择mod文件夹的函数
def select_mod_folder() -> str:
    """
    自动识别source文件夹下的mod子目录，并提供交互式选择界面

    Returns:
        str: 用户选择的mod文件夹路径，若取消则返回空字符串
    """
    try:
        # 从配置中获取source目录路径
        source_path = get_directory("source")
        if not source_path:
            print("[ERROR] 获取source目录路径失败")
            logger.error("获取source目录路径失败")
            return ""
        
        # 检查source目录是否存在
        if not os.path.exists(source_path):
            print(f"[ERROR] source目录不存在: {source_path}")
            logger.error(f"source目录不存在: {source_path}")
            return ""
        
        # 收集所有mod文件夹
        mod_folders = []
        
        # 遍历source目录下的所有语言子文件夹
        for lang_folder in os.listdir(source_path):
            lang_path = os.path.join(source_path, lang_folder)
            if os.path.isdir(lang_path):
                # 遍历语言子文件夹下的所有文件夹，直接识别mod文件夹
                for mod_folder in os.listdir(lang_path):
                    mod_folder_path = os.path.join(lang_path, mod_folder)
                    if os.path.isdir(mod_folder_path):
                        mod_folders.append({
                            "name": mod_folder,
                            "path": mod_folder_path,
                            "language": lang_folder
                        })
        
        # 检查是否找到mod文件夹
        if not mod_folders:
            print(f"[ERROR] 未找到任何mod文件夹")
            print(f"[INFO] 请检查source目录结构是否正确: {source_path}")
            print(f"[INFO] 预期结构: source/{lang_folder}/{mod_name}")
            logger.error(f"未找到任何mod文件夹，source目录: {source_path}")
            return ""
        
        # 以清晰的列表形式呈现给用户
        print("\n==========================================")
        print("        可用mod文件夹列表")
        print("==========================================")
        print(f"找到 {len(mod_folders)} 个可用的mod文件夹：")
        print("==========================================")
        
        for i, mod in enumerate(mod_folders, 1):
            print(f"{i}. {mod['name']} (语言: {mod['language']})")
            print(f"   路径: {mod['path']}")
        
        print("0. 返回上一级菜单")
        print("==========================================")
        
        # 提供交互式选择界面
        while True:
            choice = input("请选择一个mod文件夹（输入数字，直接回车默认选1）：").strip()
            if not choice:
                choice = "1"
            
            if choice == "0":
                return ""
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(mod_folders):
                    selected_mod = mod_folders[index]
                    print(f"\n==========================================")
                    print(f"        已选择mod文件夹")
                    print(f"==========================================")
                    print(f"名称: {selected_mod['name']}")
                    print(f"语言: {selected_mod['language']}")
                    print(f"路径: {selected_mod['path']}")
                    print("==========================================")
                    
                    # 确认用户选择
                    confirm = input("是否确认选择？(y/n，默认y)：").strip().lower()
                    if confirm in ["", "y", "yes"]:
                        return selected_mod['path']
                    else:
                        print("\n重新选择mod文件夹...")
                else:
                    print(f"[ERROR] 输入无效，请输入1-{len(mod_folders)}之间的数字")
            except ValueError:
                print("[ERROR] 输入无效，请输入数字")
    
    except PermissionError:
        print("[ERROR] 权限不足，无法访问目录")
        logger.error("权限不足，无法访问目录")
        return ""
    except Exception as e:
        print(f"[ERROR] 选择mod文件夹时发生异常: {str(e)}")
        logger.exception(f"选择mod文件夹时发生异常: {e}")
        return ""

# 简化show_output_guide函数，确保输出路径正确
def show_output_guide(output_path: str, mode: str, language: str):
    """
    显示输出文件夹引导

    Args:
        output_path: 输出路径
        mode: 操作模式
        language: 语言类型
    """
    print("\n🎉 操作完成！所有结果已保存至：")
    print(f"👉 输出路径：{output_path}")
    print("📂 文件夹内包含：")
    
    if mode == "Extract":
        # Extract模式输出
        mod_folder_name = os.path.basename(output_path)
        # 从输出路径中提取mod名称(去掉时间戳前缀)
        mod_name = '_'.join(os.path.basename(output_path).split('_')[2:]) if len(os.path.basename(output_path).split('_')) >= 3 else os.path.basename(output_path)
        print(f"   1. {language}_mappings.json - 字符串映射规则文件(可用于Extend模式)")
        print(f"   2. {language}_mappings.yaml - 字符串映射规则文件(可用于Extend模式)")
        # 从输出路径中提取时间戳，用于生成报告文件
        basename = os.path.basename(output_path)
        parts = basename.split('_')
        if len(parts) >= 2:
            timestamp = parts[0] + '_' + parts[1]
            print(f"   3. extract_{timestamp}_report.json - 流程报告(含检测结果、执行步骤、耗时)")
            print(f"   4. mod_info.json - mod信息文件(可用于Extend模式)")
        else:
            print(f"   3. mod_info.json - mod信息文件(可用于Extend模式)")
        print("💡 小贴士：")
        print(f"   - 若需映射，可将 {language}_mappings.json 或 {language}_mappings.yaml + mod_info.json复制到rule/{language}/{mod_name}")
        print(f"   - 报告中若标「⚠️」，代表jar反编译时跳过了无效文件，不影响结果")
    elif mode == "Extend":
        # Extend模式输出
        mod_folder_name = os.path.basename(output_path)
        # 从输出路径中提取mod名称(去掉时间戳前缀)
        mod_name = '_'.join(os.path.basename(output_path).split('_')[2:])
        print(f"   1. 被映射的Mod文件夹({mod_name}) - 映射后的源文件夹")
        
        # 根据输出路径判断映射方向
        if "Extend_zh2en" in output_path:
            # 中文映射到英文
            print(f"   2. English_mappings.json - 字符串映射规则文件(可用于Extend模式)由被映射后的src文件夹提取")
            print(f"   3. English_mappings.yaml - 字符串映射规则文件(可用于Extend模式)由被映射后的src文件夹提取")
            # 从输出路径中提取时间戳
            timestamp = os.path.basename(output_path).split('_')[0] + '_' + os.path.basename(output_path).split('_')[1]
            print(f"   4. extend_{timestamp}_report.json - 流程报告(含检测结果、执行步骤、耗时)")
            print(f"   5. mod_info.json - mod信息文件(可用于Extend模式)")
            print("💡 小贴士：")
            print(f"   - 若需映射，可将 English_mappings.json 或 English_mappings.yaml + mod_info.json复制到rule/English/{mod_name}")
            print(f"   - 报告中若标「⚠️」，代表jar反编译时跳过了无效文件，不影响结果")
        elif "Extend_en2zh" in output_path:
            # 英文映射到中文
            print(f"   2. Chinese_mappings.json - 字符串映射规则文件(可用于Extend模式)由被映射后的src文件夹提取")
            print(f"   3. Chinese_mappings.yaml - 字符串映射规则文件(可用于Extend模式)由被映射后的src文件夹提取")
            # 从输出路径中提取时间戳
            timestamp = os.path.basename(output_path).split('_')[0] + '_' + os.path.basename(output_path).split('_')[1]
            print(f"   4. extend_{timestamp}_report.json - 流程报告(含检测结果、执行步骤、耗时)")
            print(f"   5. mod_info.json - mod信息文件(可用于Extend模式)")
            print("💡 小贴士：")
            print(f"   - 若需映射，可将 Chinese_mappings.json 或 Chinese_mappings.yaml + mod_info.json复制到rule/Chinese/{mod_name}")
            print(f"   - 报告中若标「⚠️」，代表jar反编译时跳过了无效文件，不影响结果")
    
    print("==========================================")
    
    # 检查是否需要自动打开输出文件夹
    global AUTO_OPEN_OUTPUT_FOLDER
    if AUTO_OPEN_OUTPUT_FOLDER:
        print("🔄 正在自动打开输出文件夹...")
        from src.common.file_utils import open_directory
        open_directory(output_path)
        return
    else:
        # 处理用户输入
        print("输入「back」返回主菜单，输入「open」直接打开输出文件夹：")
        while True:
            choice = input().strip().lower()
            if choice == "back":
                return
            elif choice == "open":
                from src.common.file_utils import open_directory
                open_directory(output_path)
                return
            else:
                print("输入无效，请输入「back」或「open」：")


# 添加映射规则管理子流程选择函数
def select_localization_sub_flow() -> str:
    """
    让用户选择映射规则管理的子流程

    Returns:
        str: 选择的子流程类型
    """
    print("\n==========================================")
    print("        映射规则管理 - 操作选择")
    print("==========================================")
    print("请选择映射规则管理操作：")
    print("1. 提取映射规则")
    print("2. 处理未映射内容")
    print("3. 检测和解决冲突")
    print("4. 自动生成规则")
    print("5. 管理映射规则")
    print("0. 返回上一级菜单")
    print("==========================================")

    while True:
        choice = input("输入数字(0-5，直接回车默认选1)：").strip()
        if not choice:
            choice = "1"
        if choice == "0":
            return "return_to_previous"
        elif choice in ["1", "2", "3", "4", "5"]:
            sub_flows = {
                "1": "提取映射规则",
                "2": "处理未映射内容",
                "3": "检测和解决冲突",
                "4": "自动生成规则",
                "5": "管理映射规则"
            }
            return sub_flows[choice]
        print(f"输入无效，请输入正确的数字(0-5)！")

# 添加映射规则管理执行函数
def run_localization_sub_flow(sub_flow: str, base_path: str) -> dict:
    """
    运行映射规则管理子流程

    Args:
        sub_flow: 子流程类型
        base_path: 基础路径

    Returns:
        dict: 处理结果
    """
    logger.info(f"执行映射规则管理子流程：{sub_flow}")
    
    result = {
        "status": "success",
        "data": {
            "total_count": 0,
            "success_count": 0,
            "fail_count": 0,
            "fail_reasons": []
        }
    }
    
    try:
        if sub_flow == "提取映射规则":
            # 获取用户输入
            source_dir = input("请输入源目录路径：").strip()
            output_file = input("请输入输出规则文件路径：").strip()
            existing_rule = input("请输入现有规则文件路径（可选）：").strip() or None
            language = input("请输入语言类型（默认：English）：").strip() or "English"
            
            # 执行提取映射规则
            result = extract_mapping_rules(
                source_dir=source_dir,
                existing_rule=existing_rule,
                output_file=output_file,
                language=language
            )
        elif sub_flow == "处理未映射内容":
            # 获取用户输入
            rule_file = input("请输入规则文件路径：").strip()
            report_file = input("请输入未映射内容报告文件路径（可选）：").strip() or None
            list_unmapped = input("是否列出未映射内容？(y/n，默认n)：").strip().lower() == "y"
            mark_translated = input("是否将未映射内容标记为已翻译？(y/n，默认n)：").strip().lower() == "y"
            output_file = input("请输入输出文件路径（可选）：").strip() or None
            
            # 执行处理未映射内容
            result = process_unmapped_content(
                rule_file=rule_file,
                report_file=report_file,
                list_unmapped=list_unmapped,
                mark_translated=mark_translated,
                output_file=output_file
            )
        elif sub_flow == "检测和解决冲突":
            # 获取用户输入
            rule_file = input("请输入规则文件路径：").strip()
            report_file = input("请输入冲突报告文件路径（可选）：").strip() or None
            resolve = input("是否自动解决冲突？(y/n，默认n)：").strip().lower() == "y"
            resolve_strategy = input("请输入冲突解决策略（latest/oldest，默认latest）：").strip() or "latest"
            
            # 执行检测和解决冲突
            result = detect_and_resolve_conflicts(
                rule_file=rule_file,
                generate_report=bool(report_file),
                report_file=report_file,
                resolve=resolve,
                resolve_strategy=resolve_strategy
            )
        elif sub_flow == "自动生成规则":
            # 获取用户输入
            chinese_src_dir = input("请输入中文src文件夹路径：").strip()
            english_src_dir = input("请输入英文src文件夹路径（可选）：").strip() or ""
            output_file = input("请输入输出规则文件路径：").strip()
            mod_id = input("请输入模组ID（可选）：").strip() or ""
            existing_rules = input("请输入现有规则文件路径（可选）：").strip() or ""
            language = input("请输入主要语言类型（默认：English）：").strip() or "English"
            
            # 执行自动生成规则
            result = auto_generate_rules(
                chinese_src_dir=chinese_src_dir,
                english_src_dir=english_src_dir,
                output_file=output_file,
                mod_id=mod_id,
                language=language,
                existing_rules=existing_rules
            )
        elif sub_flow == "管理映射规则":
            # 执行映射规则管理
            result = manage_rules()
        elif sub_flow == "return_to_previous":
            return {"status": "success", "message": "返回上一级菜单"}
        
        return result
    except Exception as e:
        logger.exception(f"执行映射规则管理子流程时发生异常: {e}")
        result['status'] = 'fail'
        result['data']['fail_count'] = 1
        result['data']['fail_reasons'].append(str(e))
        result['data']['total_count'] = 1
        return result

# 添加完整工作流子流程选择函数
def select_workflow_sub_flow() -> str:
    """
    让用户选择完整工作流的子流程

    Returns:
        str: 选择的子流程类型
    """
    print("\n==========================================")
    print("        完整工作流 - 操作选择")
    print("==========================================")
    print("请选择完整工作流操作：")
    print("1. 生成翻译规则")
    print("2. 更新翻译规则")
    print("3. 运行完整工作流")
    print("0. 返回上一级菜单")
    print("==========================================")

    while True:
        choice = input("输入数字(0-3，直接回车默认选1)：").strip()
        if not choice:
            choice = "1"
        if choice == "0":
            return "return_to_previous"
        elif choice in ["1", "2", "3"]:
            sub_flows = {
                "1": "生成翻译规则",
                "2": "更新翻译规则",
                "3": "运行完整工作流"
            }
            return sub_flows[choice]
        print(f"输入无效，请输入正确的数字(0-3)！")

# 添加完整工作流执行函数
def run_workflow_sub_flow(sub_flow: str, base_path: str) -> dict:
    """
    运行完整工作流子流程

    Args:
        sub_flow: 子流程类型
        base_path: 基础路径

    Returns:
        dict: 处理结果
    """
    logger.info(f"执行完整工作流子流程：{sub_flow}")
    
    result = {
        "status": "success",
        "data": {
            "total_count": 0,
            "success_count": 0,
            "fail_count": 0,
            "fail_reasons": []
        }
    }
    
    try:
        if sub_flow == "生成翻译规则":
            # 获取用户输入
            english_file = input("请输入英文映射文件路径：").strip()
            chinese_file = input("请输入中文映射文件路径：").strip()
            output_file = input("请输入输出规则文件路径：").strip()
            mod_id = input("请输入模组ID（可选）：").strip() or ""
            
            # 执行生成翻译规则
            result = generate_translation_rules(
                english_file=english_file,
                chinese_file=chinese_file,
                output_file=output_file,
                mod_id=mod_id
            )
        elif sub_flow == "更新翻译规则":
            # 获取用户输入
            existing_rules_file = input("请输入现有规则文件路径：").strip()
            new_english_file = input("请输入新的英文映射文件路径：").strip()
            new_chinese_file = input("请输入新的中文映射文件路径：").strip()
            output_file = input("请输入输出规则文件路径：").strip()
            mod_id = input("请输入模组ID（可选）：").strip() or ""
            
            # 执行更新翻译规则
            result = update_translation_rules(
                existing_rules_file=existing_rules_file,
                new_english_file=new_english_file,
                new_chinese_file=new_chinese_file,
                output_file=output_file,
                mod_id=mod_id
            )
        elif sub_flow == "运行完整工作流":
            # 自动选择mod文件夹
            print("[INFO] 正在自动识别可用的mod文件夹...")
            source_dir = select_mod_folder()
            
            # 检查用户是否取消选择
            if not source_dir:
                return {"status": "success", "message": "返回上一级菜单"}
            
            # 自动生成输出目录路径
            mod_name = os.path.basename(source_dir)
            output_dir = os.path.join(get_directory("output"), f"Workflow_{mod_name}")
            print(f"[INFO] 自动生成输出目录：{output_dir}")
            
            # 询问用户是否使用双语src文件夹
            use_bilingual_src = input("是否使用双语src文件夹自动生成规则？(y/n，默认n)：").strip().lower() == "y"
            
            if use_bilingual_src:
                # 自动获取双语src文件夹路径
                # 假设双语src文件夹位于source目录下的English和Chinese子文件夹中
                source_root = os.path.dirname(os.path.dirname(source_dir))
                bilingual_src_dir = source_root
                print(f"[INFO] 自动识别双语src文件夹：{bilingual_src_dir}")
                
                mod_id = input("请输入模组ID（可选，默认使用mod名称）：").strip() or mod_name
                existing_rules = input("请输入现有规则文件路径（可选）：").strip() or ""
                
                # 执行运行完整工作流，使用双语src文件夹
                result = run_complete_workflow(
                    source_dir=source_dir,
                    output_dir=output_dir,
                    bilingual_src_dir=bilingual_src_dir,
                    mod_id=mod_id,
                    existing_rules=existing_rules
                )
            else:
                # 使用传统方式，需要英文和中文映射文件
                english_file = input("请输入英文映射文件路径：").strip()
                chinese_file = input("请输入中文映射文件路径：").strip()
                mod_id = input("请输入模组ID（可选，默认使用mod名称）：").strip() or mod_name
                existing_rules = input("请输入现有规则文件路径（可选）：").strip() or ""
                
                # 执行运行完整工作流
                result = run_complete_workflow(
                    source_dir=source_dir,
                    output_dir=output_dir,
                    english_file=english_file,
                    chinese_file=chinese_file,
                    mod_id=mod_id,
                    existing_rules=existing_rules
                )
        elif sub_flow == "return_to_previous":
            return {"status": "success", "message": "返回上一级菜单"}
        
        return result
    except Exception as e:
        logger.exception(f"执行完整工作流子流程时发生异常: {e}")
        result['status'] = 'fail'
        result['data']['fail_count'] = 1
        result['data']['fail_reasons'].append(str(e))
        result['data']['total_count'] = 1
        return result

# 从配置管理器中获取设置
from src.common.config_utils import get_setting, set_setting

# 全局变量：是否显示欢迎引导
SHOW_WELCOME_GUIDE = get_setting("show_welcome_guide")

# 全局变量：是否自动打开输出文件夹
AUTO_OPEN_OUTPUT_FOLDER = get_setting("auto_open_output_folder")

# 移除高级模式配置，简化代码
ADVANCED_MODE_ENABLED = False  # 禁用高级模式
MAIN_LANGUAGE = "全部"  # 默认值
PROCESS_GRANULARITY_ENABLED = False  # 默认值
PRECHECK_MECHANISM_ENABLED = False  # 默认值


# 修改main函数，移除冗余代码，确保逻辑清晰
def main():
    """
    主函数
    """
    logger.info("==========================================")
    logger.info("               ModLocale")
    logger.info("==========================================")
    logger.info("工具启动，开始解析命令行参数")
    
    try:
        # 加载配置文件
        if not load_config():
            print("[ERROR] 加载配置文件失败")
            return
        
        # 验证目录结构
        if not validate_directories():
            print("[ERROR] 验证目录结构失败")
            return
        
        # 检查是否需要显示欢迎引导
        if SHOW_WELCOME_GUIDE:
            logger.info("前置检查已开启，显示欢迎引导")
            show_welcome_guide()
        else:
            logger.info("前置检查已默认关闭，直接进入主菜单")
        
        # 检查项目结构
        if not check_project_structure():
            return
        
        # 初始化init_mode，构建mod映射关系
        try:
            from src.init_mode import run_init_tasks
            from src.common.config_utils import get_directory
            mod_root = get_directory("mod_root")
            if mod_root:
                init_result = run_init_tasks(mod_root)
                logger.info(f"init_mode初始化完成，状态: {init_result['status']}")
                if init_result['status'] == 'fail':
                    print(f"[WARN]  init_mode初始化失败，可能影响后续操作: {init_result['data']['fail_reasons']}")
        except Exception as e:
            logger.exception(f"初始化init_mode时发生异常: {e}")
            print(f"[WARN]  初始化init_mode时发生异常: {e}")
        
        # 解析命令行参数
        parser = argparse.ArgumentParser(
            description="ModLocale 主入口，提供Extract、Extend、Decompile模式，以及映射规则管理和完整工作流",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""示例用法：

=== Extract模式示例 ===
python main.py extract "英文提取流程"
python main.py extract -h

=== Extend模式示例 ===
python main.py extend "已有中文src文件夹映射流程"
python main.py extend -h

=== Decompile模式示例 ===
python main.py decompile "反编译单个JAR文件"
python main.py decompile "反编译目录中所有JAR文件"
python main.py decompile "提取单个JAR文件内容"
python main.py decompile "提取目录中所有JAR文件内容"
python main.py decompile -h

=== 映射规则管理示例 ===
python main.py localization extract --source-dir ./src --output-file ./rules.yaml
python main.py localization generate-rules --english-file ./en.yaml --chinese-file ./zh.yaml --output-file ./rules.yaml
python main.py localization -h

=== 完整工作流示例 ===
python main.py workflow workflow --english-file ./en.yaml --chinese-file ./zh.yaml --source-dir ./src --output-dir ./output
python main.py workflow generate-rules --english-file ./en.yaml --chinese-file ./zh.yaml --output-file ./rules.yaml
python main.py workflow -h

=== 测试模式示例 ===
python main.py --test-mode "1,1,1"  # 测试Extract模式-简洁模式-提取英文
python main.py --test-mode "1,2,1"  # 测试Extract模式-完整模式-已有英文src
python main.py --test-mode "2,1,1"  # 测试Extend模式-简洁模式-中文映射到英文
python main.py --test-mode "4,1"  # 测试Decompile模式-反编译单个JAR文件
        """,
        )
        
        # 添加测试模式参数
        parser.add_argument(
            "--test-mode",
            type=str,
            help="测试模式：使用逗号分隔的数字序列模拟用户输入，例如：'1,1,1'",
            default=None
        )

        # 创建子命令解析器
        subparsers = parser.add_subparsers(dest="mode", help="要使用的模式", required=False)

        # Extract模式子命令
        extract_parser = subparsers.add_parser(
            "extract",
            help="执行Extract模式，用于提取字符串",
            description="Extract模式用于从src目录提取字符串，不进行翻译\n\n" \
            "操作模式：\n" \
            "  简化模式(交互式)：仅显示核心选项，自动检测并执行合适的子流程\n" \
            "  高级模式(交互式)：显示完整的四种子流程，允许手动选择\n" \
            "  命令行模式：直接指定子流程类型",
        )
        extract_parser.add_argument(
            "sub_flow",
            nargs="?",
            help="子流程类型，可选值：\n"  \
            "  简化模式可用：英文提取流程, 中文提取流程\n"  \
            "  高级模式可用：已有英文src文件夹提取流程, 没有英文src文件夹提取流程, 已有中文src文件夹提取流程, 没有中文src文件夹提取流程",
        )

        # Extend模式子命令
        extend_parser = subparsers.add_parser(
            "extend",
            help="执行Extend模式，用于映射字符串",
            description="Extend模式用于使用映射规则映射字符串，实现Chinese映射English",
        )
        extend_parser.add_argument(
            "sub_flow",
            nargs="?",
            help="子流程类型，可选值：\n"  \
            "  已有中文src文件夹映射流程\n"  \
            "  没有中文src文件夹映射流程\n"  \
            "  已有中文映射规则文件流程",
        )
        
        # Decompile模式子命令
        decompile_parser = subparsers.add_parser(
            "decompile",
            help="执行Decompile模式，用于反编译或提取JAR文件",
            description="Decompile模式用于反编译或提取JAR文件\n\n" \
            "操作模式：\n" \
            "  简化模式(交互式)：仅显示核心选项，自动检测并执行合适的子流程\n" \
            "  命令行模式：直接指定子流程类型",
        )
        decompile_parser.add_argument(
            "sub_flow",
            nargs="?",
            help="子流程类型，可选值：\n"  \
            "  反编译单个JAR文件\n"  \
            "  反编译目录中所有JAR文件\n"  \
            "  提取单个JAR文件内容\n"  \
            "  提取目录中所有JAR文件内容",
        )
        
        # 映射规则管理子命令
        localization_parser = subparsers.add_parser(
            "localization",
            help="执行映射规则管理，包括提取、处理未映射内容、冲突检测等",
            description="映射规则管理，用于处理翻译规则的提取、更新、冲突检测和解决\n\n" \
            "操作模式：\n" \
            "  命令行模式：直接指定子命令和参数",
            epilog="示例用法：\n" \
            "python main.py localization extract --source-dir ./src --output-file mappings.yaml\n" \
            "python main.py localization conflict --rule-file mappings.yaml --report conflict_report.txt",
        )
        localization_parser.add_argument(
            "subcommand",
            nargs="?",
            help="本地化子命令，可选值：extract, process-unmapped, conflict, generate-rules, update-rules",
        )
        localization_parser.add_argument(
            "args",
            nargs=argparse.REMAINDER,
            help="本地化子命令的参数",
        )
        
        # 完整工作流子命令
        workflow_parser = subparsers.add_parser(
            "workflow",
            help="执行完整工作流，包括生成规则、冲突检测、翻译回写等",
            description="完整工作流，用于执行从双语数据到翻译回写的完整流程\n\n" \
            "操作模式：\n" \
            "  命令行模式：直接指定子命令和参数",
            epilog="示例用法：\n" \
            "python main.py workflow generate-rules --english-file en.yaml --chinese-file zh.yaml --output-file rules.yaml\n" \
            "python main.py workflow workflow --english-file en.yaml --chinese-file zh.yaml --source-dir ./src --output-dir ./output",
        )
        workflow_parser.add_argument(
            "subcommand",
            nargs="?",
            help="工作流子命令，可选值：generate-rules, update-rules, workflow",
        )
        workflow_parser.add_argument(
            "args",
            nargs=argparse.REMAINDER,
            help="工作流子命令的参数",
        )
        
        # Bootstrap命令，用于从EN+ZH两套src生成Rich rules
        bootstrap_parser = subparsers.add_parser(
            "bootstrap",
            help="从EN+ZH两套src生成Rich rules",
            description="从EN+ZH两套src直接生成可回写的Rich rules文件\n\n" \
            "操作模式：\n" \
            "  命令行模式：直接指定参数",
            epilog="示例用法：\n" \
            "python main.py bootstrap --en-src ./source/English/src --zh-src ./source/Chinese/src --mod-id my-mod --out ./rules/rich_rules.yaml",
        )
        bootstrap_parser.add_argument(
            "--en-src",
            required=True,
            help="英文源码目录路径",
        )
        bootstrap_parser.add_argument(
            "--zh-src",
            required=True,
            help="中文源码目录路径",
        )
        bootstrap_parser.add_argument(
            "--mod-id",
            required=True,
            help="模组ID",
        )
        bootstrap_parser.add_argument(
            "--out",
            required=True,
            help="输出规则文件路径",
        )
        bootstrap_parser.add_argument(
            "--use-cache",
            action="store_true",
            help="是否使用缓存机制",
            default=True,
        )
        
        # Rules命令，用于规则管理
        rules_parser = subparsers.add_parser(
            "rules",
            help="规则管理子命令",
            description="规则管理命令，支持规则的列表、显示、设置、删除、验证、导入和导出\n\n" \
            "操作模式：\n" \
            "  命令行模式：直接指定子命令和参数",
            epilog="示例用法：\n" \
            "python main.py rules list --rules-file ./rules/rich_rules.yaml\n" \
            "python main.py rules show --rules-file ./rules/rich_rules.yaml --rule-id <rule-id>\n" \
            "python main.py rules validate --rules-file ./rules/rich_rules.yaml\n" \
            "python main.py rules export --rules-file ./rules/rich_rules.yaml --out ./simple_mapping.yaml --format simple",
        )
        rules_parser.add_argument(
            "subcommand",
            help="规则管理子命令，可选值：list, show, set, delete, validate, import, export",
            choices=["list", "show", "set", "delete", "validate", "import", "export"]
        )
        rules_parser.add_argument(
            "args",
            nargs=argparse.REMAINDER,
            help="规则管理子命令的参数",
        )

        # 解析命令行参数
        args = parser.parse_args()
        
        # 处理测试模式
        test_mode = args.test_mode
        if test_mode:
            # 模拟用户输入的全局变量
            global __test_input_sequence
            global __test_input_index
            __test_input_sequence = test_mode.split(',')
            __test_input_index = 0
            
            # 替换input函数，模拟用户输入
            import builtins
            original_input = builtins.input
            
            def mock_input(prompt):
                global __test_input_index
                if __test_input_index < len(__test_input_sequence):
                    user_input = __test_input_sequence[__test_input_index]
                    __test_input_index += 1
                    print(f"{prompt}{user_input}")
                    return user_input
                else:
                    print(f"{prompt}")
                    return "1"  # 默认值
            
            builtins.input = mock_input
            logger.info(f"测试模式已启用，输入序列：{test_mode}")
        
        # 检查sub_flow是否存在
        sub_flow_value = getattr(args, 'sub_flow', None)
        logger.info(f"命令行参数解析完成：mode={args.mode}, sub_flow={sub_flow_value}")

        result = None
        # 执行相应的模式
        if args.mode == "extract":
            logger.info("选择Extract模式")
            if args.sub_flow:
                # 直接执行指定的子流程
                logger.info(f"直接执行Extract子流程：{args.sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：Extract")
                print(f"流程：{args.sub_flow}")
                print("==========================================")
                result = run_extract_sub_flow(args.sub_flow, None)
            else:
                # 让用户选择子流程
                logger.info("用户未指定子流程，显示Extract子流程选择菜单")
                sub_flow = select_extract_sub_flow()
                logger.info(f"用户选择Extract子流程：{sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：Extract")
                print(f"流程：{sub_flow}")
                print("==========================================")
                result = run_extract_sub_flow(sub_flow, None)
        elif args.mode == "extend":
            logger.info("选择Extend模式")
            if args.sub_flow:
                # 直接执行指定的子流程
                logger.info(f"直接执行Extend子流程：{args.sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：Extend")
                print(f"流程：{args.sub_flow}")
                print("==========================================")
                result = run_extend_sub_flow(args.sub_flow, None)
            else:
                # 让用户选择子流程
                logger.info("用户未指定子流程，显示Extend子流程选择菜单")
                sub_flow = select_extend_sub_flow()
                logger.info(f"用户选择Extend子流程：{sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：Extend")
                print(f"流程：{sub_flow}")
                print("==========================================")
                result = run_extend_sub_flow(sub_flow, None)
        elif args.mode == "decompile":
            logger.info("选择Decompile模式")
            if args.sub_flow:
                # 直接执行指定的子流程
                logger.info(f"直接执行Decompile子流程：{args.sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：Decompile")
                print(f"流程：{args.sub_flow}")
                print("==========================================")
                result = run_decompile_sub_flow(args.sub_flow, None)
            else:
                # 让用户选择子流程
                logger.info("用户未指定子流程，显示Decompile子流程选择菜单")
                sub_flow = select_decompile_sub_flow()
                logger.info(f"用户选择Decompile子流程：{sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：Decompile")
                print(f"流程：{sub_flow}")
                print("==========================================")
                result = run_decompile_sub_flow(sub_flow, None)
        elif args.mode == "localization":
            logger.info("选择映射规则管理模式")
            print(f"\n执行配置：")
            print(f"模式：映射规则管理")
            print(f"子命令：{args.subcommand}")
            print(f"参数：{' '.join(args.args)}")
            print("==========================================")
            
            # 处理映射规则管理命令
            result = None
            try:
                if args.subcommand == "extract":
                    # 解析extract子命令参数
                    extract_parser = argparse.ArgumentParser(prog="localization extract")
                    extract_parser.add_argument("--source-dir", required=True, help="源目录路径")
                    extract_parser.add_argument("--processed-dir", help="已处理文件夹路径")
                    extract_parser.add_argument("--existing-rule", help="现有规则文件路径")
                    extract_parser.add_argument("--output-file", required=True, help="输出规则文件路径")
                    extract_parser.add_argument("--language", default="English", help="语言类型")
                    extract_args = extract_parser.parse_args(args.args)
                    
                    result = extract_mapping_rules(
                        source_dir=extract_args.source_dir,
                        processed_dir=extract_args.processed_dir,
                        existing_rule=extract_args.existing_rule,
                        output_file=extract_args.output_file,
                        language=extract_args.language
                    )
                    
                elif args.subcommand == "process-unmapped":
                    # 解析process-unmapped子命令参数
                    process_parser = argparse.ArgumentParser(prog="localization process-unmapped")
                    process_parser.add_argument("--rule-file", required=True, help="规则文件路径")
                    process_parser.add_argument("--unmapped-file", required=True, help="未映射内容文件路径")
                    process_parser.add_argument("--output-file", required=True, help="输出文件路径")
                    process_parser.add_argument("--language", default="English", help="语言类型")
                    process_args = process_parser.parse_args(args.args)
                    
                    result = process_unmapped_content(
                        rule_file=process_args.rule_file,
                        unmapped_file=process_args.unmapped_file,
                        output_file=process_args.output_file,
                        language=process_args.language
                    )
                    
                elif args.subcommand == "conflict":
                    # 解析conflict子命令参数
                    conflict_parser = argparse.ArgumentParser(prog="localization conflict")
                    conflict_parser.add_argument("--rule-file", required=True, help="规则文件路径")
                    conflict_parser.add_argument("--report", help="冲突报告文件路径")
                    conflict_args = conflict_parser.parse_args(args.args)
                    
                    result = detect_and_resolve_conflicts(
                        rule_file=conflict_args.rule_file,
                        report_file=conflict_args.report
                    )
                    
                else:
                    print(f"[ERROR] 未知的子命令: {args.subcommand}")
                    logger.error(f"未知的子命令: {args.subcommand}")
                    result = {"status": "error", "message": f"未知的子命令: {args.subcommand}"}
                    
            except SystemExit:
                # 处理argparse的退出
                result = {"status": "error", "message": "参数解析失败"}
            except Exception as e:
                logger.exception(f"映射规则管理执行过程中发生异常: {e}")
                print(f"[ERROR] 映射规则管理执行过程中发生异常: {e}")
                result = {"status": "error", "message": str(e)}
        elif args.mode == "workflow":
            logger.info("选择完整工作流模式")
            print(f"\n执行配置：")
            print(f"模式：完整工作流")
            print(f"子命令：{args.subcommand}")
            print(f"参数：{' '.join(args.args)}")
            print("==========================================")
            
            # 处理完整工作流命令
            result = None
            try:
                if args.subcommand == "generate-rules":
                    # 解析generate-rules子命令参数
                    generate_parser = argparse.ArgumentParser(prog="workflow generate-rules")
                    generate_parser.add_argument("--english-file", required=True, help="英文映射文件路径")
                    generate_parser.add_argument("--chinese-file", required=True, help="中文映射文件路径")
                    generate_parser.add_argument("--output-file", required=True, help="输出规则文件路径")
                    generate_parser.add_argument("--mod-id", default="", help="模组ID")
                    generate_args = generate_parser.parse_args(args.args)
                    
                    result = generate_translation_rules(
                        english_file=generate_args.english_file,
                        chinese_file=generate_args.chinese_file,
                        output_file=generate_args.output_file,
                        mod_id=generate_args.mod_id
                    )
                    
                elif args.subcommand == "update-rules":
                    # 解析update-rules子命令参数
                    update_parser = argparse.ArgumentParser(prog="workflow update-rules")
                    update_parser.add_argument("--rule-file", required=True, help="规则文件路径")
                    update_parser.add_argument("--new-content", required=True, help="新内容文件路径")
                    update_parser.add_argument("--output-file", required=True, help="输出规则文件路径")
                    update_parser.add_argument("--language", default="English", help="语言类型")
                    update_args = update_parser.parse_args(args.args)
                    
                    result = update_translation_rules(
                        rule_file=update_args.rule_file,
                        new_content=update_args.new_content,
                        output_file=update_args.output_file,
                        language=update_args.language
                    )
                    
                elif args.subcommand == "workflow":
                    # 解析workflow子命令参数
                    workflow_parser = argparse.ArgumentParser(prog="workflow workflow")
                    workflow_parser.add_argument("--english-file", required=True, help="英文映射文件路径")
                    workflow_parser.add_argument("--chinese-file", required=True, help="中文映射文件路径")
                    workflow_parser.add_argument("--source-dir", required=True, help="源目录路径")
                    workflow_parser.add_argument("--output-dir", required=True, help="输出目录路径")
                    workflow_parser.add_argument("--mod-id", default="", help="模组ID")
                    workflow_parser.add_argument("--language", default="English", help="语言类型")
                    workflow_args = workflow_parser.parse_args(args.args)
                    
                    result = run_complete_workflow(
                        english_file=workflow_args.english_file,
                        chinese_file=workflow_args.chinese_file,
                        source_dir=workflow_args.source_dir,
                        output_dir=workflow_args.output_dir,
                        mod_id=workflow_args.mod_id,
                        language=workflow_args.language
                    )
                    
                else:
                    print(f"[ERROR] 未知的子命令: {args.subcommand}")
                    logger.error(f"未知的子命令: {args.subcommand}")
                    result = {"status": "error", "message": f"未知的子命令: {args.subcommand}"}
                    
            except SystemExit:
                # 处理argparse的退出
                result = {"status": "error", "message": "参数解析失败"}
            except Exception as e:
                logger.exception(f"完整工作流执行过程中发生异常: {e}")
                print(f"[ERROR] 完整工作流执行过程中发生异常: {e}")
                result = {"status": "error", "message": str(e)}
        elif args.mode == "bootstrap":
            logger.info("选择bootstrap模式")
            print(f"\n执行配置：")
            print(f"模式：bootstrap")
            print(f"英文源码目录：{args.en_src}")
            print(f"中文源码目录：{args.zh_src}")
            print(f"模组ID：{args.mod_id}")
            print(f"输出文件：{args.out}")
            print(f"使用缓存：{args.use_cache}")
            print("===========================================")
            
            try:
                # 导入必要的模块
                from src.common.tree_sitter_utils import extract_ast_mappings
                from src.common.yaml_utils import generate_translation_rules, save_yaml_mappings, load_yaml_mappings, RuleConflictDetector
                from datetime import datetime
                import re
                
                # 从英文源码目录提取AST映射
                print(f"[INFO] 从英文源码目录提取映射规则：{args.en_src}")
                english_mappings = list(extract_ast_mappings(args.en_src, use_cache=args.use_cache))
                print(f"[OK] 成功提取英文映射规则 {len(english_mappings)} 条")
                
                # 从中文源码目录提取AST映射
                print(f"[INFO] 从中文源码目录提取映射规则：{args.zh_src}")
                chinese_mappings = list(extract_ast_mappings(args.zh_src, use_cache=args.use_cache))
                print(f"[OK] 成功提取中文映射规则 {len(chinese_mappings)} 条")
                
                # 使用occurrence_key进行双语对齐
                print(f"[INFO] 使用occurrence_key进行双语对齐...")
                
                # 创建英文映射字典，使用occurrence_key作为键
                english_dict = {item['id']: item for item in english_mappings}
                chinese_dict = {item['id']: item for item in chinese_mappings}
                
                # 找到共同的occurrence_key
                common_keys = set(english_dict.keys()) & set(chinese_dict.keys())
                print(f"[INFO] 找到 {len(common_keys)} 个共同的occurrence_key")
                
                # 生成对齐的双语映射
                aligned_en_mappings = []
                aligned_zh_mappings = []
                for key in common_keys:
                    aligned_en_mappings.append(english_dict[key])
                    aligned_zh_mappings.append(chinese_dict[key])
                
                # 生成翻译规则
                print(f"[INFO] 生成翻译规则...")
                success = generate_translation_rules(
                    aligned_en_mappings,
                    aligned_zh_mappings,
                    args.out,
                    args.mod_id
                )
                
                if success:
                    # 检测规则冲突
                    rules = load_yaml_mappings(args.out)
                    detector = RuleConflictDetector()
                    conflicts = detector.detect_all_conflicts(rules)
                    
                    conflict_info = {
                        "total_conflicts": conflicts['total_conflicts'],
                        "duplicate_ids": len(conflicts['duplicate_ids']),
                        "duplicate_originals": len(conflicts['duplicate_originals']),
                        "translation_conflicts": len(conflicts['translation_conflicts'])
                    }
                    
                    print(f"[OK] 翻译规则生成完成，输出文件：{args.out}")
                    print(f"[OK] 生成规则 {len(rules)} 条")
                    print(f"[INFO] 冲突检测结果：")
                    print(f"  - 总冲突数：{conflict_info['total_conflicts']}")
                    print(f"  - 重复ID：{conflict_info['duplicate_ids']}")
                    print(f"  - 重复原始字符串：{conflict_info['duplicate_originals']}")
                    print(f"  - 翻译冲突：{conflict_info['translation_conflicts']}")
                    
                    # 噪声识别和状态处理
                    print(f"[INFO] 进行噪声识别和状态处理...")
                    updated_rules = []
                    noise_count = 0
                    need_review_count = 0
                    
                    for rule in rules:
                        updated_rule = rule.copy()
                        original = rule['original']
                        translated = rule['translated']
                        
                        # 噪声识别
                        is_noise = False
                        noise_reason = ""
                        noise_score = 0.0
                        
                        # 检查是否为资源路径/ID/短令牌
                        if re.match(r'^[a-zA-Z0-9_]+$', original) and len(original) < 5:
                            is_noise = True
                            noise_reason = "短令牌"
                            noise_score = 0.8
                        elif '/' in original or '\\' in original:
                            is_noise = True
                            noise_reason = "资源路径"
                            noise_score = 0.9
                        elif original.startswith('$') or original.startswith('%'):
                            is_noise = True
                            noise_reason = "特殊标识符"
                            noise_score = 0.7
                        
                        if is_noise:
                            updated_rule['status'] = "SKIP"
                            updated_rule['noise'] = {
                                "reason": noise_reason,
                                "score": noise_score
                            }
                            noise_count += 1
                        else:
                            # 检查占位符一致性
                            original_placeholders = re.findall(r'[%]\w+|\$\{.*?\}|\{.*?\}', original)
                            translated_placeholders = re.findall(r'[%]\w+|\$\{.*?\}|\{.*?\}', translated)
                            
                            if len(original_placeholders) != len(translated_placeholders):
                                updated_rule['status'] = "NEED_REVIEW"
                                updated_rule['review_reason'] = f"占位符数量不一致: 原始 {len(original_placeholders)} 个，翻译 {len(translated_placeholders)} 个"
                                need_review_count += 1
                            else:
                                updated_rule['status'] = "translated"
                        
                        updated_rules.append(updated_rule)
                    
                    # 保存更新后的规则
                    save_yaml_mappings(updated_rules, args.out, version_control=True, mod_id=args.mod_id)
                    
                    print(f"[OK] 噪声识别和状态处理完成")
                    print(f"  - 噪声规则数：{noise_count}")
                    print(f"  - 需要审查的规则数：{need_review_count}")
                    print(f"  - 正常翻译规则数：{len(updated_rules) - noise_count - need_review_count}")
                    
                    result = {
                        "status": "success",
                        "message": "bootstrap命令执行成功",
                        "data": {
                            "output_path": args.out,
                            "english_mappings_count": len(english_mappings),
                            "chinese_mappings_count": len(chinese_mappings),
                            "common_keys_count": len(common_keys),
                            "generated_rules_count": len(updated_rules),
                            "noise_count": noise_count,
                            "need_review_count": need_review_count,
                            "conflicts": conflict_info
                        }
                    }
                else:
                    result = {
                        "status": "error",
                        "message": "生成翻译规则失败"
                    }
                
            except SystemExit:
                # 处理argparse的退出
                result = {"status": "error", "message": "参数解析失败"}
            except Exception as e:
                logger.exception(f"bootstrap命令执行过程中发生异常: {e}")
                print(f"[ERROR] bootstrap命令执行过程中发生异常: {e}")
                result = {"status": "error", "message": str(e)}
        elif args.mode == "rules":
            logger.info("选择rules模式")
            print(f"\n执行配置：")
            print(f"模式：rules")
            print(f"子命令：{args.subcommand}")
            print(f"参数：{' '.join(args.args)}")
            print("===========================================")
            
            try:
                from src.common.rules_store import RulesStore
                
                # 解析通用参数
                common_parser = argparse.ArgumentParser(add_help=False)
                common_parser.add_argument("--rules-file", required=True, help="规则文件路径")
                
                # 处理不同的子命令
                if args.subcommand == "list":
                    # 解析list子命令参数
                    list_parser = argparse.ArgumentParser(prog="rules list", parents=[common_parser])
                    list_parser.add_argument("--status", help="按状态过滤规则")
                    list_parser.add_argument("--file", help="按文件过滤规则")
                    list_args = list_parser.parse_args(args.args)
                    
                    # 创建RulesStore实例
                    rules_store = RulesStore(list_args.rules_file)
                    if rules_store.load_rules():
                        # 过滤规则
                        filtered_rules = rules_store.rules
                        if list_args.status:
                            filtered_rules = rules_store.get_rules_by_status(list_args.status)
                        if list_args.file:
                            filtered_rules = rules_store.get_rules_by_file(list_args.file)
                        
                        # 输出规则列表
                        print(f"[INFO] 规则列表 ({len(filtered_rules)} 条):")
                        for rule in filtered_rules:
                            print(f"ID: {rule['id']}")
                            print(f"  Original: {rule['original']}")
                            print(f"  Translated: {rule.get('translated', '')}")
                            print(f"  Status: {rule.get('status', 'untranslated')}")
                            print(f"  File: {rule.get('meta', {}).get('file', '')}")
                            print()
                        
                        result = {
                            "status": "success",
                            "message": f"成功列出 {len(filtered_rules)} 条规则",
                            "data": {
                                "total_rules": len(rules_store.rules),
                                "filtered_rules": len(filtered_rules)
                            }
                        }
                    else:
                        result = {
                            "status": "error",
                            "message": "加载规则文件失败"
                        }
                
                elif args.subcommand == "show":
                    # 解析show子命令参数
                    show_parser = argparse.ArgumentParser(prog="rules show", parents=[common_parser])
                    show_parser.add_argument("--rule-id", required=True, help="规则ID")
                    show_args = show_parser.parse_args(args.args)
                    
                    # 创建RulesStore实例
                    rules_store = RulesStore(show_args.rules_file)
                    if rules_store.load_rules():
                        # 获取规则
                        rule = rules_store.get_rule(show_args.rule_id)
                        if rule:
                            print(f"[INFO] 规则详情:")
                            print(f"ID: {rule['id']}")
                            print(f"Original: {rule['original']}")
                            print(f"Translated: {rule.get('translated', '')}")
                            print(f"Status: {rule.get('status', 'untranslated')}")
                            print(f"File: {rule.get('meta', {}).get('file', '')}")
                            print(f"Line: {rule.get('meta', {}).get('line', '')}")
                            print(f"Context: {rule.get('context', {})}")
                            print(f"Placeholders: {rule.get('placeholders', [])}")
                            print(f"Created At: {rule.get('created_at', '')}")
                            print(f"Updated At: {rule.get('updated_at', '')}")
                            print(f"Noise: {rule.get('noise', {})}")
                            print(f"Review Reason: {rule.get('review_reason', '')}")
                            
                            result = {
                                "status": "success",
                                "message": "成功显示规则详情",
                                "data": rule
                            }
                        else:
                            result = {
                                "status": "error",
                                "message": f"未找到规则: {show_args.rule_id}"
                            }
                    else:
                        result = {
                            "status": "error",
                            "message": "加载规则文件失败"
                        }
                
                elif args.subcommand == "set":
                    # 解析set子命令参数
                    set_parser = argparse.ArgumentParser(prog="rules set", parents=[common_parser])
                    set_parser.add_argument("--rule-id", required=True, help="规则ID")
                    set_parser.add_argument("--translated", help="翻译内容")
                    set_parser.add_argument("--status", help="规则状态")
                    set_args = set_parser.parse_args(args.args)
                    
                    # 创建RulesStore实例
                    rules_store = RulesStore(set_args.rules_file)
                    if rules_store.load_rules():
                        # 准备更新内容
                        updates = {}
                        if set_args.translated is not None:
                            updates["translated"] = set_args.translated
                        if set_args.status:
                            updates["status"] = set_args.status
                        
                        if updates:
                            # 更新规则
                            if rules_store.update_rule(set_args.rule_id, updates):
                                # 保存更新后的规则
                                if rules_store.save_rules():
                                    result = {
                                        "status": "success",
                                        "message": f"成功更新规则: {set_args.rule_id}"
                                    }
                                else:
                                    result = {
                                        "status": "error",
                                        "message": "保存规则文件失败"
                                    }
                            else:
                                result = {
                                    "status": "error",
                                    "message": f"未找到规则: {set_args.rule_id}"
                                }
                        else:
                            result = {
                                "status": "error",
                                "message": "没有提供更新内容"
                            }
                    else:
                        result = {
                            "status": "error",
                            "message": "加载规则文件失败"
                        }
                
                elif args.subcommand == "delete":
                    # 解析delete子命令参数
                    delete_parser = argparse.ArgumentParser(prog="rules delete", parents=[common_parser])
                    delete_parser.add_argument("--rule-id", required=True, help="规则ID")
                    delete_args = delete_parser.parse_args(args.args)
                    
                    # 创建RulesStore实例
                    rules_store = RulesStore(delete_args.rules_file)
                    if rules_store.load_rules():
                        # 删除规则
                        if rules_store.delete_rule(delete_args.rule_id):
                            # 保存更新后的规则
                            if rules_store.save_rules():
                                result = {
                                    "status": "success",
                                    "message": f"成功删除规则: {delete_args.rule_id}"
                                }
                            else:
                                result = {
                                    "status": "error",
                                    "message": "保存规则文件失败"
                                }
                        else:
                            result = {
                                "status": "error",
                                "message": f"未找到规则: {delete_args.rule_id}"
                            }
                    else:
                        result = {
                            "status": "error",
                            "message": "加载规则文件失败"
                        }
                
                elif args.subcommand == "validate":
                    # 解析validate子命令参数
                    validate_parser = argparse.ArgumentParser(prog="rules validate", parents=[common_parser])
                    validate_args = validate_parser.parse_args(args.args)
                    
                    # 创建RulesStore实例
                    rules_store = RulesStore(validate_args.rules_file)
                    if rules_store.load_rules():
                        # 验证规则
                        errors = rules_store.validate_rules()
                        
                        if errors:
                            print(f"[ERROR] 发现 {len(errors)} 个错误:")
                            for error in errors:
                                print(f"  - {error}")
                            
                            result = {
                                "status": "error",
                                "message": f"规则验证失败，发现 {len(errors)} 个错误",
                                "data": {
                                    "errors": errors
                                }
                            }
                        else:
                            print(f"[OK] 规则验证通过，未发现错误")
                            
                            result = {
                                "status": "success",
                                "message": "规则验证通过",
                                "data": {
                                    "total_rules": len(rules_store.rules)
                                }
                            }
                    else:
                        result = {
                            "status": "error",
                            "message": "加载规则文件失败"
                        }
                
                elif args.subcommand == "import":
                    # 解析import子命令参数
                    import_parser = argparse.ArgumentParser(prog="rules import", parents=[common_parser])
                    import_parser.add_argument("--source-file", required=True, help="源规则文件路径")
                    import_parser.add_argument("--merge", action="store_true", help="是否合并到现有规则，否则替换")
                    import_args = import_parser.parse_args(args.args)
                    
                    # 创建RulesStore实例
                    rules_store = RulesStore(import_args.rules_file)
                    if rules_store.load_rules():
                        # 导入规则
                        import_result = rules_store.import_rules(import_args.source_file, import_args.merge)
                        
                        # 保存更新后的规则
                        if rules_store.save_rules():
                            result = {
                                "status": "success",
                                "message": import_result["message"],
                                "data": import_result
                            }
                        else:
                            result = {
                                "status": "error",
                                "message": "保存规则文件失败"
                            }
                    else:
                        result = {
                            "status": "error",
                            "message": "加载规则文件失败"
                        }
                
                elif args.subcommand == "export":
                    # 解析export子命令参数
                    export_parser = argparse.ArgumentParser(prog="rules export", parents=[common_parser])
                    export_parser.add_argument("--out", required=True, help="输出文件路径")
                    export_parser.add_argument("--format", default="rich", choices=["rich", "simple"], help="导出格式")
                    export_args = export_parser.parse_args(args.args)
                    
                    # 创建RulesStore实例
                    rules_store = RulesStore(export_args.rules_file)
                    if rules_store.load_rules():
                        # 导出规则
                        if rules_store.export_rules(export_args.out, export_args.format):
                            result = {
                                "status": "success",
                                "message": f"成功导出规则到 {export_args.out}",
                                "data": {
                                    "exported_rules": len(rules_store.rules),
                                    "format": export_args.format
                                }
                            }
                        else:
                            result = {
                                "status": "error",
                                "message": "导出规则失败"
                            }
                    else:
                        result = {
                            "status": "error",
                            "message": "加载规则文件失败"
                        }
                
                else:
                    result = {
                        "status": "error",
                        "message": f"未知的子命令: {args.subcommand}"
                    }
                
            except SystemExit:
                # 处理argparse的退出
                result = {"status": "error", "message": "参数解析失败"}
            except Exception as e:
                logger.exception(f"rules命令执行过程中发生异常: {e}")
                print(f"[ERROR] rules命令执行过程中发生异常: {e}")
                result = {"status": "error", "message": str(e)}
        else:
            # 没有指定模式，使用交互式菜单
            logger.info("未指定模式，显示主菜单")
            mode = select_main_mode()
            logger.info(f"用户选择主模式：{mode}")

            if mode == "1":
                # Extract模式
                sub_flow = select_extract_sub_flow()
                logger.info(f"用户选择Extract子流程：{sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：Extract")
                print(f"流程：{sub_flow}")
                print("==========================================")
                result = run_extract_sub_flow(sub_flow, None)
            elif mode == "2":
                # Extend模式
                sub_flow = select_extend_sub_flow()
                logger.info(f"用户选择Extend子流程：{sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：Extend")
                print(f"流程：{sub_flow}")
                print("==========================================")
                result = run_extend_sub_flow(sub_flow, None)
            elif mode == "3":
                # Decompile模式
                sub_flow = select_decompile_sub_flow()
                logger.info(f"用户选择Decompile子流程：{sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：Decompile")
                print(f"流程：{sub_flow}")
                print("==========================================")
                result = run_decompile_sub_flow(sub_flow, None)
            elif mode == "4":
                # 文件管理模式
                sub_flow = select_file_management_sub_flow()
                logger.info(f"用户选择文件管理子流程：{sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：文件管理")
                print(f"流程：{sub_flow}")
                print("===========================================")
                result = run_file_management_sub_flow(sub_flow, None)
            elif mode == "5":
                # 映射规则管理
                logger.info("选择映射规则管理模式")
                sub_flow = select_localization_sub_flow()
                logger.info(f"用户选择映射规则管理子流程：{sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：映射规则管理")
                print(f"流程：{sub_flow}")
                print("===========================================")
                result = run_localization_sub_flow(sub_flow, None)
            elif mode == "6":
                # 完整工作流
                logger.info("选择完整工作流模式")
                sub_flow = select_workflow_sub_flow()
                logger.info(f"用户选择完整工作流子流程：{sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：完整工作流")
                print(f"流程：{sub_flow}")
                print("===========================================")
                result = run_workflow_sub_flow(sub_flow, None)
        
        # 处理执行结果
        if result and isinstance(result, dict):
            logger.info(f"模式执行完成：{result['status']}")
            if result.get("data", {}).get("output_path"):
                # 根据模式判断语言类型
                if args.mode == "extract" or mode == "1":
                    # Extract模式
                    language = "English" if "英文" in result.get("sub_flow", "") else "Chinese"
                    show_output_guide(result["data"]["output_path"], "Extract", language)
                elif args.mode == "extend" or mode == "2":
                    # Extend模式
                    language = "English" if "中文→英文" in result.get("sub_flow", "") else "Chinese"
                    show_output_guide(result["data"]["output_path"], "Extend", language)
        
        logger.info("工具执行完成，退出")
    except Exception as e:
        logger.exception(f"工具执行过程中发生异常: {e}")
        print(f"[ERROR] 工具执行过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
