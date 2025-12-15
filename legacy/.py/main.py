#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地化工具主入口

提供Extract和Extend两种模式的选择和执行。

使用方法：
python main.py [模块名称] [参数]

模块列表：
- extract: 执行Extract模式，用于提取字符串
- extend: 执行Extend模式，用于映射字符串

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

# 设置全局日志记录器
logger = setup_logger("localization_tool")


def select_main_mode() -> str:
    """
    让用户选择主模式(Extract或Extend或高级模式)

    Returns:
        str: 选择的模式编号("1"、"2"或"3")
    """
    print("==========================================")
    print("             本地化工具")
    print("==========================================")
    print("请选择本地化模式：")
    print("1. Extract模式(仅提取字符串，默认简洁模式)")
    print("2. Extend模式(执行映射流程，默认简洁模式)")
    print("3. 高级模式(自定义提取/映射，可配置粒度/主体)")
    print("==========================================")

    while True:
        choice = input("输入数字(1/2/3，直接回车默认选1)：").strip()
        if not choice:  # 直接回车，默认选1
            return "1"
        elif choice in ["1", "2", "3"]:
            return choice
        print(f"输入无效，请输入正确的数字(1/2/3)！")


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
        print("✅ 检测到source/English/jar文件夹，将反编译未汉化jar包")
    else:
        print("❌ 未检测到source/English/src或jar文件夹，请先准备源文件")
    
    print("📤 提取结果将保存到：主目录/Localization_File/output/Extract_English/")
    print("   包含：字符串映射规则文件 + 流程报告 + mod_info.json")
    print("==========================================")
    print("请选择提取语言：")
    print("1. 提取英文(优先检测src/无则反编译未汉化jar)")
    print("2. 提取中文(优先检测src/无则反编译已汉化jar)")
    print("==========================================")

    while True:
        lang_choice = input("输入数字(1/2，直接回车默认选1)：").strip()
        if not lang_choice:  # 直接回车，默认选1
            return "英文提取流程"
        elif lang_choice in ["1", "2"]:
            return "英文提取流程" if lang_choice == "1" else "中文提取流程"
        print(f"输入无效，请输入正确的数字(1/2)！")


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
    print("            Extend模式 - 简洁模式")
    print("==========================================")
    
    # 显示检测结果
    print("🔍 正在检测主目录下的source和rule文件夹...")
    rule_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "rule")
    if os.path.exists(rule_path):
        print("✅ 检测到rule文件夹，将优先使用映射规则文件")
    else:
        print("❌ 未检测到rule文件夹，将直接检测src/jar文件夹")
    
    if detection_result["chinese_src"] or detection_result["chinese_jar"]:
        print("✅ 检测到source/Chinese文件夹，可进行中文相关映射")
    if detection_result["english_src"] or detection_result["english_jar"]:
        print("✅ 检测到source/English文件夹，可进行英文相关映射")
    
    print("📤 映射结果将保存到：主目录/Localization_File/output/Extend_xxx/")
    print("   包含：映射后的源文件夹 + 字符串映射规则文件 + 流程报告 + mod_info.json")
    print("==========================================")
    
    print("请选择映射方向：")
    print("1. 中文映射到英文(优先检测映射规则/无则自动检测src/jar)")
    print("2. 英文映射到中文(优先检测映射规则/无则自动检测src/jar)")
    print("==========================================")
    
    while True:
        direction_choice = input("输入数字(1/2，直接回车默认选1)：").strip()
        if not direction_choice:  # 直接回车，默认选1
            return "已有中文src文件夹映射流程"
        elif direction_choice in ["1", "2"]:
            mapping_direction = "中文→英文" if direction_choice == "1" else "英文→中文"
            
            # 显示执行信息
            print(f"\n==========================================")
            print(f"        Extend模式 - [{mapping_direction}] 简洁模式")
            print("==========================================")
            print("正在执行：优先检测映射规则文件夹→检测src文件夹→无则反编译jar")
            print("流程步骤：创建文件夹→重命名模组→恢复备份→字符串映射...")
            
            if direction_choice == "1":
                return "已有中文src文件夹映射流程"
            else:
                return "已有英文src文件夹映射流程"
        print(f"输入无效，请输入正确的数字(1/2)！")


