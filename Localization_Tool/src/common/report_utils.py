#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告工具模块

该模块包含报告生成和保存功能。
"""

import json
import os
from typing import Any, Dict, Optional

from .timestamp_utils import get_formatted_timestamp


def generate_report(
    process_id: str,
    mode: str,
    sub_flow: str,
    status: str,
    data: Dict[str, Any],
    decompile: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    生成报告

    Args:
        process_id: 处理ID
        mode: 模式(Extract或Extend)
        sub_flow: 子流程
        status: 状态(success或fail)
        data: 数据
        decompile: 反编译信息(可选)

    Returns:
        Dict[str, Any]: 报告数据
    """
    # 获取当前时间
    start_time = get_formatted_timestamp()
    end_time = get_formatted_timestamp()

    # 构建报告结构
    report = {
        "process_id": process_id,
        "mode": mode,
        "sub_flow": sub_flow,
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "data": data,
    }

    # 如果有反编译信息，添加到报告中
    if decompile:
        report["decompile"] = decompile

    return report


def save_report(report: Dict[str, Any], report_path: str, timestamp: str, rule_type: str = None, mod_name: str = None, language: str = None) -> bool:
    """
    保存报告到文件

    Args:
        report: 报告数据
        report_path: 报告保存路径
        timestamp: 时间戳
        rule_type: 规则类型(regular: 常规提取规则, mapping: 映射规则)
        mod_name: 模组名称
        language: 语言类型(English或Chinese)

    Returns:
        bool: 是否成功保存
    """
    try:
        # 根据规则类型确定基础报告保存路径
        base_report_path = report_path
        
        # 判断是单个文件还是多个文件处理
        is_single_file = False
        data = report.get("data", {})
        total_count = data.get("total_count", 1)
        
        # 检查total_count，判断是否为单个文件处理
        if total_count == 1:
            is_single_file = True
        
        # 检查是否为单个JAR文件反编译报告
        if report.get("sub_flow") == "反编译单个JAR文件":
            is_single_file = True
        
        # 确定最终报告保存路径
        if is_single_file:
            # 单个文件处理，直接保存到输出文件夹根目录
            final_report_path = base_report_path
        else:
            # 多个文件处理，统一保存到Report文件夹内
            final_report_path = os.path.join(base_report_path, "Report")
        
        # 确保报告目录存在
        os.makedirs(final_report_path, exist_ok=True)

        # 构建报告文件名
        report_file = os.path.join(
            final_report_path, f"{report['mode'].lower()}_{timestamp}_report.json"
        )

        # 保存报告
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"[OK] 报告保存成功: {report_file}")
        return True
    except Exception as e:
        print(f"[ERROR] 报告保存失败: {e}")
        return False


