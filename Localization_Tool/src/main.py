#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地化工具主入口

提供Extract、Extend和Decompile三种模式的选择和执行。

使用方法：
python main.py [模块名称] [参数]

模块列表：
- extract: 执行Extract模式，用于提取字符串
- extend: 执行Extend模式，用于映射字符串
- decompile: 执行Decompile模式，用于反编译或提取JAR文件

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

# 设置全局日志记录器
logger = setup_logger("localization_tool")


# 修改select_main_mode函数，移除高级模式的重复选项
def select_main_mode() -> str:
    """
    让用户选择主模式(Extract或Extend或Decompile或文件管理模式)

    Returns:
        str: 选择的模式编号("1"、"2"、"3"或"4")
    """
    print("===========================================")
    print("             本地化工具")
    print("===========================================")
    print("请选择本地化模式：")
    print("1. Extract模式(仅提取字符串，默认简洁模式)")
    print("2. Extend模式(执行映射流程，默认简洁模式)")
    print("3. Decompile模式(执行JAR文件反编译/提取)")
    print("4. 文件管理模式(文件夹创建、重命名、备份恢复)")
    print("===========================================")

    while True:
        choice = input("输入数字(1/2/3/4，直接回车默认选1)：").strip()
        if not choice:  # 直接回车，默认选1
            return "1"
        elif choice in ["1", "2", "3", "4"]:
            return choice
        print(f"输入无效，请输入正确的数字(1/2/3/4)！")


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
    print("                本地化工具")
    print("==========================================")
    print("📌 【前置检查】请确认已按以下结构存放文件：")
    print("Localization_Tool/File/")
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
    print("\n# 本地化工具 - 友好用户引导手册")
    print("(适配终端交互，全程嵌入式引导，通俗易懂+步骤化，降低操作门槛)")
    print("\n## 🌟 欢迎使用本地化工具！")
    print("在开始操作前，请先完成「文件夹准备」(30秒即可搞定)，工具会严格按照你存放的文件夹结构识别文件，")
    print("输出内容也会统一整理到指定文件夹，全程无需手动翻找～")
    print("\n## 📂 第一步：主目录结构准备(必看！)")
    print("请先在Localization_Tool目录下创建「File」文件夹，并按以下结构存放文件夹，")
    print("**命名必须严格一致**(工具自动识别，错字会导致检测失败)：")
    print("""```
Localization_Tool/ (工具主目录)
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
    print("| Extract-提取英文 | Localization_Tool/File/source/English/src 或 Localization_Tool/File/source/English/jars | 优先读src，无则反编译jar，结果存到Localization_Tool/File/output/Extract_English |")
    print("| Extract-提取中文 | Localization_Tool/File/source/Chinese/src 或 Localization_Tool/File/source/Chinese/jars | 优先读src，无则反编译jar，结果存到Localization_Tool/File/output/Extract_Chinese |")
    print("| Extend-中映射英 | Localization_Tool/File/source/Chinese/xxx + Localization_Tool/File/rule/Chinese/xxx | 优先读映射规则，无则读src/jars，结果存到Localization_Tool/File/output/Extend_Zh2En |")
    print("| Extend-英映射中 | Localization_Tool/File/source/English/xxx + Localization_Tool/File/rule/English/xxx | 优先读映射规则，无则读src/jars，结果存到Localization_Tool/File/output/Extend_En2Zh |")
    print("\n💡 提示：Localization_Tool/File 目录会在工具启动时自动创建！")
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
    logger.info("             本地化工具")
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
            description="本地化工具主入口，提供Extract、Extend和Decompile三种模式",
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
                print("==========================================")
                result = run_file_management_sub_flow(sub_flow, None)
        
        # 处理执行结果
        if result:
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
