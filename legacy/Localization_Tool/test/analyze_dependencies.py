#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖分析工具

该脚本用于分析Python项目的依赖使用情况，识别未被实际使用的依赖包，并计算它们的存储空间大小。
"""

import os
import sys
import re
import json
from typing import Dict, List, Set, Optional
from pathlib import Path

# 使用现代的importlib.metadata代替已弃用的pkg_resources
try:
    from importlib.metadata import distributions, Distribution
    from importlib.metadata import PackageNotFoundError
    MODERN_METADATA = True
except ImportError:
    # 回退到pkg_resources（仅用于兼容性）
    from pkg_resources import working_set, DistributionNotFound
    MODERN_METADATA = False


def get_installed_packages() -> List[Distribution]:
    """
    获取所有已安装的Python包
    
    Returns:
        List[Distribution]: 已安装包的列表
    """
    if MODERN_METADATA:
        return list(distributions())
    else:
        return list(working_set)


def get_package_name(dist: Distribution) -> str:
    """
    获取包的名称
    
    Args:
        dist: 包的Distribution对象
    
    Returns:
        str: 包名
    """
    if MODERN_METADATA:
        return dist.name
    else:
        return dist.key


def get_package_version(dist: Distribution) -> str:
    """
    获取包的版本
    
    Args:
        dist: 包的Distribution对象
    
    Returns:
        str: 包的版本
    """
    if MODERN_METADATA:
        return dist.version
    else:
        return dist.version


def get_package_dependencies(dist: Distribution) -> Set[str]:
    """
    获取指定包的所有依赖
    
    Args:
        dist: 包的Distribution对象
    
    Returns:
        Set[str]: 依赖包名集合
    """
    dependencies = set()
    
    try:
        if MODERN_METADATA:
            # 使用importlib.metadata获取依赖
            requirements = dist.requires or []
            for req in requirements:
                # 提取包名（忽略版本约束）
                pkg_name = req.split(';')[0].split('[')[0].strip()
                dependencies.add(pkg_name)
        else:
            # 使用pkg_resources获取依赖
            for req in dist.requires():
                dependencies.add(req.key)
                # 递归获取依赖的依赖（暂时注释，避免递归过深）
                # try:
                #     dep_dist = working_set.find(req)
                #     if dep_dist:
                #         dependencies.update(get_package_dependencies(dep_dist))
                # except DistributionNotFound:
                #     pass
    except Exception as e:
        print(f"[ERROR] 无法获取包 {get_package_name(dist)} 的依赖: {e}")
    
    return dependencies


def get_package_size(package_name: str) -> int:
    """
    计算指定包的存储空间大小（字节）
    
    Args:
        package_name: 包名
    
    Returns:
        int: 包的存储空间大小（字节）
    """
    try:
        # 获取包的安装位置
        if MODERN_METADATA:
            from importlib.metadata import files
            pkg_files = files(package_name)
            if not pkg_files:
                return 0
            
            # 计算所有文件的大小总和
            total_size = 0
            for file in pkg_files:
                file_path = file.locate()
                if file_path and file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size
        else:
            from pkg_resources import get_distribution
            package = get_distribution(package_name)
            package_path = package.location
            
            # 计算目录大小
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(package_path):
                # 跳过虚拟环境中的其他包目录
                if os.path.basename(dirpath) == 'site-packages' or 'venv' in dirpath.lower():
                    continue
                
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            return total_size
    except Exception as e:
        print(f"[ERROR] 无法计算包 {package_name} 的大小: {e}")
        return 0


def find_imports_in_codebase(codebase_path: str) -> Set[str]:
    """
    查找代码库中所有导入的包名
    
    Args:
        codebase_path: 代码库根目录
    
    Returns:
        Set[str]: 导入的包名集合
    """
    imports = set()
    
    # 正则表达式匹配import语句
    import_pattern = re.compile(r'^\s*(?:import|from)\s+([a-zA-Z0-9_]+)', re.MULTILINE)
    
    # 遍历代码库中的所有Python文件
    for root, dirs, files in os.walk(codebase_path):
        # 跳过某些目录
        if any(exclude in root for exclude in ['.venv', '__pycache__', '.git', 'build', 'dist', '.trae']):
            continue
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 查找所有import语句
                    matches = import_pattern.findall(content)
                    for match in matches:
                        # 添加导入的包名
                        imports.add(match)
                except Exception as e:
                    print(f"[ERROR] 无法读取文件 {file_path}: {e}")
    
    # 移除Python标准库包
    standard_lib_packages = {
        'os', 'sys', 'json', 're', 'datetime', 'time', 'logging', 'tempfile', 
        'shutil', 'subprocess', 'zipfile', 'concurrent', 'typing', 'dataclasses',
        'pathlib', 'gc', 'platform', 'traceback', 'inspect', 'collections',
        'enum', 'math', 'random', 'string', 'struct', 'threading', 'weakref'
    }
    
    # 只保留第三方包
    third_party_imports = imports - standard_lib_packages
    
    return third_party_imports


def get_declared_dependencies(codebase_path: str) -> Set[str]:
    """
    获取项目声明的依赖（从requirements.txt和dev-requirements.txt）
    
    Args:
        codebase_path: 代码库根目录
    
    Returns:
        Set[str]: 声明的依赖包名集合
    """
    declared_dependencies = set()
    
    # 读取requirements.txt文件
    req_files = [
        os.path.join(codebase_path, 'Localization_Tool', 'requirements.txt'),
        os.path.join(codebase_path, 'Localization_Tool', 'dev-requirements.txt'),
        os.path.join(codebase_path, 'Localization_Tool', 'requirements.in'),
        os.path.join(codebase_path, 'Localization_Tool', 'dev-requirements.in')
    ]
    
    for req_file in req_files:
        if os.path.exists(req_file):
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # 提取包名（忽略版本号和注释）
                            pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0]
                            pkg_name = pkg_name.split('[')[0].split(';')[0].strip()
                            declared_dependencies.add(pkg_name)
            except Exception as e:
                print(f"[ERROR] 无法读取依赖文件 {req_file}: {e}")
    
    return declared_dependencies


def analyze_dependencies(codebase_path: str, venv_path: Optional[str] = None) -> Dict[str, any]:
    """
    分析依赖使用情况
    
    Args:
        codebase_path: 代码库根目录
        venv_path: 虚拟环境目录（可选）
    
    Returns:
        Dict[str, any]: 依赖分析结果
    """
    # 获取所有已安装的包
    installed_packages = get_installed_packages()
    
    # 查找代码库中导入的包
    imported_packages = find_imports_in_codebase(codebase_path)
    
    # 获取项目声明的依赖
    declared_dependencies = get_declared_dependencies(codebase_path)
    
    # 识别未使用的依赖
    unused_dependencies = []
    total_unused_size = 0
    
    for dist in installed_packages:
        pkg_name = get_package_name(dist)
        pkg_version = get_package_version(dist)
        
        # 检查包是否被导入
        if pkg_name not in imported_packages:
            # 检查包是否是其他已使用包的依赖
            is_dependency = False
            for used_pkg in imported_packages:
                try:
                    if MODERN_METADATA:
                        from importlib.metadata import distribution
                        used_dist = distribution(used_pkg)
                        used_deps = get_package_dependencies(used_dist)
                        if pkg_name in used_deps:
                            is_dependency = True
                            break
                    else:
                        from pkg_resources import get_distribution
                        used_dist = get_distribution(used_pkg)
                        used_deps = get_package_dependencies(used_dist)
                        if pkg_name in used_deps:
                            is_dependency = True
                            break
                except Exception:
                    continue
            
            if not is_dependency:
                # 计算包大小
                pkg_size = get_package_size(pkg_name)
                total_unused_size += pkg_size
                
                unused_dependencies.append({
                    'name': pkg_name,
                    'version': pkg_version,
                    'size': pkg_size,
                    'size_human': f"{pkg_size / 1024:.2f} KB" if pkg_size < 1024*1024 else f"{pkg_size / (1024*1024):.2f} MB"
                })
    
    # 按大小排序
    unused_dependencies.sort(key=lambda x: x['size'], reverse=True)
    
    # 生成分析报告
    report = {
        'total_installed_packages': len(installed_packages),
        'total_imported_packages': len(imported_packages),
        'total_declared_dependencies': len(declared_dependencies),
        'total_unused_dependencies': len(unused_dependencies),
        'total_unused_size': total_unused_size,
        'total_unused_size_human': f"{total_unused_size / 1024:.2f} KB" if total_unused_size < 1024*1024 else f"{total_unused_size / (1024*1024):.2f} MB",
        'unused_dependencies': unused_dependencies,
        'imported_packages': sorted(list(imported_packages)),
        'declared_dependencies': sorted(list(declared_dependencies))
    }
    
    return report


def generate_markdown_report(report: Dict[str, any]) -> str:
    """
    生成Markdown格式的分析报告
    
    Args:
        report: 依赖分析结果
    
    Returns:
        str: Markdown格式的报告
    """
    md_report = "# 依赖分析报告\n\n"
    md_report += "## 1. 依赖概览\n\n"
    md_report += "| 类别 | 数量 |\n"
    md_report += "|------|------|\n"
    md_report += f"| 已安装的包总数 | {report['total_installed_packages']} |\n"
    md_report += f"| 代码中直接使用的外部依赖 | {report['total_imported_packages']} |\n"
    md_report += f"| 项目声明的依赖 | {report['total_declared_dependencies']} |\n"
    md_report += f"| 未使用的依赖 | {report['total_unused_dependencies']} |\n"
    md_report += f"| 未使用依赖的总大小 | {report['total_unused_size_human']} |\n\n"
    
    md_report += "## 2. 未使用的依赖列表\n\n"
    
    if report['unused_dependencies']:
        md_report += "| 包名 | 版本 | 大小 |\n"
        md_report += "|------|------|------|\n"
        for dep in report['unused_dependencies']:
            md_report += f"| {dep['name']} | {dep['version']} | {dep['size_human']} |\n"
    else:
        md_report += "暂无未使用的依赖\n\n"
    
    md_report += "## 3. 代码中使用的外部依赖\n\n"
    md_report += "| 包名 |\n"
    md_report += "|------|\n"
    for pkg in report['imported_packages']:
        md_report += f"| {pkg} |\n"
    
    md_report += "\n## 4. 项目声明的依赖\n\n"
    md_report += "| 包名 |\n"
    md_report += "|------|\n"
    for pkg in report['declared_dependencies']:
        md_report += f"| {pkg} |\n"
    
    md_report += "\n## 5. 建议操作\n\n"
    md_report += "1. **移除未使用的依赖**：运行 `pip uninstall <package_name>` 移除未使用的包\n"
    md_report += "2. **更新requirements文件**：确保requirements文件只包含必要的依赖\n"
    md_report += "3. **定期运行依赖分析**：建议每周或每月运行一次依赖分析\n"
    md_report += "4. **使用虚拟环境**：为每个项目使用独立的虚拟环境，避免依赖冲突\n"
    
    return md_report


def main() -> int:
    """
    主函数
    """
    # 设置路径
    codebase_path = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(codebase_path, '.venv')
    
    print("=" * 60)
    print("          依赖分析工具")
    print("=" * 60)
    print(f"代码库路径: {codebase_path}")
    print(f"虚拟环境路径: {venv_path}")
    print("=" * 60)
    
    # 分析依赖
    report = analyze_dependencies(codebase_path, venv_path)
    
    # 输出分析结果
    print(f"\n已安装的包总数: {report['total_installed_packages']}")
    print(f"代码中导入的外部依赖数: {report['total_imported_packages']}")
    print(f"项目声明的依赖数: {report['total_declared_dependencies']}")
    print(f"未使用的依赖数: {report['total_unused_dependencies']}")
    print(f"未使用依赖的总大小: {report['total_unused_size_human']}")
    
    print("\n" + "=" * 60)
    print("          未使用的依赖列表")
    print("=" * 60)
    print(f"{'包名':<30} {'版本':<15} {'大小':<10}")
    print("-" * 60)
    
    for dep in report['unused_dependencies']:
        print(f"{dep['name']:<30} {dep['version']:<15} {dep['size_human']:<10}")
    
    # 生成Markdown报告
    md_report = generate_markdown_report(report)
    
    # 保存报告到文件
    report_file = os.path.join(codebase_path, 'dependency_analysis_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(md_report)
    
    # 保存JSON格式报告
    json_report_file = os.path.join(codebase_path, 'dependency_analysis_report.json')
    with open(json_report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"Markdown报告已保存到: {report_file}")
    print(f"JSON报告已保存到: {json_report_file}")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