def toggle_advanced_mode() -> None:
    """
    切换高级模式的开启/关闭状态
    """
    global ADVANCED_MODE_ENABLED
    ADVANCED_MODE_ENABLED = not ADVANCED_MODE_ENABLED
    set_setting("advanced_mode_enabled", ADVANCED_MODE_ENABLED)
    status = "开启" if ADVANCED_MODE_ENABLED else "关闭"
    print(f"\n✅ 高级模式已{status}！")


def set_main_language() -> None:
    """
    设置主体语言
    """
    global MAIN_LANGUAGE
    
    print("\n==========================================")
    print("        高级模式 - 主体语言设置")
    print("==========================================")
    print(f"当前主体语言：{MAIN_LANGUAGE}")
    print("请选择主体语言：")
    print("1. 全部")
    print("2. 中文")
    print("3. 英文")
    print("==========================================")
    
    while True:
        choice = input("输入数字(1/2/3，直接回车默认选1)：").strip()
        if not choice:  # 直接回车，默认选1
            choice = "1"
        if choice in ["1", "2", "3"]:
            languages = ["全部", "中文", "英文"]
            MAIN_LANGUAGE = languages[int(choice) - 1]
            set_setting("main_language", MAIN_LANGUAGE)
            print(f"✅ 主体语言已设置为：{MAIN_LANGUAGE}！")
            break
        print(f"输入无效，请输入正确的数字(1/2/3)！")


def toggle_process_granularity() -> None:
    """
    切换流程粒度的开启/关闭状态
    """
    global PROCESS_GRANULARITY_ENABLED
    PROCESS_GRANULARITY_ENABLED = not PROCESS_GRANULARITY_ENABLED
    set_setting("process_granularity_enabled", PROCESS_GRANULARITY_ENABLED)
    status = "开启" if PROCESS_GRANULARITY_ENABLED else "关闭"
    print(f"\n✅ 流程粒度控制已{status}！")


def toggle_precheck_mechanism() -> None:
    """
    切换前置检查的开启/关闭状态
    """
    global PRECHECK_MECHANISM_ENABLED
    global SHOW_WELCOME_GUIDE
    
    PRECHECK_MECHANISM_ENABLED = not PRECHECK_MECHANISM_ENABLED
    SHOW_WELCOME_GUIDE = PRECHECK_MECHANISM_ENABLED
    set_setting("precheck_mechanism_enabled", PRECHECK_MECHANISM_ENABLED)
    set_setting("show_welcome_guide", SHOW_WELCOME_GUIDE)
    status = "开启" if PRECHECK_MECHANISM_ENABLED else "关闭"
    print(f"\n✅ 前置检查机制已{status}！")


def advanced_settings() -> None:
    """
    高级模式CLI设置系统主入口
    """
    while True:
        print("\n==========================================")
        print("        高级模式 - CLI设置系统")
        print("==========================================")
        
        # 显示高级模式主开关状态
        status = "开启" if ADVANCED_MODE_ENABLED else "关闭"
        print(f"1. 高级模式主开关：{status}")
        
        # 仅在高级模式开启状态下，显示并允许配置其他三个分支选项
        if ADVANCED_MODE_ENABLED:
            print(f"2. 主体语言设置：{MAIN_LANGUAGE}")
            print(f"3. 流程粒度控制：{'开启' if PROCESS_GRANULARITY_ENABLED else '关闭'}")
            print(f"4. 前置检查机制：{'开启' if PRECHECK_MECHANISM_ENABLED else '关闭'}")
        
        print("5. 返回主菜单")
        print("==========================================")
        
        choice = input("输入数字(1-5，直接回车默认选5)：").strip()
        if not choice:  # 直接回车，默认选5
            choice = "5"
        
        if choice == "1":
            # 切换高级模式主开关
            toggle_advanced_mode()
        elif choice == "2" and ADVANCED_MODE_ENABLED:
            # 设置主体语言
            set_main_language()
        elif choice == "3" and ADVANCED_MODE_ENABLED:
            # 切换流程粒度控制
            toggle_process_granularity()
        elif choice == "4" and ADVANCED_MODE_ENABLED:
            # 切换前置检查机制
            toggle_precheck_mechanism()
        elif choice == "5":
            # 返回主菜单
            break
        else:
            print(f"输入无效，请输入正确的数字(1-5)！")


