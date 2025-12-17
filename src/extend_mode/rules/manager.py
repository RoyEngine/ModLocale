#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rules子模块 - 规则管理功能

负责映射规则的创建、编辑、删除、查询和导入/导出
"""

import os
import shutil
import yaml
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.common.yaml_utils import (
    load_yaml_mappings,
    save_yaml_mappings,
    RuleConflictDetector
)


class RuleManager:
    """
    规则管理器，负责映射规则的CRUD操作
    """
    
    def __init__(self, rule_file: str = None):
        """
        初始化规则管理器
        
        Args:
            rule_file: 规则文件路径
        """
        self.rule_file = rule_file
        self.rules = []
        self.conflict_detector = RuleConflictDetector()
        self.original_rules = []  # 用于恢复和比较
        
        if rule_file and os.path.exists(rule_file):
            self.load_rules()
            self.original_rules = self.rules.copy()
    
    def load_rules(self, rule_file: str = None) -> bool:
        """
        加载规则文件
        
        Args:
            rule_file: 规则文件路径，默认使用初始化时的路径
        
        Returns:
            bool: 加载成功返回True，否则返回False
        """
        if rule_file:
            self.rule_file = rule_file
        
        if not self.rule_file:
            return False
        
        self.rules = load_yaml_mappings(self.rule_file)
        self.original_rules = self.rules.copy()
        return True
    
    def save_rules(self, rule_file: str = None) -> bool:
        """
        保存规则到文件
        
        Args:
            rule_file: 规则文件路径，默认使用初始化时的路径
        
        Returns:
            bool: 保存成功返回True，否则返回False
        """
        if rule_file:
            self.rule_file = rule_file
        
        if not self.rule_file:
            return False
        
        return save_yaml_mappings(self.rules, self.rule_file)
    
    def create_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新规则
        
        Args:
            rule: 规则字典，包含id、original、translated等字段
        
        Returns:
            Dict[str, Any]: 创建结果
        """
        # 验证规则格式
        if not self._validate_rule(rule):
            return {
                "status": "error",
                "message": "规则格式无效"
            }
        
        # 检查是否存在重复ID
        existing_rule = self.get_rule_by_id(rule.get("id"))
        if existing_rule:
            return {
                "status": "error",
                "message": f"已存在ID为{rule.get('id')}的规则"
            }
        
        # 添加规则
        self.rules.append(rule)
        
        return {
            "status": "success",
            "message": "规则创建成功",
            "rule": rule
        }
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新现有规则
        
        Args:
            rule_id: 规则ID
            updates: 要更新的字段和值
        
        Returns:
            Dict[str, Any]: 更新结果
        """
        # 查找规则
        rule_index = self._get_rule_index_by_id(rule_id)
        if rule_index == -1:
            return {
                "status": "error",
                "message": f"未找到ID为{rule_id}的规则"
            }
        
        # 验证更新内容
        updated_rule = self.rules[rule_index].copy()
        updated_rule.update(updates)
        if not self._validate_rule(updated_rule):
            return {
                "status": "error",
                "message": "更新后的规则格式无效"
            }
        
        # 更新规则
        self.rules[rule_index].update(updates)
        
        return {
            "status": "success",
            "message": "规则更新成功",
            "rule": self.rules[rule_index]
        }
    
    def delete_rule(self, rule_id: str) -> Dict[str, Any]:
        """
        删除规则
        
        Args:
            rule_id: 规则ID
        
        Returns:
            Dict[str, Any]: 删除结果
        """
        # 查找规则
        rule_index = self._get_rule_index_by_id(rule_id)
        if rule_index == -1:
            return {
                "status": "error",
                "message": f"未找到ID为{rule_id}的规则"
            }
        
        # 删除规则
        deleted_rule = self.rules.pop(rule_index)
        
        return {
            "status": "success",
            "message": "规则删除成功",
            "rule": deleted_rule
        }
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取规则
        
        Args:
            rule_id: 规则ID
        
        Returns:
            Optional[Dict[str, Any]]: 找到的规则，找不到返回None
        """
        for rule in self.rules:
            if rule.get("id") == rule_id:
                return rule
        return None
    
    def get_rule_by_original(self, original: str) -> Optional[Dict[str, Any]]:
        """
        根据原始文本获取规则
        
        Args:
            original: 原始文本
        
        Returns:
            Optional[Dict[str, Any]]: 找到的规则，找不到返回None
        """
        for rule in self.rules:
            if rule.get("original") == original:
                return rule
        return None
    
    def query_rules(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        查询规则
        
        Args:
            filters: 查询条件，例如{"status": "translated"}
        
        Returns:
            List[Dict[str, Any]]: 符合条件的规则列表
        """
        if not filters:
            return self.rules.copy()
        
        result = []
        for rule in self.rules:
            match = True
            for key, value in filters.items():
                if rule.get(key) != value:
                    match = False
                    break
            if match:
                result.append(rule)
        
        return result
    
    def import_rules(self, import_file: str, merge: bool = True) -> Dict[str, Any]:
        """
        从文件导入规则
        
        Args:
            import_file: 要导入的规则文件路径
            merge: 是否合并到现有规则，False表示替换
        
        Returns:
            Dict[str, Any]: 导入结果
        """
        if not import_file or not os.path.exists(import_file):
            return {
                "status": "error",
                "message": "导入文件无效"
            }
        
        imported_rules = load_yaml_mappings(import_file)
        if not imported_rules:
            return {
                "status": "error",
                "message": "导入文件内容无效"
            }
        
        if not merge:
            # 替换现有规则
            self.rules = imported_rules
        else:
            # 合并规则
            for rule in imported_rules:
                existing_index = self._get_rule_index_by_id(rule.get("id"))
                if existing_index == -1:
                    # 添加新规则
                    self.rules.append(rule)
                else:
                    # 更新现有规则
                    self.rules[existing_index].update(rule)
        
        return {
            "status": "success",
            "message": f"成功导入{len(imported_rules)}条规则",
            "imported_count": len(imported_rules)
        }
    
    def export_rules(self, export_file: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        导出规则到文件
        
        Args:
            export_file: 导出文件路径
            filters: 导出条件，例如{"status": "translated"}
        
        Returns:
            Dict[str, Any]: 导出结果
        """
        # 获取要导出的规则
        export_rules = self.query_rules(filters)
        
        # 导出规则
        success = save_yaml_mappings(export_rules, export_file)
        
        if success:
            return {
                "status": "success",
                "message": f"成功导出{len(export_rules)}条规则",
                "exported_count": len(export_rules),
                "export_file": export_file
            }
        else:
            return {
                "status": "error",
                "message": "规则导出失败"
            }
    
    def detect_conflicts(self) -> Dict[str, Any]:
        """
        检测规则冲突
        
        Returns:
            Dict[str, Any]: 冲突检测结果
        """
        conflicts = self.conflict_detector.detect_all_conflicts(self.rules)
        
        return {
            "status": "success",
            "message": "冲突检测完成",
            "total_conflicts": conflicts['total_conflicts'],
            "conflict_details": conflicts
        }
    
    def resolve_conflicts(self) -> Dict[str, Any]:
        """
        自动解决规则冲突
        
        Returns:
            Dict[str, Any]: 冲突解决结果
        """
        conflicts = self.conflict_detector.detect_all_conflicts(self.rules)
        
        if conflicts['total_conflicts'] == 0:
            return {
                "status": "success",
                "message": "没有检测到冲突"
            }
        
        # 自动解决冲突
        resolved_rules = self.conflict_detector.resolve_all_conflicts(self.rules)
        self.rules = resolved_rules
        
        return {
            "status": "success",
            "message": "冲突解决完成",
            "resolved_count": conflicts['total_conflicts']
        }
    
    def backup_rules(self, backup_dir: str = None) -> Dict[str, Any]:
        """
        备份规则文件
        
        Args:
            backup_dir: 备份目录，默认使用规则文件所在目录
        
        Returns:
            Dict[str, Any]: 备份结果
        """
        if not self.rule_file:
            return {
                "status": "error",
                "message": "没有可备份的规则文件"
            }
        
        if not backup_dir:
            backup_dir = os.path.dirname(self.rule_file)
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(self.rule_file)
        name, ext = os.path.splitext(base_name)
        backup_file = os.path.join(backup_dir, f"{name}_backup_{timestamp}{ext}")
        
        # 复制文件
        shutil.copy2(self.rule_file, backup_file)
        
        return {
            "status": "success",
            "message": "规则备份成功",
            "backup_file": backup_file
        }
    
    def restore_rules(self, backup_file: str) -> Dict[str, Any]:
        """
        从备份恢复规则
        
        Args:
            backup_file: 备份文件路径
        
        Returns:
            Dict[str, Any]: 恢复结果
        """
        if not backup_file or not os.path.exists(backup_file):
            return {
                "status": "error",
                "message": "备份文件无效"
            }
        
        # 加载备份文件
        backup_rules = load_yaml_mappings(backup_file)
        if not backup_rules:
            return {
                "status": "error",
                "message": "备份文件内容无效"
            }
        
        # 替换当前规则
        self.rules = backup_rules
        
        # 保存到原始文件
        if self.rule_file:
            self.save_rules()
        
        return {
            "status": "success",
            "message": "规则恢复成功"
        }
    
    def _validate_rule(self, rule: Dict[str, Any]) -> bool:
        """
        验证规则格式
        
        Args:
            rule: 规则字典
        
        Returns:
            bool: 格式有效返回True，否则返回False
        """
        required_fields = ["id", "original"]
        for field in required_fields:
            if field not in rule:
                return False
        return True
    
    def _get_rule_index_by_id(self, rule_id: str) -> int:
        """
        根据ID获取规则索引
        
        Args:
            rule_id: 规则ID
        
        Returns:
            int: 规则索引，找不到返回-1
        """
        for i, rule in enumerate(self.rules):
            if rule.get("id") == rule_id:
                return i
        return -1
    
    def _get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取规则
        
        Args:
            rule_id: 规则ID
        
        Returns:
            Optional[Dict[str, Any]]: 找到的规则，找不到返回None
        """
        index = self._get_rule_index_by_id(rule_id)
        if index != -1:
            return self.rules[index]
        return None


def manage_rules(
    rule_file: str,
    action: str,
    **kwargs
) -> Dict[str, Any]:
    """
    规则管理功能的入口函数
    
    Args:
        rule_file: 规则文件路径
        action: 操作类型，可选值：create, update, delete, get, query, detect-conflicts, resolve-conflicts, import, export, backup, restore
        **kwargs: 操作参数
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    manager = RuleManager(rule_file)
    
    actions = {
        "create": manager.create_rule,
        "update": manager.update_rule,
        "delete": manager.delete_rule,
        "get": manager.get_rule_by_id,
        "query": manager.query_rules,
        "detect-conflicts": manager.detect_conflicts,
        "resolve-conflicts": manager.resolve_conflicts,
        "import": manager.import_rules,
        "export": manager.export_rules,
        "backup": manager.backup_rules,
        "restore": manager.restore_rules
    }
    
    if action not in actions:
        return {
            "status": "error",
            "message": f"未知操作类型：{action}"
        }
    
    # 调用对应的方法
    if action in ["create", "detect-conflicts", "resolve-conflicts", "backup"]:
        result = actions[action](**kwargs)
    elif action in ["update"]:
        result = actions[action](kwargs.get("rule_id"), kwargs.get("updates"))
    elif action in ["delete", "get"]:
        result = actions[action](kwargs.get("rule_id"))
    elif action in ["query"]:
        result = actions[action](kwargs.get("filters"))
    elif action in ["import"]:
        result = actions[action](kwargs.get("import_file"), kwargs.get("merge", True))
    elif action in ["export"]:
        result = actions[action](kwargs.get("export_file"), kwargs.get("filters"))
    elif action in ["restore"]:
        result = actions[action](kwargs.get("backup_file"))
    else:
        result = {"status": "error", "message": f"不支持的操作：{action}"}
    
    # 保存规则（如果有修改）
    if action in ["create", "update", "delete", "resolve-conflicts", "import"]:
        manager.save_rules()
    
    return result
