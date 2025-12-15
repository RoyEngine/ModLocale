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


def save_report(report: Dict[str, Any], report_path: str, timestamp: str) -> bool:
    """
    保存报告到文件

    Args:
        report: 报告数据
        report_path: 报告保存路径
        timestamp: 时间戳

    Returns:
        bool: 是否成功保存
    """
    try:
        # 确保报告目录存在
        os.makedirs(report_path, exist_ok=True)

        # 构建报告文件名
        report_file = os.path.join(
            report_path, f"{report['mode'].lower()}_{timestamp}_report.json"
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