def select_cli_settings(subject: str = "", submode: str = "", granularity: str = "") -> None:
    """
    让用户选择CLI设置选项(关闭前置检查、关闭完成工作后自动打开输出文件夹)
    
    Args:
        subject: 操作主体
        submode: 子模式
        granularity: 流程粒度
    """
    # 构建标题
    title_suffix = f" [{subject}-{submode}-{granularity}]" if subject and submode and granularity else ""
    
    # 显示CLI设置选项组
    print(f"\n==========================================")
    print(f"        高级模式{title_suffix} CLI设置")
    print("==========================================")
    print("请选择CLI设置选项(默认：关闭前置检查，自动打开输出文件夹)：")
    print("1. 关闭前置检查(直接进入主菜单，适合自动化测试)")
    print("2. 开启前置检查(显示欢迎引导和文件夹结构说明)")
    print("3. 关闭完成工作后自动打开输出文件夹")
    print("4. 开启完成工作后自动打开输出文件夹")
    print("==========================================")
    
    # 重置为默认值
    global SHOW_WELCOME_GUIDE
    global AUTO_OPEN_OUTPUT_FOLDER
    SHOW_WELCOME_GUIDE = False  # 默认关闭前置检查
    AUTO_OPEN_OUTPUT_FOLDER = True  # 默认自动打开输出文件夹
    
    # 循环获取用户输入，直到输入有效
    while True:
        cli_choice = input("输入数字(1/2/3/4，直接回车默认选1,4)：").strip()
        if not cli_choice:  # 直接回车，使用默认设置
            break
        
        # 检查输入是否有效
        if cli_choice in ["1", "2", "3", "4"]:
            if cli_choice == "1":
                SHOW_WELCOME_GUIDE = False
            elif cli_choice == "2":
                SHOW_WELCOME_GUIDE = True
            elif cli_choice == "3":
                AUTO_OPEN_OUTPUT_FOLDER = False
            elif cli_choice == "4":
                AUTO_OPEN_OUTPUT_FOLDER = True
            break
        else:
            print(f"输入无效，请输入正确的数字(1/2/3/4)！")
    
    # 保存设置
    set_setting("show_welcome_guide", SHOW_WELCOME_GUIDE)
    set_setting("auto_open_output_folder", AUTO_OPEN_OUTPUT_FOLDER)


def select_advanced_mode() -> str:
    """
    高级模式入口，进入CLI设置系统
    
    Returns:
        str: 选择的子流程
    """
    # 进入高级模式CLI设置系统
    advanced_settings()
    
    # CLI设置完成后，重新显示主菜单并获取用户选择
    mode = select_main_mode()
    
    # 根据用户选择的模式，获取对应的子流程
    if mode == "1":
        # Extract模式
        return select_extract_sub_flow()
    elif mode == "2":
        # Extend模式
        return select_extend_sub_flow()
    else:
        # 再次进入高级模式CLI设置系统
        return select_advanced_mode()


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
    
    # 定义 Localization_File 目录路径(在工具根目录的上级目录)
    main_root = os.path.dirname(tool_root)
    localization_file_path = os.path.join(main_root, "Localization_File")
    
    # 定义 Localization_File 下的必要文件夹结构 - 严格按照框架文档
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
    
    # 从配置中获取其他目录路径
    rule_path = get_directory("rules")
    output_path = get_directory("output")
    logs_path = get_directory("logs")
    
    # 定义工具内部的必要文件夹结构 - 严格按照框架文档
    tool_folders = [
        # 工具内部的规则目录
        os.path.join(rule_path, "English"),
        os.path.join(rule_path, "Chinese"),
        # 工具内部的输出和日志目录
        output_path,
        logs_path
    ]
    
    try:
        # 创建 Localization_File 目录结构
        for folder in localization_folders:
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
                logger.info(f"创建文件夹: {folder}")
        
        # 创建工具内部目录结构
        for folder in tool_folders:
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