def update_report_status(
    report: Dict[str, Any], status: str, data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    更新报告状态

    Args:
        report: 报告数据
        status: 新状态
        data: 新数据(可选)

    Returns:
        Dict[str, Any]: 更新后的报告数据
    """
    # 更新状态
    report["status"] = status

    # 更新结束时间
    report["end_time"] = get_formatted_timestamp()

    # 如果有新数据，更新数据
    if data:
        report["data"].update(data)

    return report


def get_report_summary(report: Dict[str, Any]) -> str:
    """
    获取报告摘要

    Args:
        report: 报告数据

    Returns:
        str: 报告摘要
    """
    summary = f"""
📋 报告摘要
==========
模式: {report['mode']}
子流程: {report['sub_flow']}
状态: {report['status']}
开始时间: {report['start_time']}
结束时间: {report['end_time']}
处理ID: {report['process_id']}

数据统计:
- 总数量: {report['data'].get('total_count', 0)}
- 成功数量: {report['data'].get('success_count', 0)}
- 失败数量: {report['data'].get('fail_count', 0)}
"""

    # 如果有反编译信息，添加到摘要中
    if "decompile" in report:
        summary += "\n反编译信息:\n"
        summary += f"- JAR路径: {report['decompile'].get('jar_path', 'N/A')}\n"
        summary += f"- 状态: {report['decompile'].get('status', 'N/A')}"

    return summary


def merge_reports(reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    合并多个报告为一个报告

    Args:
        reports: 报告列表

    Returns:
        Dict[str, Any]: 合并后的报告
    """
    if not reports:
        return {}

    # 合并报告数据
    merged_data = {
        "total_count": 0,
        "success_count": 0,
        "fail_count": 0,
        "fail_reasons": []
    }

    # 收集所有失败原因
    fail_reasons = []

    # 统计数据
    for report in reports:
        data = report.get("data", {})
        merged_data["total_count"] += data.get("total_count", 0)
        merged_data["success_count"] += data.get("success_count", 0)
        merged_data["fail_count"] += data.get("fail_count", 0)
        fail_reasons.extend(data.get("fail_reasons", []))

    # 去重失败原因
    merged_data["fail_reasons"] = list(set(fail_reasons))

    # 确定整体状态
    overall_status = "success" if merged_data["fail_count"] == 0 else "fail"

    # 构建合并后的报告
    merged_report = {
        "process_id": reports[0]["process_id"],
        "mode": reports[0]["mode"],
        "sub_flow": "合并报告",
        "start_time": min(report["start_time"] for report in reports),
        "end_time": max(report["end_time"] for report in reports),
        "status": overall_status,
        "data": merged_data,
        "sub_reports": reports
    }

    return merged_report


def find_reports(directory: str, mode: Optional[str] = None, status: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    查找符合条件的报告

    Args:
        directory: 报告目录
        mode: 模式(可选)
        status: 状态(可选)
        start_time: 开始时间(可选)
        end_time: 结束时间(可选)

    Returns:
        List[Dict[str, Any]]: 符合条件的报告列表
    """
    reports = []

    # 遍历目录下所有报告文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith("_report.json"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        report = json.load(f)
                    
                    # 检查报告是否符合条件
                    match = True
                    
                    # 检查模式
                    if mode and report.get("mode", "") != mode:
                        match = False
                    
                    # 检查状态
                    if status and report.get("status", "") != status:
                        match = False
                    
                    # 检查开始时间
                    if start_time and report.get("start_time", "") < start_time:
                        match = False
                    
                    # 检查结束时间
                    if end_time and report.get("end_time", "") > end_time:
                        match = False
                    
                    if match:
                        reports.append(report)
                except Exception as e:
                    print(f"[ERROR] 读取报告文件失败: {file_path} - {e}")
    
    return reports


def generate_report_statistics(reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    生成报告统计信息

    Args:
        reports: 报告列表

    Returns:
        Dict[str, Any]: 统计信息
    """
    if not reports:
        return {}

    # 初始化统计数据
    stats = {
        "total_reports": len(reports),
        "success_reports": 0,
        "fail_reports": 0,
        "total_processed": 0,
        "total_success": 0,
        "total_fail": 0,
        "mode_distribution": {},
        "status_distribution": {}
    }

    # 统计数据
    for report in reports:
        # 统计报告状态
        status = report.get("status", "")
        if status == "success":
            stats["success_reports"] += 1
        else:
            stats["fail_reports"] += 1
        
        # 统计模式分布
        mode = report.get("mode", "")
        stats["mode_distribution"][mode] = stats["mode_distribution"].get(mode, 0) + 1
        
        # 统计状态分布
        stats["status_distribution"][status] = stats["status_distribution"].get(status, 0) + 1
        
        # 统计处理数量
        data = report.get("data", {})
        stats["total_processed"] += data.get("total_count", 0)
        stats["total_success"] += data.get("success_count", 0)
        stats["total_fail"] += data.get("fail_count", 0)

    return stats


def export_report(report: Dict[str, Any], export_path: str, format: str = "json") -> bool:
    """
    导出报告为不同格式

    Args:
        report: 报告数据
        export_path: 导出路径
        format: 导出格式(json, txt, yaml)

    Returns:
        bool: 是否成功导出
    """
    try:
        # 确保导出目录存在
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        
        if format == "json":
            # 导出为JSON格式
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        elif format == "txt":
            # 导出为文本格式
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(get_report_summary(report))
        elif format == "yaml":
            # 导出为YAML格式
            import yaml
            with open(export_path, "w", encoding="utf-8") as f:
                yaml.dump(report, f, allow_unicode=True, default_flow_style=False)
        else:
            print(f"[ERROR] 不支持的导出格式: {format}")
            return False
        
        print(f"[OK] 报告已导出到: {export_path}")
        return True
    except Exception as e:
        print(f"[ERROR] 导出报告失败: {e}")
        return False


def cleanup_old_reports(directory: str, days: int = 7) -> bool:
    """
    清理指定天数前的旧报告

    Args:
        directory: 报告目录
        days: 保留天数

    Returns:
        bool: 是否成功清理
    """
    try:
        import time
        
        # 计算过期时间
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        # 遍历目录下所有报告文件
        deleted_count = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith("_report.json"):
                    file_path = os.path.join(root, file)
                    # 获取文件修改时间
                    mtime = os.path.getmtime(file_path)
                    # 如果文件过期，删除
                    if mtime < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
        
        print(f"[OK] 已清理 {deleted_count} 个旧报告文件")
        return True
    except Exception as e:
        print(f"[ERROR] 清理旧报告失败: {e}")
        return False
