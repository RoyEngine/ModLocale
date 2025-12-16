#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAR文件处理工具

该模块包含JAR文件的反编译、内容分析和版本检测功能。
"""

import os
import subprocess
import tempfile
import zipfile
import requests
import shutil
import concurrent.futures
from typing import List, Dict, Any, Optional


def is_jar_file(file_path: str) -> bool:
    """
    检查文件是否为JAR文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否为JAR文件
    """
    return file_path.lower().endswith(".jar")

# 工具路径
tools_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools")
cfr_path = os.path.join(tools_dir, "cfr-0.152", "cfr-0.152.jar")
procyon_path = os.path.join(tools_dir, "procyon-decompiler-0.6.0", "procyon-decompiler-0.6.0.jar")

# 反编译工具下载配置
decompiler_config = {
    "cfr": {
        "version": "0.152",
        "url": "https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar",
        "dir": os.path.join(tools_dir, "cfr-0.152"),
        "path": cfr_path
    },
    "procyon": {
        "version": "0.6.0",
        "url": "https://github.com/mstrobel/procyon/releases/download/v0.6.0/procyon-decompiler-0.6.0.jar",
        "dir": os.path.join(tools_dir, "procyon-decompiler-0.6.0"),
        "path": procyon_path
    }
}


def check_java_environment() -> bool:
    """
    检查Java环境是否可用
    
    Returns:
        bool: Java环境是否可用
    """
    try:
        # 检查Java是否安装
        result = subprocess.run(
            ["java", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return True
        else:
            print("[ERROR] Java环境检测失败，返回码非零")
            print(f"  错误信息: {result.stderr}")
            return False
    except FileNotFoundError:
        print("[ERROR] 未找到Java可执行文件，请确保Java已安装并添加到环境变量")
        return False
    except Exception as e:
        print(f"[ERROR] 检测Java环境时发生异常: {str(e)}")
        return False


def check_jar_file_integrity(jar_path: str) -> bool:
    """
    检查JAR文件完整性
    
    Args:
        jar_path: JAR文件路径
    
    Returns:
        bool: JAR文件是否完整
    """
    if not os.path.exists(jar_path):
        print(f"[ERROR] JAR文件不存在: {jar_path}")
        return False
    
    if not os.path.isfile(jar_path):
        print(f"[ERROR] {jar_path} 不是一个文件")
        return False
    
    # 检查文件大小
    if os.path.getsize(jar_path) == 0:
        print(f"[ERROR] JAR文件为空: {jar_path}")
        return False
    
    # 检查文件是否为有效的ZIP文件
    try:
        with zipfile.ZipFile(jar_path, "r") as zip_ref:
            # 尝试获取文件列表，验证ZIP格式
            zip_ref.namelist()
            return True
    except zipfile.BadZipFile:
        print(f"[ERROR] JAR文件格式无效或已损坏: {jar_path}")
        return False
    except Exception as e:
        print(f"[ERROR] 检查JAR文件完整性时发生异常: {jar_path}")
        print(f"  异常信息: {str(e)}")
        return False


def download_decompiler(decompiler_name: str) -> bool:
    """
    下载指定的反编译工具
    
    Args:
        decompiler_name: 反编译工具名称(cfr或procyon)
    
    Returns:
        bool: 下载是否成功
    """
    if decompiler_name not in decompiler_config:
        print(f"[ERROR] 不支持的反编译工具: {decompiler_name}")
        return False
    
    config = decompiler_config[decompiler_name]
    url = config["url"]
    target_dir = config["dir"]
    target_path = config["path"]
    
    print(f"[INFO] 开始下载反编译工具: {decompiler_name} {config['version']}")
    print(f"[INFO] 下载地址: {url}")
    print(f"[INFO] 保存路径: {target_path}")
    
    try:
        # 创建目标目录
        os.makedirs(target_dir, exist_ok=True)
        print(f"[DIR] 创建目录: {target_dir}")
        
        # 下载文件
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # 保存文件
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"[OK] 成功下载反编译工具: {decompiler_name}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 下载反编译工具失败: {e}")
        # 清理可能的部分下载文件
        if os.path.exists(target_path):
            os.remove(target_path)
        return False
    except Exception as e:
        print(f"[ERROR] 下载反编译工具时发生异常: {e}")
        # 清理可能的部分下载文件
        if os.path.exists(target_path):
            os.remove(target_path)
        return False


def check_decompiler_tools(download_missing: bool = True) -> bool:
    """
    检查反编译工具是否可用，可选自动下载缺失的工具
    
    Args:
        download_missing: 是否自动下载缺失的工具
    
    Returns:
        bool: 反编译工具是否可用
    """
    # 检查tools目录是否存在
    if not os.path.exists(tools_dir):
        print(f"[INFO] tools目录不存在，创建目录: {tools_dir}")
        os.makedirs(tools_dir, exist_ok=True)
    
    # 检查至少有一个反编译工具可用
    cfr_available = os.path.exists(cfr_path)
    procyon_available = os.path.exists(procyon_path)
    
    if cfr_available or procyon_available:
        print(f"[OK] 找到可用的反编译工具")
        if cfr_available:
            print(f"  - CFR: {cfr_path}")
        if procyon_available:
            print(f"  - Procyon: {procyon_path}")
        return True
    
    # 没有可用的反编译工具，尝试自动下载
    if download_missing:
        print("[INFO] 没有可用的反编译工具，尝试自动下载")
        
        # 尝试下载CFR
        if download_decompiler("cfr"):
            return True
        
        # CFR下载失败，尝试下载Procyon
        if download_decompiler("procyon"):
            return True
        
        # 两个工具都下载失败
        print("[ERROR] 自动下载反编译工具失败")
        print(f"[NOTE] 请手动下载以下至少一个文件:")
        print(f"  - CFR: {decompiler_config['cfr']['url']}")
        print(f"  - Procyon: {decompiler_config['procyon']['url']}")
        print(f"[NOTE] 并将其放入对应目录:")
        print(f"  - CFR: {cfr_path}")
        print(f"  - Procyon: {procyon_path}")
        return False
    
    # 不自动下载，直接返回失败
    print("[ERROR] 没有可用的反编译工具")
    print(f"[NOTE] 请确保以下至少一个文件存在:")
    print(f"  - {cfr_path}")
    print(f"  - {procyon_path}")
    return False


def convert_unicode_escapes(file_path: str) -> bool:
    """
    将文件中的Unicode转义序列转换为实际字符
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool: 是否转换成功
    """
    import re
    
    try:
        # 使用latin-1编码读取文件，避免自动转换Unicode转义序列
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
        
        # 检查是否存在Unicode转义序列
        if not re.search(r'\\u[0-9a-fA-F]{4}', content):
            # 没有需要转换的Unicode转义序列
            return False
        
        # 使用正则表达式查找所有\uXXXX格式的Unicode转义序列
        def replace_unicode_escape(match):
            """替换单个Unicode转义序列"""
            try:
                # 获取\uXXXX部分，转换为实际字符
                return bytes(match.group(0), 'latin-1').decode('unicode_escape')
            except Exception:
                # 如果转换失败，返回原字符串
                return match.group(0)
        
        # 转换所有Unicode转义序列
        converted_content = re.sub(r'\\u[0-9a-fA-F]{4}', replace_unicode_escape, content)
        
        # 写入转换后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(converted_content)
        return True
    except Exception as e:
        print(f"[ERROR] 转换Unicode转义序列时发生异常: {file_path}")
        print(f"  异常类型: {type(e).__name__}")
        print(f"  异常信息: {str(e)}")
        return False


def convert_unicode_escapes_in_dir(directory: str) -> int:
    """
    转换目录中所有Java和Kotlin文件的Unicode转义序列
    
    Args:
        directory: 目录路径
    
    Returns:
        int: 转换成功的文件数量
    """
    converted_count = 0
    
    # 遍历目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 只处理Java和Kotlin文件
            if file.endswith(('.java', '.kt', '.kts')):
                file_path = os.path.join(root, file)
                if convert_unicode_escapes(file_path):
                    converted_count += 1
    
    return converted_count


def decompile_jar(jar_path: str, output_dir: str, decompiler: str = "cfr") -> bool:
    """
    反编译JAR文件
    
    Args:
        jar_path: JAR文件路径
        output_dir: 输出目录
        decompiler: 反编译工具，可选值：cfr或procyon
    
    Returns:
        bool: 是否反编译成功
    """
    # 1. 检查Java环境
    if not check_java_environment():
        return False
    
    # 2. 检查反编译工具，自动下载缺失的工具
    if not check_decompiler_tools(download_missing=True):
        return False
    
    # 3. 检查指定的反编译工具是否可用
    if decompiler == "cfr" and not os.path.exists(cfr_path):
        print(f"[ERROR] CFR反编译工具不可用: {cfr_path}")
        print(f"[INFO] 尝试自动下载CFR...")
        if not download_decompiler("cfr"):
            return False
    elif decompiler == "procyon" and not os.path.exists(procyon_path):
        print(f"[ERROR] Procyon反编译工具不可用: {procyon_path}")
        print(f"[INFO] 尝试自动下载Procyon...")
        if not download_decompiler("procyon"):
            return False
    
    # 3. 检查JAR文件完整性
    if not check_jar_file_integrity(jar_path):
        return False
    
    # 4. 确保输出目录存在
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print(f"[ERROR] 创建输出目录失败: {output_dir}")
        print(f"  异常信息: {str(e)}")
        return False
    
    # 5. 选择反编译工具
    decompile_result = False
    if decompiler == "cfr":
        decompile_result = _decompile_with_cfr(jar_path, output_dir)
    elif decompiler == "procyon":
        decompile_result = _decompile_with_procyon(jar_path, output_dir)
    else:
        print(f"[ERROR] 不支持的反编译工具: {decompiler}")
        print(f"[NOTE] 支持的反编译工具: cfr, procyon")
        return False
    
    # 6. 转换Unicode转义序列为实际字符
    if decompile_result:
        print(f"[NOTE] 开始转换反编译文件中的Unicode转义序列...")
        converted_count = convert_unicode_escapes_in_dir(output_dir)
        if converted_count > 0:
            print(f"OK 成功转换 {converted_count} 个文件中的Unicode转义序列")
        else:
            print(f"[NOTE] 没有需要转换的Unicode转义序列")
    
    return decompile_result


def _decompile_with_cfr(jar_path: str, output_dir: str) -> bool:
    """
    使用CFR反编译JAR文件
    
    Args:
        jar_path: JAR文件路径
        output_dir: 输出目录
    
    Returns:
        bool: 是否反编译成功
    """
    # 检查CFR工具是否存在
    if not os.path.exists(cfr_path):
        print(f"[ERROR] CFR工具不存在: {cfr_path}")
        return False
    
    # 验证JAR文件
    if not os.path.exists(jar_path):
        print(f"[ERROR] JAR文件不存在: {jar_path}")
        return False
    
    if not os.path.isfile(jar_path):
        print(f"[ERROR] {jar_path} 不是一个文件")
        return False
    
    # 构建简化的命令，只保留必要的参数
    cmd = [
        "java",
        "-jar",
        cfr_path,
        jar_path,
        "--outputdir",
        output_dir
    ]
    
    print(f"[NOTE] 开始使用CFR反编译JAR文件: {os.path.basename(jar_path)}")
    print(f"[DIR] 输出目录: {output_dir}")
    print(f"[CMD] 执行命令: {' '.join(cmd)}")
    
    try:
        # 执行命令
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(jar_path),
            timeout=300  # 设置5分钟超时
        )
        
        if result.returncode == 0:
            print(f"OK 使用CFR反编译成功: {os.path.basename(jar_path)}")
            # 验证输出目录是否有内容
            if os.path.exists(output_dir):
                if os.listdir(output_dir):
                    print(f"[INFO] 输出目录包含 {len(os.listdir(output_dir))} 个文件")
                    return True
                else:
                    print(f"[WARNING] 反编译成功但输出目录为空: {output_dir}")
                    return True
            else:
                print(f"[ERROR] 输出目录不存在: {output_dir}")
                return False
        else:
            print(f"[ERROR] 使用CFR反编译失败: {os.path.basename(jar_path)}")
            print(f"  退出码: {result.returncode}")
            if result.stdout:
                print(f"  标准输出: {result.stdout[:500]}{'...' if len(result.stdout) > 500 else ''}")
            if result.stderr:
                print(f"  错误输出: {result.stderr[:500]}{'...' if len(result.stderr) > 500 else ''}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] 使用CFR反编译超时: {os.path.basename(jar_path)}")
        print(f"  超时时间: 5分钟")
        return False
    except FileNotFoundError:
        print(f"[ERROR] 未找到Java可执行文件，请确保Java已安装并添加到环境变量")
        return False
    except Exception as e:
        print(f"[ERROR] 使用CFR反编译时发生异常: {os.path.basename(jar_path)}")
        print(f"  异常类型: {type(e).__name__}")
        print(f"  异常信息: {str(e)}")
        import traceback
        print(f"  堆栈跟踪: {traceback.format_exc()[:1000]}{'...' if len(traceback.format_exc()) > 1000 else ''}")
        return False


def _decompile_with_procyon(jar_path: str, output_dir: str) -> bool:
    """
    使用Procyon反编译JAR文件
    
    Args:
        jar_path: JAR文件路径
        output_dir: 输出目录
    
    Returns:
        bool: 是否反编译成功
    """
    # 检查Procyon工具是否存在
    if not os.path.exists(procyon_path):
        print(f"[ERROR] Procyon工具不存在: {procyon_path}")
        return False
    
    # 验证JAR文件
    if not os.path.exists(jar_path):
        print(f"[ERROR] JAR文件不存在: {jar_path}")
        return False
    
    if not os.path.isfile(jar_path):
        print(f"[ERROR] {jar_path} 不是一个文件")
        return False
    
    # 构建命令
    cmd = [
        "java",
        "-jar",
        procyon_path,
        "-o",
        output_dir,
        jar_path
    ]
    
    print(f"[NOTE] 开始使用Procyon反编译JAR文件: {os.path.basename(jar_path)}")
    print(f"[DIR] 输出目录: {output_dir}")
    print(f"[CMD] 执行命令: {' '.join(cmd)}")
    
    try:
        # 执行命令
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(jar_path),
            timeout=300  # 设置5分钟超时
        )
        
        if result.returncode == 0:
            print(f"OK 使用Procyon反编译成功: {os.path.basename(jar_path)}")
            # 验证输出目录是否有内容
            if os.path.exists(output_dir):
                if os.listdir(output_dir):
                    print(f"[INFO] 输出目录包含 {len(os.listdir(output_dir))} 个文件")
                    return True
                else:
                    print(f"[WARNING] 反编译成功但输出目录为空: {output_dir}")
                    return True
            else:
                print(f"[ERROR] 输出目录不存在: {output_dir}")
                return False
        else:
            print(f"[ERROR] 使用Procyon反编译失败: {os.path.basename(jar_path)}")
            print(f"  退出码: {result.returncode}")
            print(f"  标准输出: {result.stdout[:500]}{'...' if len(result.stdout) > 500 else ''}")
            print(f"  错误输出: {result.stderr[:500]}{'...' if len(result.stderr) > 500 else ''}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] 使用Procyon反编译超时: {os.path.basename(jar_path)}")
        print(f"  超时时间: 5分钟")
        return False
    except FileNotFoundError:
        print(f"[ERROR] 未找到Java可执行文件，请确保Java已安装并添加到环境变量")
        return False
    except Exception as e:
        print(f"[ERROR] 使用Procyon反编译时发生异常: {os.path.basename(jar_path)}")
        print(f"  异常类型: {type(e).__name__}")
        print(f"  异常信息: {str(e)}")
        import traceback
        print(f"  堆栈跟踪: {traceback.format_exc()[:1000]}{'...' if len(traceback.format_exc()) > 1000 else ''}")
        return False


def analyze_jar_content(jar_path: str) -> Dict[str, Any]:
    """
    分析JAR文件内容
    
    Args:
        jar_path: JAR文件路径
    
    Returns:
        Dict[str, Any]: JAR文件内容分析结果
    """
    result = {
        "file_count": 0,
        "class_count": 0,
        "resource_count": 0,
        "meta_inf_files": [],
        "manifest_content": None,
        "class_files": [],
        "resource_files": [],
        "jar_size": 0
    }
    
    # 检查JAR文件是否存在
    if not os.path.exists(jar_path):
        print(f"[ERROR] JAR文件不存在: {jar_path}")
        return result
    
    # 获取JAR文件大小
    result["jar_size"] = os.path.getsize(jar_path)
    
    try:
        with zipfile.ZipFile(jar_path, "r") as zip_ref:
            # 获取所有文件列表
            all_files = zip_ref.namelist()
            result["file_count"] = len(all_files)
            
            # 分析文件类型
            for file_name in all_files:
                if file_name.endswith(".class"):
                    result["class_count"] += 1
                    result["class_files"].append(file_name)
                elif file_name.startswith("META-INF/"):
                    result["meta_inf_files"].append(file_name)
                else:
                    result["resource_count"] += 1
                    result["resource_files"].append(file_name)
            
            # 读取Manifest文件
            if "META-INF/MANIFEST.MF" in all_files:
                with zip_ref.open("META-INF/MANIFEST.MF") as manifest_file:
                    result["manifest_content"] = manifest_file.read().decode("utf-8")
        
        print(f"OK 成功分析JAR文件内容: {jar_path}")
        print(f"   文件总数: {result['file_count']}")
        print(f"   类文件数: {result['class_count']}")
        print(f"   资源文件数: {result['resource_count']}")
        print(f"   JAR大小: {result['jar_size']} 字节")
    except Exception as e:
        print(f"[ERROR] 分析JAR文件内容时发生异常: {jar_path}")
        print(f"  异常信息: {str(e)}")
    
    return result


def detect_jar_version(jar_path: str) -> Optional[str]:
    """
    检测JAR文件版本
    
    Args:
        jar_path: JAR文件路径
    
    Returns:
        Optional[str]: JAR文件版本，如果无法检测则返回None
    """
    # 分析JAR文件内容
    analysis_result = analyze_jar_content(jar_path)
    
    # 从Manifest文件中提取版本信息
    if analysis_result["manifest_content"]:
        manifest_lines = analysis_result["manifest_content"].split("\n")
        for line in manifest_lines:
            if line.strip().startswith("Implementation-Version:"):
                return line.split(":")[1].strip()
            elif line.strip().startswith("Specification-Version:"):
                return line.split(":")[1].strip()
            elif line.strip().startswith("Bundle-Version:"):
                return line.split(":")[1].strip()
    
    # 从文件名中提取版本信息
    jar_name = os.path.basename(jar_path)
    # 使用正则表达式提取版本号
    import re
    version_pattern = r"(\d+(?:\.\d+)*)(?:[-_](?:alpha|beta|rc|release|final|\d+))*"  # noqa: W605
    match = re.search(version_pattern, jar_name)
    if match:
        return match.group(1)
    
    return None


def decompile_jar_to_mod(jar_path: str, mod_dir: str, decompiler: str = "cfr") -> bool:
    """
    反编译JAR文件到mod目录
    
    Args:
        jar_path: JAR文件路径
        mod_dir: mod目录
        decompiler: 反编译工具，可选值：cfr或procyon
    
    Returns:
        bool: 是否反编译成功
    """
    # 创建jar文件夹
    jar_dir = os.path.join(mod_dir, "jar")
    os.makedirs(jar_dir, exist_ok=True)
    
    # 反编译JAR文件
    return decompile_jar(jar_path, jar_dir, decompiler)


def get_decompiler_path(
    base_path: str, decompiler_type: str = "procyon"
) -> Optional[str]:
    """
    获取反编译器路径
    
    Args:
        base_path: 基础路径
        decompiler_type: 反编译器类型(procyon或cfr)
    
    Returns:
        Optional[str]: 反编译器路径，如果不存在则返回None
    """
    try:
        # 构建反编译器路径
        if decompiler_type == "procyon":
            decompiler_path = os.path.join(
                base_path,
                "tools",
                "procyon-decompiler-0.6.0",
                "procyon-decompiler-0.6.0.jar",
            )
        elif decompiler_type == "cfr":
            decompiler_path = os.path.join(
                base_path,
                "tools",
                "cfr-0.152",
                "cfr-0.152.jar",
            )
        else:
            print(f"[ERROR] 不支持的反编译器类型: {decompiler_type}")
            return None

        # 检查反编译器是否存在
        if os.path.exists(decompiler_path):
            return decompiler_path
        else:
            print(f"[ERROR] 反编译器不存在: {decompiler_path}")
            return None
    except Exception as e:
        print(f"[ERROR] 获取反编译器路径时发生异常: {e}")
        return None


def find_jar_files(directory: str) -> List[str]:
    """
    在目录下查找所有JAR文件
    
    Args:
        directory: 目录路径
    
    Returns:
        List[str]: JAR文件路径列表
    """
    jar_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".jar"):
                jar_files.append(os.path.join(root, file))
    return jar_files


def _decompile_jar_task(jar_file: str, output_dir: str, decompiler: str, jar_name: str) -> Dict[str, Any]:
    """
    单个JAR文件反编译任务，用于并行处理
    
    Args:
        jar_file: JAR文件路径
        output_dir: 输出目录
        decompiler: 反编译工具
        jar_name: JAR文件名
    
    Returns:
        Dict[str, Any]: 反编译结果
    """
    # 构建输出目录
    jar_output_dir = os.path.join(output_dir, jar_name)
    
    # 反编译JAR文件
    success = decompile_jar(jar_file, jar_output_dir, decompiler)
    
    # 记录结果
    return {
        "jar_file": jar_file,
        "output_dir": jar_output_dir,
        "success": success,
        "decompiler": decompiler
    }


def decompile_all_jars_in_dir(input_dir: str, output_dir: str, decompiler: str = "cfr", max_workers: int = None) -> List[Dict[str, Any]]:
    """
    反编译目录中的所有JAR文件，支持并行处理
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        decompiler: 反编译工具，可选值：cfr或procyon
        max_workers: 最大工作线程数，默认为CPU核心数
    
    Returns:
        List[Dict[str, Any]]: 反编译结果列表
    """
    # 查找所有JAR文件
    jar_files = find_jar_files(input_dir)
    
    print(f"[NOTE] 找到 {len(jar_files)} 个JAR文件")
    
    if not jar_files:
        return []
    
    # 检查Java环境和反编译工具
    if not check_java_environment():
        return []
    
    if not check_decompiler_tools(download_missing=True):
        return []
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    # 使用并行处理反编译所有JAR文件
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交任务
        future_to_jar = {
            executor.submit(
                _decompile_jar_task,
                jar_file,
                output_dir,
                decompiler,
                os.path.basename(jar_file).replace(".jar", "")
            ): jar_file for jar_file in jar_files
        }
        
        # 处理结果
        for future in concurrent.futures.as_completed(future_to_jar):
            jar_file = future_to_jar[future]
            try:
                result = future.result()
                results.append(result)
                if result["success"]:
                    print(f"OK 反编译成功: {os.path.basename(jar_file)}")
                else:
                    print(f"[ERROR] 反编译失败: {os.path.basename(jar_file)}")
            except Exception as e:
                print(f"[ERROR] 反编译 {os.path.basename(jar_file)} 时发生异常: {e}")
                results.append({
                    "jar_file": jar_file,
                    "output_dir": os.path.join(output_dir, os.path.basename(jar_file).replace(".jar", "")),
                    "success": False,
                    "decompiler": decompiler
                })
    
    return results


def extract_jar(jar_path: str, output_dir: str) -> bool:
    """
    提取JAR文件内容，不进行反编译
    
    Args:
        jar_path: JAR文件路径
        output_dir: 输出目录
    
    Returns:
        bool: 是否提取成功
    """
    # 检查JAR文件是否存在
    if not os.path.exists(jar_path):
        print(f"[ERROR] JAR文件不存在: {jar_path}")
        return False
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"[NOTE] 开始提取JAR文件内容: {jar_path}")
    print(f"[DIR] 输出目录: {output_dir}")
    
    try:
        with zipfile.ZipFile(jar_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)
        
        print(f"OK 成功提取JAR文件内容: {jar_path}")
        return True
    except Exception as e:
        print(f"[ERROR] 提取JAR文件内容时发生异常: {jar_path}")
        print(f"  异常信息: {str(e)}")
        return False


def get_jar_main_class(jar_path: str) -> Optional[str]:
    """
    获取JAR文件的主类
    
    Args:
        jar_path: JAR文件路径
    
    Returns:
        Optional[str]: JAR文件的主类，如果无法获取则返回None
    """
    # 分析JAR文件内容
    analysis_result = analyze_jar_content(jar_path)
    
    # 从Manifest文件中提取主类
    if analysis_result["manifest_content"]:
        manifest_lines = analysis_result["manifest_content"].split("\n")
        for line in manifest_lines:
            if line.strip().startswith("Main-Class:"):
                return line.split(":")[1].strip()
    
    return None