def show_welcome_guide():
    """
    显示欢迎信息和文件夹结构引导
    """
    print("==========================================")
    print("                本地化工具")
    print("==========================================")
    print("📌 【前置检查】请确认已按以下结构存放文件：")
    print("主目录/Localization_File/")
    print("├─ source/English/(src/jar) ｜ 英文源文件")
    print("├─ source/Chinese/(src/jar) ｜ 中文源文件")
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
    print("请先在电脑任意位置创建一个「主目录」(建议命名：`Tool`)，并按以下结构存放文件夹，")
    print("**命名必须严格一致**(工具自动识别，错字会导致检测失败)：")
    print("```")
    print("主目录/ (例如：d:/Poki/Tool)")
    print("├─ Localization_File/ (源文件存放区，工具自动创建！)")
    print("│  ├─ source/ (源文件存放区)")
    print("│  │  ├─ English/ (英文源文件)")
    print("│  │  │  ├─ src/ (可选：已有英文源码文件夹，放待提取的英文文本文件)")
    print("│  │  │  └─ jar/ (可选：待反编译的英文jar包，未汉化版)")
    print("│  │  └─ Chinese/ (中文源文件)")
    print("│  │     ├─ src/ (可选：已有中文化源码文件夹，放待提取/映射的中文文本文件)")
    print("│  │     └─ jar/ (可选：待反编译的中文jar包，已汉化版)")
    print("│  ├─ rule/ (映射规则存放区，Extend模式专属，可选)")
    print("│  │  ├─ English/ (英文映射规则文件)")
    print("│  │  └─ Chinese/ (中文映射规则文件)")
    print("│  └─ output/ (工具自动生成，无需创建！所有提取/映射结果+报告都在这里)")
    print("└─ Localization_Tool/ (工具主目录)")
    print("   ├─ src/ (工具源代码)")
    print("   ├─ config/ (配置文件)")
    print("   ├─ logs/ (日志文件)")
    print("   └─ scripts/ (启动脚本)")
    print("```")
    print("\n### ✨ 核心引导：不同模式对应哪些文件夹？")
    print("| 操作模式       | 需准备的源文件夹       | 工具会自动处理什么？|")
    print("|----------------|------------------------|---------------------------------------------|")
    print("| Extract-提取英文 | Localization_File/source/English/src 或 Localization_File/source/English/jar | 优先读src，无则反编译jar，结果存到Localization_File/output/Extract_English |")
    print("| Extract-提取中文 | Localization_File/source/Chinese/src 或 Localization_File/source/Chinese/jar | 优先读src，无则反编译jar，结果存到Localization_File/output/Extract_Chinese |")
    print("| Extend-中映射英 | Localization_File/source/Chinese/xxx + Localization_File/rule/Chinese/xxx | 优先读映射规则，无则读src/jar，结果存到Localization_File/output/Extend_Zh2En |")
    print("| Extend-英映射中 | Localization_File/source/English/xxx + Localization_File/rule/English/xxx | 优先读映射规则，无则读src/jar，结果存到Localization_File/output/Extend_En2Zh |")
    print("\n💡 提示：Localization_File 目录会在工具启动时自动创建！")
    print("\n输入「start」进入主菜单，输入「help」重新查看引导：")


