#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则存储与管理模块

该模块提供规则的加载、保存、确定性排序、版本备份和管理功能
支持多种规则格式和操作
"""

import os
import yaml
import hashlib
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Set

from .yaml_utils import load_yaml_mappings, save_yaml_mappings


class RulesStore:
    """
    规则存储与管理类
    支持规则的加载、保存、确定性排序、版本备份和管理
    """
    
    def __init__(self, rules_file: str = ""):
        """
        初始化RulesStore
        
        Args:
            rules_file: 规则文件路径
        """
        self.rules_file = rules_file
        self.rules: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "mod_id": ""
        }
        self.backup_dir: Optional[str] = None
        
        if rules_file:
            self.set_rules_file(rules_file)
    
    def set_rules_file(self, rules_file: str):
        """
        设置规则文件路径
        
        Args:
            rules_file: 规则文件路径
        """
        self.rules_file = rules_file
        # 创建备份目录
        self.backup_dir = os.path.join(os.path.dirname(rules_file), "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def load_rules(self, rules_file: str = "") -> bool:
        """
        加载规则文件
        
        Args:
            rules_file: 规则文件路径，若为空则使用当前设置的文件
        
        Returns:
            bool: 是否加载成功
        """
        if rules_file:
            self.set_rules_file(rules_file)
        
        try:
            # 加载规则
            all_rules = load_yaml_mappings(self.rules_file)
            
            # 加载元数据（如果存在）
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            if isinstance(yaml_data, dict):
                # 提取元数据
                self.metadata = {
                    "version": yaml_data.get("version", "1.0"),
                    "created_at": yaml_data.get("created_at", datetime.now().isoformat()),
                    "updated_at": yaml_data.get("updated_at", datetime.now().isoformat()),
                    "mod_id": yaml_data.get("id", "")
                }
            
            self.rules = all_rules
            # 对规则进行确定性排序
            self._sort_rules()
            return True
        except Exception as e:
            print(f"[ERROR] 加载规则文件失败: {self.rules_file} - {e}")
            return False
    
    def save_rules(self, rules_file: str = "", version_control: bool = True) -> bool:
        """
        保存规则到文件
        
        Args:
            rules_file: 规则文件路径，若为空则使用当前设置的文件
            version_control: 是否启用版本控制
        
        Returns:
            bool: 是否保存成功
        """
        if rules_file:
            self.set_rules_file(rules_file)
        
        try:
            # 更新元数据
            self.metadata["updated_at"] = datetime.now().isoformat()
            
            # 对规则进行确定性排序
            self._sort_rules()
            
            # 保存规则
            success = save_yaml_mappings(
                self.rules, 
                self.rules_file, 
                version_control=version_control,
                mod_id=self.metadata["mod_id"]
            )
            
            return success
        except Exception as e:
            print(f"[ERROR] 保存规则文件失败: {self.rules_file} - {e}")
            return False
    
    def _sort_rules(self):
        """
        对规则进行确定性排序
        使用 occurrence_key 作为排序键
        """
        self.rules.sort(key=lambda x: x.get("id", ""))
    
    def create_backup(self) -> str:
        """
        创建规则文件的备份
        
        Returns:
            str: 备份文件路径
        """
        if not self.rules_file or not os.path.exists(self.rules_file):
            raise ValueError("规则文件不存在，无法创建备份")
        
        # 确保备份目录存在
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = os.path.basename(self.rules_file)
        backup_file = os.path.join(self.backup_dir, f"{os.path.splitext(file_name)[0]}_{timestamp}.yaml")
        
        # 创建备份
        shutil.copy2(self.rules_file, backup_file)
        
        return backup_file
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        列出所有备份文件
        
        Returns:
            List[Dict[str, Any]]: 备份文件列表，包含文件名、路径、创建时间和大小
        """
        backups = []
        
        if not self.backup_dir or not os.path.exists(self.backup_dir):
            return backups
        
        # 遍历备份目录中的所有文件
        for file_name in os.listdir(self.backup_dir):
            if file_name.endswith(".yaml") or file_name.endswith(".yml"):
                file_path = os.path.join(self.backup_dir, file_name)
                try:
                    # 获取文件创建时间
                    create_time = os.path.getctime(file_path)
                    formatted_time = datetime.fromtimestamp(create_time).isoformat()
                    
                    backups.append({
                        "file_name": file_name,
                        "file_path": file_path,
                        "created_at": formatted_time,
                        "file_size": os.path.getsize(file_path)
                    })
                except Exception as e:
                    print(f"[WARN] 读取备份文件信息失败: {file_path} - {e}")
        
        # 按创建时间倒序排序
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        
        return backups
    
    def restore_backup(self, backup_file: str) -> bool:
        """
        从备份文件恢复规则
        
        Args:
            backup_file: 备份文件路径
        
        Returns:
            bool: 是否恢复成功
        """
        if not os.path.exists(backup_file):
            print(f"[ERROR] 备份文件不存在: {backup_file}")
            return False
        
        try:
            # 创建当前规则文件的备份
            current_backup = self.create_backup()
            print(f"[INFO] 已创建当前规则文件的备份: {current_backup}")
            
            # 恢复备份
            shutil.copy2(backup_file, self.rules_file)
            
            # 重新加载规则
            self.load_rules()
            
            return True
        except Exception as e:
            print(f"[ERROR] 恢复备份失败: {backup_file} - {e}")
            return False
    
    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定ID的规则
        
        Args:
            rule_id: 规则ID
        
        Returns:
            Optional[Dict[str, Any]]: 规则字典，若不存在则返回None
        """
        for rule in self.rules:
            if rule.get("id") == rule_id:
                return rule
        return None
    
    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """
        添加新规则
        
        Args:
            rule: 规则字典
        
        Returns:
            bool: 是否添加成功
        """
        # 检查规则ID是否已存在
        if self.get_rule(rule.get("id", "")):
            print(f"[WARN] 规则ID已存在: {rule.get('id')}")
            return False
        
        # 添加创建时间
        if "created_at" not in rule:
            rule["created_at"] = datetime.now().isoformat()
        
        # 添加更新时间
        rule["updated_at"] = datetime.now().isoformat()
        
        # 添加到规则列表
        self.rules.append(rule)
        
        # 重新排序
        self._sort_rules()
        
        return True
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新规则
        
        Args:
            rule_id: 规则ID
            updates: 更新的字段和值
        
        Returns:
            bool: 是否更新成功
        """
        for i, rule in enumerate(self.rules):
            if rule.get("id") == rule_id:
                # 更新规则
                updates["updated_at"] = datetime.now().isoformat()
                self.rules[i].update(updates)
                
                # 重新排序
                self._sort_rules()
                
                return True
        
        print(f"[WARN] 未找到规则: {rule_id}")
        return False
    
    def delete_rule(self, rule_id: str) -> bool:
        """
        删除规则
        
        Args:
            rule_id: 规则ID
        
        Returns:
            bool: 是否删除成功
        """
        initial_len = len(self.rules)
        self.rules = [rule for rule in self.rules if rule.get("id") != rule_id]
        
        # 检查是否删除成功
        return len(self.rules) < initial_len
    
    def get_rules_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        根据状态获取规则
        
        Args:
            status: 规则状态
        
        Returns:
            List[Dict[str, Any]]: 符合条件的规则列表
        """
        return [rule for rule in self.rules if rule.get("status") == status]
    
    def get_rules_by_original(self, original: str) -> List[Dict[str, Any]]:
        """
        根据原始字符串获取规则
        
        Args:
            original: 原始字符串
        
        Returns:
            List[Dict[str, Any]]: 符合条件的规则列表
        """
        return [rule for rule in self.rules if rule.get("original") == original]
    
    def get_rules_by_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        根据文件路径获取规则
        
        Args:
            file_path: 文件路径
        
        Returns:
            List[Dict[str, Any]]: 符合条件的规则列表
        """
        return [rule for rule in self.rules if 
                rule.get("context", {}).get("file") == file_path or 
                rule.get("meta", {}).get("file") == file_path]
    
    def validate_rules(self) -> List[str]:
        """
        验证规则的合法性
        
        Returns:
            List[str]: 错误信息列表
        """
        errors = []
        seen_ids: Set[str] = set()
        
        for i, rule in enumerate(self.rules):
            rule_index = i + 1
            
            # 检查必要字段
            if "id" not in rule:
                errors.append(f"规则 {rule_index}: 缺少必要字段 'id'")
            else:
                rule_id = rule["id"]
                if rule_id in seen_ids:
                    errors.append(f"规则 {rule_index}: 重复的id '{rule_id}'")
                seen_ids.add(rule_id)
            
            if "original" not in rule:
                errors.append(f"规则 {rule_index}: 缺少必要字段 'original'")
            
            if "status" in rule:
                valid_statuses = ["translated", "untranslated", "needs_review", "SKIP", "KEEP"]
                if rule["status"] not in valid_statuses:
                    errors.append(f"规则 {rule_index}: 无效的状态 '{rule['status']}'")
            
            # 检查占位符一致性
            if "original" in rule and "translated" in rule:
                original = rule["original"]
                translated = rule["translated"]
                
                # 提取占位符
                original_placeholders = self._extract_placeholders(original)
                translated_placeholders = self._extract_placeholders(translated)
                
                if len(original_placeholders) != len(translated_placeholders):
                    errors.append(f"规则 {rule_index}: 占位符数量不一致 - 原始: {len(original_placeholders)}, 翻译: {len(translated_placeholders)}")
        
        return errors
    
    def _extract_placeholders(self, text: str) -> List[str]:
        """
        提取文本中的占位符
        
        Args:
            text: 文本字符串
        
        Returns:
            List[str]: 占位符列表
        """
        import re
        
        # 匹配各种占位符格式
        patterns = [
            r'%\w+',         # %s, %d 等
            r'\$\{.*?\}',     # ${placeholder} 格式
            r'\{.*?\}',       # {placeholder} 格式
            r'\$\w+'          # $variable 格式
        ]
        
        placeholders = []
        for pattern in patterns:
            placeholders.extend(re.findall(pattern, text))
        
        return placeholders
    
    def get_statistics(self) -> Dict[str, int]:
        """
        获取规则统计信息
        
        Returns:
            Dict[str, int]: 统计信息字典
        """
        stats = {
            "total_rules": len(self.rules),
            "translated_rules": len(self.get_rules_by_status("translated")),
            "untranslated_rules": len(self.get_rules_by_status("untranslated")),
            "needs_review_rules": len(self.get_rules_by_status("needs_review")),
            "skip_rules": len(self.get_rules_by_status("SKIP")),
            "keep_rules": len(self.get_rules_by_status("KEEP")),
            "with_translation": sum(1 for rule in self.rules if "translated" in rule and rule["translated"])
        }
        
        return stats
    
    def clear_rules(self):
        """
        清空所有规则
        """
        self.rules = []
        self.metadata["updated_at"] = datetime.now().isoformat()
    
    def import_rules(self, source_file: str, merge: bool = True) -> Dict[str, Any]:
        """
        从其他规则文件导入规则
        
        Args:
            source_file: 源规则文件路径
            merge: 是否合并到现有规则，否则替换
        
        Returns:
            Dict[str, Any]: 导入结果
        """
        # 加载源规则
        source_rules = load_yaml_mappings(source_file)
        
        if not merge:
            # 替换现有规则
            self.rules = source_rules
            self._sort_rules()
            
            return {
                "status": "success",
                "message": f"成功导入 {len(source_rules)} 条规则，替换了现有规则",
                "imported_count": len(source_rules),
                "merged_count": 0,
                "skipped_count": 0
            }
        
        # 合并规则
        imported_count = 0
        merged_count = 0
        skipped_count = 0
        
        # 创建现有规则ID集合
        existing_ids = {rule.get("id") for rule in self.rules}
        
        for source_rule in source_rules:
            rule_id = source_rule.get("id")
            
            if rule_id in existing_ids:
                # 规则已存在，尝试合并
                existing_rule = self.get_rule(rule_id)
                if existing_rule:
                    # 合并规则，保留现有规则的状态和元数据
                    merged_rule = existing_rule.copy()
                    
                    # 只合并特定字段
                    fields_to_merge = ["translated", "context", "placeholders"]
                    for field in fields_to_merge:
                        if field in source_rule:
                            merged_rule[field] = source_rule[field]
                    
                    # 更新现有规则
                    self.update_rule(rule_id, merged_rule)
                    merged_count += 1
                else:
                    skipped_count += 1
            else:
                # 新规则，直接添加
                self.add_rule(source_rule)
                imported_count += 1
                existing_ids.add(rule_id)
        
        return {
            "status": "success",
            "message": f"成功导入 {imported_count} 条规则，合并 {merged_count} 条规则，跳过 {skipped_count} 条规则",
            "imported_count": imported_count,
            "merged_count": merged_count,
            "skipped_count": skipped_count
        }
    
    def export_rules(self, output_file: str, format: str = "rich") -> bool:
        """
        导出规则到文件
        
        Args:
            output_file: 输出文件路径
            format: 导出格式，支持 "rich" 和 "simple"
        
        Returns:
            bool: 是否导出成功
        """
        try:
            if format == "simple":
                # 导出为简单映射格式
                simple_rules = []
                for rule in self.rules:
                    simple_rule = {
                        "original": rule.get("original", ""),
                        "translated": rule.get("translated", "")
                    }
                    simple_rules.append(simple_rule)
                
                # 保存为简单格式
                with open(output_file, 'w', encoding='utf-8') as f:
                    yaml.dump(simple_rules, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            else:
                # 导出为rich格式
                self.save_rules(output_file)
            
            return True
        except Exception as e:
            print(f"[ERROR] 导出规则失败: {output_file} - {e}")
            return False
    
    def generate_fingerprint(self, rule: Dict[str, Any]) -> str:
        """
        生成规则的指纹
        
        Args:
            rule: 规则字典
        
        Returns:
            str: 指纹字符串
        """
        # 使用规则的关键字段生成指纹
        fingerprint_data = {
            "original": rule.get("original", ""),
            "context": rule.get("context", {}),
            "meta": rule.get("meta", {})
        }
        
        # 转换为字符串
        data_str = str(fingerprint_data)
        
        # 生成SHA256哈希
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def add_fingerprints(self) -> int:
        """
        为所有规则添加指纹
        
        Returns:
            int: 添加的指纹数量
        """
        added_count = 0
        
        for rule in self.rules:
            if "fingerprint" not in rule:
                rule["fingerprint"] = self.generate_fingerprint(rule)
                added_count += 1
        
        return added_count
    
    def __len__(self) -> int:
        """
        获取规则数量
        
        Returns:
            int: 规则数量
        """
        return len(self.rules)
    
    def __iter__(self):
        """
        迭代规则
        
        Returns:
            Iterator[Dict[str, Any]]: 规则迭代器
        """
        return iter(self.rules)
    
    def __getitem__(self, index: int) -> Dict[str, Any]:
        """
        获取指定索引的规则
        
        Args:
            index: 规则索引
        
        Returns:
            Dict[str, Any]: 规则字典
        """
        return self.rules[index]