def check_source_folders() -> dict:
    """
    检查source文件夹下的src和jar子文件夹
    
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
        if os.path.exists(os.path.join(english_path, "jar")):
            result["english_jar"] = True
    
    # 检查中文源文件夹
    chinese_path = os.path.join(source_path, "Chinese")
    if os.path.exists(chinese_path):
        if os.path.exists(os.path.join(chinese_path, "src")):
            result["chinese_src"] = True
        if os.path.exists(os.path.join(chinese_path, "jar")):
            result["chinese_jar"] = True
    
    return result


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
        mod_name = '_'.join(os.path.basename(output_path).split('_')[2:])
        print(f"   1. {language}_mappings.json - 字符串映射规则文件(可用于Extend模式)")
        print(f"   2. {language}_mappings.yaml - 字符串映射规则文件(可用于Extend模式)")
        # 从输出路径中提取时间戳
        timestamp = os.path.basename(output_path).split('_')[0] + '_' + os.path.basename(output_path).split('_')[1]
        print(f"   3. extract_{timestamp}_report.json - 流程报告(含检测结果、执行步骤、耗时)")
        print(f"   4. mod_info.json - mod信息文件(可用于Extend模式)")
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

# 高级模式配置全局变量
ADVANCED_MODE_ENABLED = get_setting("advanced_mode_enabled")  # 高级模式主开关：False-关闭，True-开启
MAIN_LANGUAGE = get_setting("main_language")  # 主体语言设置：全部/中文/英文
PROCESS_GRANULARITY_ENABLED = get_setting("process_granularity_enabled")  # 流程粒度控制：False-关闭，True-开启
PRECHECK_MECHANISM_ENABLED = get_setting("precheck_mechanism_enabled")  # 前置检查机制：False-关闭，True-开启

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
        
        # 获取基础路径
        base_path = get_directory("tool_root")
        if not base_path:
            # 回退到当前脚本的项目根目录
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 检查项目结构
        if not check_project_structure():
            return
        
        # 导入目录管理函数
        from src.common.file_utils import cleanup_nested_src_directories, compare_source_with_backup, fix_source_directory
        
        # 获取Localization_File目录路径
        localization_file_path = os.path.join(os.path.dirname(base_path), "Localization_File")
        source_path = os.path.join(localization_file_path, "source")
        source_backup_path = os.path.join(localization_file_path, "source_backup")
        
        
        # 解析命令行参数
        parser = argparse.ArgumentParser(
            description="本地化工具主入口，提供Extract和Extend两种模式",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""示例用法：

=== Extract模式示例 ===
python main.py extract "英文提取流程"
python main.py extract -h

=== Extend模式示例 ===
python main.py extend "已有中文src文件夹映射流程"
python main.py extend -h

=== 测试模式示例 ===
python main.py --test-mode "1,1,1"  # 测试Extract模式-简洁模式-提取英文
python main.py --test-mode "1,2,1"  # 测试Extract模式-完整模式-已有英文src
python main.py --test-mode "2,1,1"  # 测试Extend模式-简洁模式-中文映射到英文
python main.py --test-mode "3,1,1,1"  # 测试高级模式-全部功能-Extract子模式
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
            description="Extract模式用于从src目录提取字符串，不进行翻译\n\n" 
            "操作模式：\n" 
            "  简化模式(交互式)：仅显示核心选项，自动检测并执行合适的子流程\n" 
            "  高级模式(交互式)：显示完整的四种子流程，允许手动选择\n" 
            "  命令行模式：直接指定子流程类型",
        )
        extract_parser.add_argument(
            "sub_flow",
            nargs="?",
            help="子流程类型，可选值：\n"  
            "  简化模式可用：英文提取流程, 中文提取流程\n"  
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
            help="子流程类型，可选值：\n"  
            "  已有中文src文件夹映射流程\n"  
            "  没有中文src文件夹映射流程\n"  
            "  已有中文映射规则文件流程",
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

        logger.info(f"工具基础路径：{base_path}")

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
                result = run_extract_sub_flow(args.sub_flow, base_path)
            else:
                # 让用户选择子流程
                logger.info("用户未指定子流程，显示Extract子流程选择菜单")
                sub_flow = select_extract_sub_flow()
                logger.info(f"用户选择Extract子流程：{sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：Extract")
                print(f"流程：{sub_flow}")
                print("==========================================")
                result = run_extract_sub_flow(sub_flow, base_path)
        elif args.mode == "extend":
            logger.info("选择Extend模式")
            if args.sub_flow:
                # 直接执行指定的子流程
                logger.info(f"直接执行Extend子流程：{args.sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：Extend")
                print(f"流程：{args.sub_flow}")
                print("==========================================")
                result = run_extend_sub_flow(args.sub_flow, base_path)
            else:
                # 让用户选择子流程
                logger.info("用户未指定子流程，显示Extend子流程选择菜单")
                sub_flow = select_extend_sub_flow()
                logger.info(f"用户选择Extend子流程：{sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：Extend")
                print(f"流程：{sub_flow}")
                print("==========================================")
                result = run_extend_sub_flow(sub_flow, base_path)
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
                result = run_extract_sub_flow(sub_flow, base_path)
            elif mode == "2":
                # Extend模式
                sub_flow = select_extend_sub_flow()
                logger.info(f"用户选择Extend子流程：{sub_flow}")
                print(f"\n执行配置：")
                print(f"模式：Extend")
                print(f"流程：{sub_flow}")
                print("==========================================")
                result = run_extend_sub_flow(sub_flow, base_path)
            else:
                # 高级模式
                sub_flow = select_advanced_mode()
                logger.info(f"用户选择高级模式子流程：{sub_flow}")
                # 根据子流程类型选择对应的run函数
                if sub_flow in ["英文提取流程", "中文提取流程", "已有英文src文件夹提取流程", "没有英文src文件夹提取流程", "已有中文src文件夹提取流程", "没有中文src文件夹提取流程"]:
                    print(f"\n执行配置：")
                    print(f"模式：Extract(高级模式)")
                    print(f"流程：{sub_flow}")
                    print("==========================================")
                    result = run_extract_sub_flow(sub_flow, base_path)
                else:
                    print(f"\n执行配置：")
                    print(f"模式：Extend(高级模式)")
                    print(f"流程：{sub_flow}")
                    print("==========================================")
                    result = run_extend_sub_flow(sub_flow, base_path)

        if result:
            # 记录结果
            logger.info(f"流程执行完成，结果：status={result['status']}, total={result['data']['total_count']}, success={result['data']['success_count']}, fail={result['data']['fail_count']}")
            if result["data"]["fail_count"] > 0:
                logger.warning(f"执行失败项：{result['data']['fail_reasons']}")
            
            # 输出结果到控制台
            print("\n执行结果：")
            print(f"状态：{result['status']}")
            print(f"总数量：{result['data']['total_count']}")
            print(f"成功数量：{result['data']['success_count']}")
            print(f"失败数量：{result['data']['fail_count']}")
            if result["data"]["fail_count"] > 0:
                print("失败原因：")
                for reason in result["data"]["fail_reasons"]:
                    print(f"  - {reason}")
            
            # 显示输出引导
            if result.get("output_path") and result.get("status") == "success":
                # 从result中提取mode和language
                mode = result.get("mode", "Extract")
                language = result.get("language", "English")
                show_output_guide(result["output_path"], mode, language)
    
    except KeyboardInterrupt:
        logger.info("工具被用户中断")
        print("\n[WARN] 工具被用户中断")
    except SystemExit:
        logger.info("工具正常退出")
        print("\n[END] 工具正常退出")
    except Exception as e:
        logger.error(f"工具执行过程中发生错误：{str(e)}", exc_info=True)
        print(f"\n[ERROR] 工具执行过程中发生错误：{str(e)}")
        print("详细错误信息已记录到日志文件中")
    finally:
        logger.info("==========================================")
        logger.info("             工具执行结束")
        logger.info("==========================================")


if __name__ == "__main__":
    main()
