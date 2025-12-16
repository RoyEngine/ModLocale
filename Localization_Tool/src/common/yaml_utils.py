#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YAML映射文件处理工具

该模块包含YAML映射文件的加载、验证和应用功能。
"""

import os
import yaml
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from .tree_sitter_utils import extract_ast_mappings


class RuleConflictDetector:
    """
    规则冲突检测器
    检测和解决YAML映射规则中的冲突
    """
    
    @staticmethod
    def detect_duplicate_ids(yaml_mappings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检测重复ID冲突
        
        Args:
            yaml_mappings: YAML映射列表
        
        Returns:
            List[Dict[str, Any]]: 冲突列表
        """
        conflicts = []
        id_map = {}
        
        for i, mapping in enumerate(yaml_mappings):
            mapping_id = mapping.get("id")
            if mapping_id:
                if mapping_id in id_map:
                    # 找到重复ID
                    conflicts.append({
                        "type": "duplicate_id",
                        "id": mapping_id,
                        "conflicts": [
                            {"index": id_map[mapping_id][0], "mapping": id_map[mapping_id][1]},
                            {"index": i, "mapping": mapping}
                        ]
                    })
                else:
                    id_map[mapping_id] = (i, mapping)
        
        return conflicts
    
    @staticmethod
    def detect_duplicate_originals(yaml_mappings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检测相同原始字符串但不同ID的冲突
        
        Args:
            yaml_mappings: YAML映射列表
        
        Returns:
            List[Dict[str, Any]]: 冲突列表
        """
        conflicts = []
        original_map = {}
        
        for i, mapping in enumerate(yaml_mappings):
            original = mapping.get("original")
            if original:
                if original in original_map:
                    # 找到相同原始字符串
                    original_map[original].append({"index": i, "mapping": mapping})
                else:
                    original_map[original] = [{"index": i, "mapping": mapping}]
        
        # 提取有多个映射的原始字符串
        for original, mappings in original_map.items():
            if len(mappings) > 1:
                conflicts.append({
                    "type": "duplicate_original",
                    "original": original,
                    "conflicts": mappings
                })
        
        return conflicts
    
    @staticmethod
    def detect_translation_conflicts(yaml_mappings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检测相同原始字符串但不同翻译的冲突
        
        Args:
            yaml_mappings: YAML映射列表
        
        Returns:
            List[Dict[str, Any]]: 冲突列表
        """
        conflicts = []
        original_map = {}
        
        for i, mapping in enumerate(yaml_mappings):
            original = mapping.get("original")
            translated = mapping.get("translated")
            if original and translated:
                if original in original_map:
                    # 检查翻译是否不同
                    existing_translations = original_map[original]
                    has_conflict = False
                    for existing in existing_translations:
                        if existing["translated"] != translated:
                            has_conflict = True
                            break
                    
                    if has_conflict:
                        existing_translations.append({"index": i, "mapping": mapping, "translated": translated})
                    else:
                        existing_translations.append({"index": i, "mapping": mapping, "translated": translated})
                else:
                    original_map[original] = [{"index": i, "mapping": mapping, "translated": translated}]
        
        # 提取有冲突的原始字符串
        for original, translations in original_map.items():
            if len(translations) > 1:
                # 检查是否有不同的翻译
                unique_translations = set(t["translated"] for t in translations)
                if len(unique_translations) > 1:
                    conflicts.append({
                        "type": "translation_conflict",
                        "original": original,
                        "unique_translations": list(unique_translations),
                        "conflicts": [t for t in translations]
                    })
        
        return conflicts
    
    @staticmethod
    def detect_all_conflicts(yaml_mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        检测所有类型的冲突
        
        Args:
            yaml_mappings: YAML映射列表
        
        Returns:
            Dict[str, Any]: 所有冲突信息
        """
        duplicate_ids = RuleConflictDetector.detect_duplicate_ids(yaml_mappings)
        duplicate_originals = RuleConflictDetector.detect_duplicate_originals(yaml_mappings)
        translation_conflicts = RuleConflictDetector.detect_translation_conflicts(yaml_mappings)
        
        return {
            "total_conflicts": len(duplicate_ids) + len(duplicate_originals) + len(translation_conflicts),
            "duplicate_ids": duplicate_ids,
            "duplicate_originals": duplicate_originals,
            "translation_conflicts": translation_conflicts,
            "conflict_summary": {
                "duplicate_ids": len(duplicate_ids),
                "duplicate_originals": len(duplicate_originals),
                "translation_conflicts": len(translation_conflicts)
            }
        }
    
    @staticmethod
    def resolve_conflicts(mappings: List[Dict[str, Any]], conflicts: Dict[str, Any], resolution_strategy: str = "latest") -> List[Dict[str, Any]]:
        """
        解决冲突
        
        Args:
            mappings: 原始映射列表
            conflicts: 冲突信息
            resolution_strategy: 解决策略，可选值：
                - latest: 使用最新的映射(默认)
                - first: 使用第一个映射
                - longest: 使用最长的翻译
                - shortest: 使用最短的翻译
                - manual: 手动解决(返回冲突信息)
        
        Returns:
            List[Dict[str, Any]]: 解决后的映射列表或冲突信息
        """
        if resolution_strategy == "manual":
            return conflicts
        
        print(f"[INFO] 使用{resolution_strategy}策略解决冲突")
        
        # 创建映射ID到索引的字典，用于快速查找
        mapping_dict = {}
        for i, mapping in enumerate(mappings):
            mapping_dict[mapping.get("id", f"auto_{i}")] = i
        
        # 解决重复ID冲突
        resolved_mappings = mappings.copy()
        
        # 解决重复ID冲突
        for conflict in conflicts["duplicate_ids"]:
            conflict_ids = [item["index"] for item in conflict["conflicts"]]
            conflict_mappings = [item["mapping"] for item in conflict["conflicts"]]
            
            if resolution_strategy == "latest":
                # 使用最后一个映射
                selected = conflict_mappings[-1]
                selected_index = conflict_ids[-1]
            elif resolution_strategy == "first":
                # 使用第一个映射
                selected = conflict_mappings[0]
                selected_index = conflict_ids[0]
            elif resolution_strategy == "longest":
                # 使用最长的翻译
                selected = max(conflict_mappings, key=lambda x: len(x.get("translated", "")))
                selected_index = conflict_ids[conflict_mappings.index(selected)]
            elif resolution_strategy == "shortest":
                # 使用最短的翻译
                selected = min(conflict_mappings, key=lambda x: len(x.get("translated", "")))
                selected_index = conflict_ids[conflict_mappings.index(selected)]
            else:
                # 默认使用最新的映射
                selected = conflict_mappings[-1]
                selected_index = conflict_ids[-1]
            
            # 保留选中的映射，移除其他冲突映射
            for i in sorted(conflict_ids, reverse=True):
                if i != selected_index:
                    del resolved_mappings[i]
        
        # 解决重复原始字符串冲突
        for conflict in conflicts["duplicate_originals"]:
            original = conflict["original"]
            conflict_ids = [item["index"] for item in conflict["conflicts"]]
            conflict_mappings = [item["mapping"] for item in conflict["conflicts"]]
            
            if resolution_strategy == "latest":
                selected = conflict_mappings[-1]
                selected_index = conflict_ids[-1]
            elif resolution_strategy == "first":
                selected = conflict_mappings[0]
                selected_index = conflict_ids[0]
            elif resolution_strategy == "longest":
                selected = max(conflict_mappings, key=lambda x: len(x.get("translated", "")))
                selected_index = conflict_ids[conflict_mappings.index(selected)]
            elif resolution_strategy == "shortest":
                selected = min(conflict_mappings, key=lambda x: len(x.get("translated", "")))
                selected_index = conflict_ids[conflict_mappings.index(selected)]
            else:
                selected = conflict_mappings[-1]
                selected_index = conflict_ids[-1]
            
            # 保留选中的映射，移除其他冲突映射
            for i in sorted(conflict_ids, reverse=True):
                if i != selected_index:
                    del resolved_mappings[i]
        
        # 解决翻译冲突
        for conflict in conflicts["translation_conflicts"]:
            original = conflict["original"]
            conflict_ids = [item["index"] for item in conflict["conflicts"]]
            conflict_mappings = [item["mapping"] for item in conflict["conflicts"]]
            
            if resolution_strategy == "latest":
                selected = conflict_mappings[-1]
                selected_index = conflict_ids[-1]
            elif resolution_strategy == "first":
                selected = conflict_mappings[0]
                selected_index = conflict_ids[0]
            elif resolution_strategy == "longest":
                selected = max(conflict_mappings, key=lambda x: len(x.get("translated", "")))
                selected_index = conflict_ids[conflict_mappings.index(selected)]
            elif resolution_strategy == "shortest":
                selected = min(conflict_mappings, key=lambda x: len(x.get("translated", "")))
                selected_index = conflict_ids[conflict_mappings.index(selected)]
            else:
                selected = conflict_mappings[-1]
                selected_index = conflict_ids[-1]
            
            # 保留选中的映射，移除其他冲突映射
            for i in sorted(conflict_ids, reverse=True):
                if i != selected_index:
                    del resolved_mappings[i]
        
        print(f"[OK] 冲突解决完成，剩余 {len(resolved_mappings)} 条映射")
        return resolved_mappings
    
    @staticmethod
    def generate_conflict_report(conflicts: Dict[str, Any]) -> str:
        """
        生成冲突报告
        
        Args:
            conflicts: 冲突信息
        
        Returns:
            str: 冲突报告
        """
        report = []
        report.append("# 规则冲突检测报告")
        report.append(f"\n## 冲突摘要")
        report.append(f"总冲突数: {conflicts['total_conflicts']}")
        report.append(f"重复ID: {conflicts['conflict_summary']['duplicate_ids']}")
        report.append(f"重复原始字符串: {conflicts['conflict_summary']['duplicate_originals']}")
        report.append(f"翻译冲突: {conflicts['conflict_summary']['translation_conflicts']}")
        
        if conflicts['duplicate_ids']:
            report.append(f"\n## 重复ID冲突")
            for conflict in conflicts['duplicate_ids']:
                report.append(f"\nID: {conflict['id']}")
                for i, item in enumerate(conflict['conflicts']):
                    report.append(f"  冲突 {i+1}:")
                    report.append(f"    索引: {item['index']}")
                    report.append(f"    原始字符串: {item['mapping'].get('original', 'N/A')}")
                    report.append(f"    翻译: {item['mapping'].get('translated', 'N/A')}")
        
        if conflicts['duplicate_originals']:
            report.append(f"\n## 重复原始字符串冲突")
            for conflict in conflicts['duplicate_originals']:
                report.append(f"\n原始字符串: {conflict['original']}")
                for i, item in enumerate(conflict['conflicts']):
                    report.append(f"  冲突 {i+1}:")
                    report.append(f"    索引: {item['index']}")
                    report.append(f"    ID: {item['mapping'].get('id', 'N/A')}")
                    report.append(f"    翻译: {item['mapping'].get('translated', 'N/A')}")
        
        if conflicts['translation_conflicts']:
            report.append(f"\n## 翻译冲突")
            for conflict in conflicts['translation_conflicts']:
                report.append(f"\n原始字符串: {conflict['original']}")
                report.append(f"  唯一翻译数: {len(conflict['unique_translations'])}")
                for i, item in enumerate(conflict['conflicts']):
                    report.append(f"  冲突 {i+1}:")
                    report.append(f"    索引: {item['index']}")
                    report.append(f"    ID: {item['mapping'].get('id', 'N/A')}")
                    report.append(f"    翻译: {item['translated']}")
        
        return '\n'.join(report)


class YAMLMappingValidator:
    """
    YAML映射验证器
    """
    
    @staticmethod
    def validate_mappings(ast_mappings: List[Dict[str, Any]], yaml_mappings: List[Dict[str, Any]]) -> List[str]:
        """
        验证AST映射与YAML映射的一致性
        
        Args:
            ast_mappings: AST映射列表
            yaml_mappings: YAML映射列表
        
        Returns:
            List[str]: 错误列表
        """
        errors = []
        
        # 创建YAML映射ID到映射的字典
        yaml_mapping_dict = {yaml_item["id"]: yaml_item for yaml_item in yaml_mappings}
        
        for ast_item in ast_mappings:
            yaml_item = yaml_mapping_dict.get(ast_item["id"])
            
            if yaml_item:
                # 验证占位符数量
                ast_placeholders = re.findall(r'[%]\w+|\$\{.*?\}|\{.*?\}', ast_item["original"])
                yaml_placeholders = re.findall(r'[%]\w+|\$\{.*?\}|\{.*?\}', yaml_item.get("translated", ""))
                
                if len(ast_placeholders) != len(yaml_placeholders):
                    errors.append(f"占位符数量不一致: {ast_item['id']} - AST: {len(ast_placeholders)}, YAML: {len(yaml_placeholders)}")
                
                # 验证状态合法性
                if yaml_item.get("status") not in ["translated", "untranslated", "needs_review"]:
                    errors.append(f"无效状态: {ast_item['id']} - {yaml_item.get('status')}")
            else:
                errors.append(f"未找到YAML映射: {ast_item['id']}")
        
        return errors
    
    @staticmethod
    def validate_yaml_structure(yaml_mapping: Dict[str, Any]) -> List[str]:
        """
        验证YAML映射的结构合法性
        
        Args:
            yaml_mapping: YAML映射
        
        Returns:
            List[str]: 错误列表
        """
        errors = []
        
        required_fields = ["id", "original"]
        for field in required_fields:
            if field not in yaml_mapping:
                errors.append(f"缺少必填字段: {field}")
        
        if "status" in yaml_mapping:
            if yaml_mapping["status"] not in ["translated", "untranslated", "needs_review"]:
                errors.append(f"无效状态值: {yaml_mapping['status']}")
        
        if "placeholders" in yaml_mapping:
            if not isinstance(yaml_mapping["placeholders"], list):
                errors.append(f"placeholders必须是列表类型")
        
        return errors
    
    @staticmethod
    def validate_yaml_file(file_path: str) -> List[str]:
        """
        验证YAML文件的合法性
        
        Args:
            file_path: YAML文件路径
        
        Returns:
            List[str]: 错误列表
        """
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(f"YAML解析错误: {e}")
            return errors
        except Exception as e:
            errors.append(f"读取YAML文件错误: {e}")
            return errors
        
        if not isinstance(yaml_data, list):
            errors.append(f"YAML文件必须包含一个列表")
            return errors
        
        for i, mapping in enumerate(yaml_data):
            item_errors = YAMLMappingValidator.validate_yaml_structure(mapping)
            if item_errors:
                for error in item_errors:
                    errors.append(f"第{i+1}项: {error}")
        
        return errors


def load_yaml_mappings(file_path: str) -> List[Dict[str, Any]]:
    """
    加载YAML映射文件，支持带有版本信息的YAML格式
    
    Args:
        file_path: YAML映射文件路径
    
    Returns:
        List[Dict[str, Any]]: YAML映射列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
        
        if not yaml_data:
            return []
        
        # 处理带有版本信息的YAML格式
        if isinstance(yaml_data, dict):
            # 检查是否是新版本格式
            if "mappings" in yaml_data:
                # 提取映射列表
                mappings = yaml_data["mappings"]
                # 确保映射列表是列表类型
                if isinstance(mappings, list):
                    return mappings
                elif mappings:
                    return [mappings]
                return []
        
        # 处理传统列表格式
        if isinstance(yaml_data, list):
            return yaml_data
        else:
            return [yaml_data]
    except yaml.YAMLError as e:
        print(f"[WARN]  解析YAML文件失败: {file_path} - {e}")
    except Exception as e:
        print(f"[WARN]  加载YAML文件失败: {file_path} - {e}")
    
    return []

def compare_yaml_versions(file1: str, file2: str) -> Dict[str, Any]:
    """
    比较两个YAML映射文件的版本差异
    
    Args:
        file1: 第一个YAML文件路径
        file2: 第二个YAML文件路径
    
    Returns:
        Dict[str, Any]: 差异信息
    """
    # 加载两个文件的映射
    mappings1 = load_yaml_mappings(file1)
    mappings2 = load_yaml_mappings(file2)
    
    # 创建ID到映射的字典
    mappings_dict1 = {item["id"]: item for item in mappings1 if "id" in item}
    mappings_dict2 = {item["id"]: item for item in mappings2 if "id" in item}
    
    # 找出只在file1中存在的映射
    only_in_file1 = [item for id, item in mappings_dict1.items() if id not in mappings_dict2]
    
    # 找出只在file2中存在的映射
    only_in_file2 = [item for id, item in mappings_dict2.items() if id not in mappings_dict1]
    
    # 找出内容不同的映射
    different_mappings = []
    common_ids = set(mappings_dict1.keys()) & set(mappings_dict2.keys())
    
    for id in common_ids:
        item1 = mappings_dict1[id]
        item2 = mappings_dict2[id]
        
        # 比较除了version和created_at之外的所有字段
        keys_to_compare = set(item1.keys()) | set(item2.keys()) - {"version", "created_at", "updated_at"}
        
        is_different = False
        for key in keys_to_compare:
            if item1.get(key) != item2.get(key):
                is_different = True
                break
        
        if is_different:
            different_mappings.append({
                "id": id,
                "file1": item1,
                "file2": item2
            })
    
    return {
        "only_in_file1": only_in_file1,
        "only_in_file2": only_in_file2,
        "different_mappings": different_mappings,
        "total_common": len(common_ids),
        "total_different": len(different_mappings),
        "total_only_in_file1": len(only_in_file1),
        "total_only_in_file2": len(only_in_file2)
    }

def merge_yaml_versions(file1: str, file2: str, output_file: str, prefer_file1: bool = True) -> bool:
    """
    合并两个YAML映射文件的版本
    
    Args:
        file1: 第一个YAML文件路径
        file2: 第二个YAML文件路径
        output_file: 输出文件路径
        prefer_file1: 是否优先使用file1的内容
    
    Returns:
        bool: 是否合并成功
    """
    # 比较两个文件的差异
    diff = compare_yaml_versions(file1, file2)
    
    # 加载两个文件的映射
    mappings1 = load_yaml_mappings(file1)
    mappings2 = load_yaml_mappings(file2)
    
    # 创建ID到映射的字典
    mappings_dict1 = {item["id"]: item for item in mappings1 if "id" in item}
    mappings_dict2 = {item["id"]: item for item in mappings2 if "id" in item}
    
    # 合并映射
    merged_mappings = []
    
    # 处理共同ID的映射
    for id in set(mappings_dict1.keys()) & set(mappings_dict2.keys()):
        if prefer_file1:
            merged_mappings.append(mappings_dict1[id])
        else:
            merged_mappings.append(mappings_dict2[id])
    
    # 添加只在file1中存在的映射
    for item in diff["only_in_file1"]:
        merged_mappings.append(item)
    
    # 添加只在file2中存在的映射
    for item in diff["only_in_file2"]:
        merged_mappings.append(item)
    
    # 保存合并后的映射
    return save_yaml_mappings(merged_mappings, output_file)

def list_yaml_versions(directory: str) -> List[Dict[str, Any]]:
    """
    列出指定目录下的所有YAML映射版本
    
    Args:
        directory: 目录路径
    
    Returns:
        List[Dict[str, Any]]: 版本列表，按时间排序
    """
    versions = []
    
    # 检查备份目录
    backup_dir = os.path.join(directory, "backups")
    if not os.path.exists(backup_dir):
        return versions
    
    # 遍历备份目录中的所有YAML文件
    for file_name in os.listdir(backup_dir):
        if file_name.endswith(".yaml") or file_name.endswith(".yml"):
            file_path = os.path.join(backup_dir, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    yaml_data = yaml.safe_load(f)
                
                # 提取版本信息
                version = _get_yaml_version(yaml_data)
                created_at = None
                
                if isinstance(yaml_data, dict):
                    if "created_at" in yaml_data:
                        created_at = yaml_data["created_at"]
                    elif "mappings" in yaml_data and yaml_data["mappings"]:
                        # 尝试从第一个映射中获取created_at
                        first_mapping = yaml_data["mappings"][0]
                        if isinstance(first_mapping, dict) and "created_at" in first_mapping:
                            created_at = first_mapping["created_at"]
                
                versions.append({
                    "file_name": file_name,
                    "file_path": file_path,
                    "version": version,
                    "created_at": created_at,
                    "file_size": os.path.getsize(file_path)
                })
            except Exception as e:
                print(f"[WARN]  读取版本文件失败: {file_path} - {e}")
    
    # 按时间排序
    versions.sort(key=lambda x: x["created_at"] if x["created_at"] else "", reverse=True)
    
    return versions

def restore_yaml_version(backup_file: str, target_file: str) -> bool:
    """
    从备份文件恢复YAML映射版本
    
    Args:
        backup_file: 备份文件路径
        target_file: 目标文件路径
    
    Returns:
        bool: 是否恢复成功
    """
    try:
        import shutil
        
        # 加载备份文件的映射
        mappings = load_yaml_mappings(backup_file)
        
        # 保存到目标文件
        return save_yaml_mappings(mappings, target_file)
    except Exception as e:
        print(f"[ERROR] 恢复YAML版本失败: {backup_file} -> {target_file} - {e}")
        return False


def _get_yaml_version(yaml_data: Any) -> str:
    """
    获取YAML映射的版本号
    
    Args:
        yaml_data: YAML数据
    
    Returns:
        str: 版本号，默认"1.0"
    """
    if isinstance(yaml_data, dict) and "version" in yaml_data:
        return yaml_data["version"]
    return "1.0"

def _get_yaml_mappings(yaml_data: Any) -> List[Dict[str, Any]]:
    """
    从YAML数据中获取映射列表
    
    Args:
        yaml_data: YAML数据
    
    Returns:
        List[Dict[str, Any]]: 映射列表
    """
    if isinstance(yaml_data, list):
        return yaml_data
    elif isinstance(yaml_data, dict) and "mappings" in yaml_data:
        return yaml_data["mappings"]
    return []

def _save_yaml_version(file_path: str, mappings: List[Dict[str, Any]], version: str = "1.0", mod_id: str = "") -> bool:
    """
    保存带有版本信息的YAML映射
    
    Args:
        file_path: 文件路径
        mappings: 映射列表
        version: 版本号
        mod_id: 模组ID，用于直接匹配文件夹
    
    Returns:
        bool: 是否保存成功
    """
    try:
        # 创建带有版本信息的YAML结构
        yaml_data = {
            "version": version,
            "created_at": datetime.now().isoformat(),
            "id": mod_id,  # 添加mod_id字段，用于直接匹配文件夹
            "mappings": mappings
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            # 写入中文注释
            f.write("# YAML映射规则文件\n")
            f.write("# 字段说明：\n")
            f.write("#   version: 版本信息\n")
            f.write("#   created_at: 创建时间\n")
            f.write("#   id: 模组唯一标识符，用于直接匹配文件夹\n")
            f.write("#   mappings: 映射规则列表\n")
            f.write("# 映射规则字段说明：\n")
            f.write("#   id: 唯一标识符，格式为 文件路径:行号\n")
            f.write("#   original: 原始字符串\n")
            f.write("#   translated: 翻译后的字符串\n")
            f.write("#   context: 上下文信息，包含父节点类型和节点类型\n")
            f.write("#   status: 翻译状态，可选值：untranslated, translated, needs_review\n")
            f.write("#   placeholders: 占位符列表\n")
            f.write("\n")
            yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return True
    except Exception as e:
        print(f"[ERROR] 保存带版本信息的YAML映射失败: {file_path} - {e}")
        return False

def save_yaml_mappings(mappings: List[Dict[str, Any]], file_path: str, version_control: bool = True, mod_id: str = "") -> bool:
    """
    保存YAML映射到文件，支持版本控制
    
    Args:
        mappings: YAML映射列表
        file_path: 文件路径
        version_control: 是否启用版本控制
        mod_id: 模组ID，用于直接匹配文件夹
    
    Returns:
        bool: 是否保存成功
    """
    try:
        import shutil
        from datetime import datetime
        
        # 确保目标目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 如果启用版本控制，保存历史版本
        if version_control and os.path.exists(file_path):
            # 创建备份目录
            backup_dir = os.path.join(os.path.dirname(file_path), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"mappings_{timestamp}.yaml")
            
            # 复制当前文件到备份目录
            shutil.copy2(file_path, backup_file)
            print(f"[OK] 已保存映射规则历史版本到: {backup_file}")
        
        # 保存当前版本
        if version_control:
            # 使用版本控制格式保存
            success = _save_yaml_version(file_path, mappings, mod_id=mod_id)
        else:
            # 使用传统格式保存，添加中文注释
            with open(file_path, 'w', encoding='utf-8') as f:
                # 写入中文注释
                f.write("# YAML映射规则文件\n")
                f.write("# 字段说明：\n")
                f.write("#   id: 唯一标识符，格式为 文件路径:行号\n")
                f.write("#   original: 原始字符串\n")
                f.write("#   translated: 翻译后的字符串\n")
                f.write("#   context: 上下文信息，包含父节点类型和节点类型\n")
                f.write("#   status: 翻译状态，可选值：untranslated, translated, needs_review\n")
                f.write("#   placeholders: 占位符列表\n")
                f.write("\n")
                yaml.dump(mappings, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            success = True
        
        if success:
            print(f"[OK] 映射规则已保存到: {file_path}")
        else:
            print(f"[ERROR] 映射规则保存失败: {file_path}")
        return success
    except Exception as e:
        print(f"[ERROR] 保存YAML映射失败: {file_path} - {e}")
        return False


def generate_translation_rules(english_mappings: List[Dict[str, Any]], chinese_mappings: List[Dict[str, Any]], output_file: str, mod_id: str = "") -> bool:
    """
    利用双语数据生成翻译规则文件
    
    Args:
        english_mappings: 英文映射列表
        chinese_mappings: 中文映射列表
        output_file: 输出文件路径
        mod_id: 模组ID
        
    Returns:
        bool: 是否生成成功
    """
    print(f"[INFO] 开始生成翻译规则文件")
    print(f"[INFO] 英文映射条目数: {len(english_mappings)}")
    print(f"[INFO] 中文映射条目数: {len(chinese_mappings)}")
    
    # 数据验证
    if not english_mappings:
        print(f"[ERROR] 英文映射数据为空")
        return False
    
    if not chinese_mappings:
        print(f"[ERROR] 中文映射数据为空")
        return False
    
    # 验证数据对齐
    if len(english_mappings) != len(chinese_mappings):
        print(f"[WARN] 英文和中文映射条目数不一致: 英文{len(english_mappings)}条，中文{len(chinese_mappings)}条")
        # 只处理前N条，N为较小的数量
        min_len = min(len(english_mappings), len(chinese_mappings))
        english_mappings = english_mappings[:min_len]
        chinese_mappings = chinese_mappings[:min_len]
        print(f"[INFO] 只处理前{min_len}条映射数据")
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 生成翻译规则
    rules = []
    
    # 遍历双语映射对，添加数据验证
    for i, (en_item, zh_item) in enumerate(zip(english_mappings, chinese_mappings)):
        # 验证条目完整性
        if not en_item or not isinstance(en_item, dict):
            print(f"[WARN] 跳过无效的英文映射条目 #{i+1}")
            continue
        
        if not zh_item or not isinstance(zh_item, dict):
            print(f"[WARN] 跳过无效的中文映射条目 #{i+1}")
            continue
        
        original = en_item.get('original')
        if not original:
            print(f"[WARN] 跳过缺少original字段的英文映射条目 #{i+1}")
            continue
        
        # 获取中文翻译
        translated = zh_item.get('original', '')
        if not translated:
            print(f"[WARN] 中文映射条目 #{i+1}缺少翻译内容，使用空字符串")
        
        # 构建规则条目
        rule = {
            'id': en_item.get('id', f'auto_{i+1}'),
            'original': original,
            'translated': translated,
            'context': en_item.get('context', {}),
            'status': 'translated',
            'placeholders': en_item.get('placeholders', []),
            'created_at': datetime.now().isoformat()
        }
        rules.append(rule)
    
    # 检查生成的规则数量
    if not rules:
        print(f"[ERROR] 没有生成任何规则，可能是数据格式错误")
        return False
    
    # 保存规则文件
    success = save_yaml_mappings(rules, output_file, version_control=True, mod_id=mod_id)
    
    if success:
        print(f"[OK] 翻译规则已生成到: {output_file}")
        print(f"[OK] 生成规则条目数: {len(rules)}")
    else:
        print(f"[ERROR] 翻译规则生成失败")
    
    return success


def generate_incremental_rules(english_mappings: List[Dict[str, Any]], existing_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    基于双语对生成增量规则
    
    Args:
        english_mappings: 新的英文映射列表
        existing_rules: 现有的翻译规则列表
        
    Returns:
        List[Dict[str, Any]]: 增量规则列表
    """
    print(f"[INFO] 开始生成增量规则")
    print(f"[INFO] 新的英文映射条目数: {len(english_mappings)}")
    print(f"[INFO] 现有规则条目数: {len(existing_rules)}")
    
    # 创建现有规则的字典，用于快速查找
    existing_dict = {item['original']: item for item in existing_rules}
    
    incremental_rules = []
    
    for en_item in english_mappings:
        original = en_item.get('original', '')
        
        if original in existing_dict:
            # 已存在的规则，保留翻译，标记为保留
            existing_rule = existing_dict[original].copy()
            existing_rule['status'] = 'translated'
            incremental_rules.append(existing_rule)
        else:
            # 新的规则，需要翻译，标记为未翻译
            new_rule = {
                'id': en_item.get('id', ''),
                'original': original,
                'translated': '',
                'context': en_item.get('context', {}),
                'status': 'untranslated',
                'placeholders': en_item.get('placeholders', [])
            }
            incremental_rules.append(new_rule)
    
    print(f"[OK] 增量规则生成完成，共 {len(incremental_rules)} 条")
    
    return incremental_rules


def update_translation_rules(existing_rules_file: str, new_english_file: str, new_chinese_file: str, output_file: str, mod_id: str = "") -> bool:
    """
    更新现有规则，确保增量学习
    
    Args:
        existing_rules_file: 现有规则文件路径
        new_english_file: 新的英文映射文件路径
        new_chinese_file: 新的中文映射文件路径
        output_file: 输出文件路径
        mod_id: 模组ID
        
    Returns:
        bool: 是否更新成功
    """
    print(f"[INFO] 开始更新翻译规则")
    print(f"[INFO] 现有规则文件: {existing_rules_file}")
    print(f"[INFO] 新的英文文件: {new_english_file}")
    print(f"[INFO] 新的中文文件: {new_chinese_file}")
    
    # 验证输入文件是否存在
    for file_path in [existing_rules_file, new_english_file, new_chinese_file]:
        if not os.path.exists(file_path):
            print(f"[ERROR] 文件不存在: {file_path}")
            return False
    
    # 加载现有规则
    existing_rules = load_yaml_mappings(existing_rules_file)
    print(f"[INFO] 现有规则条目数: {len(existing_rules)}")
    
    # 加载新的英文和中文映射
    new_english_mappings = load_yaml_mappings(new_english_file)
    new_chinese_mappings = load_yaml_mappings(new_chinese_file)
    print(f"[INFO] 新的英文映射条目数: {len(new_english_mappings)}")
    print(f"[INFO] 新的中文映射条目数: {len(new_chinese_mappings)}")
    
    # 数据对齐验证
    if len(new_english_mappings) != len(new_chinese_mappings):
        print(f"[WARN] 新的英文和中文映射条目数不一致")
        min_len = min(len(new_english_mappings), len(new_chinese_mappings))
        new_english_mappings = new_english_mappings[:min_len]
        new_chinese_mappings = new_chinese_mappings[:min_len]
        print(f"[INFO] 只处理前{min_len}条新映射数据")
    
    # 创建现有规则的字典，用于快速查找
    existing_dict = {}
    for rule in existing_rules:
        original = rule.get('original')
        if original:
            existing_dict[original] = rule
    
    # 生成更新后的规则
    updated_rules = []
    new_entries = 0
    updated_entries = 0
    skipped_entries = 0
    
    for i, (en_item, zh_item) in enumerate(zip(new_english_mappings, new_chinese_mappings)):
        original = en_item.get('original')
        if not original:
            print(f"[WARN] 跳过缺少original字段的新英文映射条目 #{i+1}")
            skipped_entries += 1
            continue
        
        translated = zh_item.get('original', '')
        
        if original in existing_dict:
            # 已有该原始字符串的规则，更新翻译
            existing_rule = existing_dict[original].copy()
            
            # 只更新翻译和状态，保留其他字段
            existing_rule['translated'] = translated
            existing_rule['status'] = 'translated'
            existing_rule['updated_at'] = datetime.now().isoformat()
            
            updated_rules.append(existing_rule)
            updated_entries += 1
        else:
            # 新的原始字符串，创建新规则
            new_rule = {
                'id': en_item.get('id', f'auto_{i+1}'),
                'original': original,
                'translated': translated,
                'context': en_item.get('context', {}),
                'status': 'translated',
                'placeholders': en_item.get('placeholders', []),
                'created_at': datetime.now().isoformat()
            }
            updated_rules.append(new_rule)
            new_entries += 1
    
    # 添加未在新映射中出现的现有规则（保留未翻译内容）
    for rule in existing_rules:
        original = rule.get('original')
        if original and original not in {r.get('original') for r in updated_rules}:
            updated_rules.append(rule.copy())
            skipped_entries += 1
    
    # 检查更新后的规则数量
    if not updated_rules:
        print(f"[ERROR] 没有生成任何更新后的规则")
        return False
    
    # 保存更新后的规则
    success = save_yaml_mappings(updated_rules, output_file, version_control=True, mod_id=mod_id)
    
    if success:
        print(f"[OK] 翻译规则已更新到: {output_file}")
        print(f"[OK] 更新统计:")
        print(f"      新增规则: {new_entries} 条")
        print(f"      更新规则: {updated_entries} 条")
        print(f"      跳过规则: {skipped_entries} 条")
        print(f"      总规则数: {len(updated_rules)} 条")
    else:
        print(f"[ERROR] 翻译规则更新失败")
    
    return success


def generate_initial_yaml_mappings(ast_mappings: List[Dict[str, Any]], mark_unmapped: bool = False) -> List[Dict[str, Any]]:
    """
    基于AST映射生成初始YAML映射
    
    Args:
        ast_mappings: AST映射列表
        mark_unmapped: 是否将未映射内容标记为"unmapped"状态
    
    Returns:
        List[Dict[str, Any]]: 初始YAML映射列表
    """
    yaml_mappings = []
    
    for ast_item in ast_mappings:
        yaml_item = {
            "id": ast_item["id"],
            "original": ast_item["original"],
            "translated": "" if mark_unmapped else ast_item["original"],  # 未映射时为空字符串
            "context": ast_item.get("context"),
            "status": "unmapped" if mark_unmapped else "untranslated",  # 支持未映射标记
            "placeholders": []
        }
        
        # 提取占位符信息
        placeholders = re.findall(r'[%]\w+|\$\{.*?\}|\{.*?\}', ast_item["original"])
        if placeholders:
            for i, placeholder in enumerate(placeholders):
                yaml_item["placeholders"].append({
                    "type": f"placeholder_{i+1}",
                    "example": placeholder
                })
        
        yaml_mappings.append(yaml_item)
    
    return yaml_mappings


def apply_yaml_mapping(source_file: str, yaml_mappings: List[Dict[str, Any]]) -> str:
    """
    应用YAML映射到源代码文件
    
    Args:
        source_file: 源代码文件路径
        yaml_mappings: YAML映射列表
    
    Returns:
        str: 应用映射后的源代码
    """
    from src.common.tree_sitter_utils import extract_strings_from_file
    
    # 提取源文件中的字符串
    source_strings = extract_strings_from_file(source_file)
    
    if not source_strings:
        print(f"[WARN]  未从文件 {source_file} 提取到任何字符串")
        # 读取并返回原始内容
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[WARN]  读取源文件失败: {source_file} - {e}")
            return ""
    
    # 创建映射字典，使用original作为键，translated作为值
    mapping_dict = {}
    unmapped_strings = set()
    
    for mapping in yaml_mappings:
        if "original" in mapping:
            original = mapping["original"]
            if "translated" in mapping and mapping["status"] in ["translated", "untranslated"]:
                translated = mapping["translated"]
                mapping_dict[original] = translated
            else:
                # 标记为未映射字符串
                unmapped_strings.add(original)
    
    # 读取源文件内容
    try:
        with open(source_file, 'rb') as f:
            content = f.read()
    except Exception as e:
        print(f"[WARN]  读取源文件失败: {source_file} - {e}")
        return ""
    
    # 应用映射，从后往前替换，避免位置偏移问题
    # 确保meta字段中包含start_line
    for string_info in source_strings:
        if "start_line" not in string_info["meta"]:
            string_info["meta"]["start_line"] = string_info["meta"].get("line", 1)
    
    sorted_strings = sorted(source_strings, key=lambda x: x["meta"]["start_line"], reverse=True)
    
    result = content
    for string_info in sorted_strings:
        original = string_info["original"]
        if original in mapping_dict:
            translated = mapping_dict[original]
            start_byte = string_info["meta"].get("start_byte", None)
            end_byte = string_info["meta"].get("end_byte", None)
            
            if start_byte is not None and end_byte is not None:
                # 替换字符串内容
                result = result[:start_byte] + translated.encode('utf-8') + result[end_byte:]
                line_num = string_info["meta"]["start_line"]
                print(f"OK 替换 {source_file}:{line_num} - {original} -> {translated}")
        elif original in unmapped_strings:
            # 记录未映射字符串
            line_num = string_info["meta"]["start_line"]
            print(f"[WARN]  未映射内容: {source_file}:{line_num} - {original}")
        else:
            # 未在映射规则中找到的字符串，标记为未映射
            line_num = string_info["meta"]["start_line"]
            print(f"[WARN]  未映射内容: {source_file}:{line_num} - {original}")
    
    # 返回应用映射后的内容
    try:
        return result.decode('utf-8')
    except Exception as e:
        print(f"[WARN]  解码映射后的内容失败: {source_file} - {e}")
        return ""


def create_yaml_mapping_from_directory(root_dir: str, output_file: str) -> bool:
    """
    从目录创建YAML映射文件
    
    Args:
        root_dir: 源代码目录
        output_file: 输出YAML文件路径
    
    Returns:
        bool: 是否创建成功
    """
    # 提取AST映射
    ast_mappings = extract_ast_mappings(root_dir)
    
    if not ast_mappings:
        print(f"[WARN]  未从目录 {root_dir} 提取到任何字符串")
        return False
    
    # 生成初始YAML映射
    yaml_mappings = generate_initial_yaml_mappings(ast_mappings)
    
    # 保存到文件
    return save_yaml_mappings(yaml_mappings, output_file)


def update_mapping_status(mappings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    根据映射结果更新状态
    
    Args:
        mappings: 映射列表
    
    Returns:
        List[Dict[str, Any]]: 更新状态后的映射列表
    """
    updated_mappings = []
    
    for mapping in mappings:
        updated_mapping = mapping.copy()
        
        # 根据translated字段更新状态
        if not updated_mapping.get("translated"):
            updated_mapping["status"] = "unmapped"
        elif updated_mapping["status"] == "unmapped":
            updated_mapping["status"] = "translated"
        
        updated_mappings.append(updated_mapping)
    
    return updated_mappings


def merge_mapping_rules(existing_rules: List[Dict[str, Any]], new_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    合并现有规则与新提取的规则
    
    Args:
        existing_rules: 现有映射规则
        new_rules: 新提取的映射规则
    
    Returns:
        List[Dict[str, Any]]: 合并后的映射规则
    """
    # 创建现有规则ID集合
    existing_ids = {rule["id"] for rule in existing_rules if "id" in rule}
    
    merged_rules = existing_rules.copy()
    
    # 添加新规则(不覆盖现有规则)
    for new_rule in new_rules:
        if "id" in new_rule and new_rule["id"] not in existing_ids:
            merged_rules.append(new_rule)
    
    return merged_rules


def extract_mappings_from_processed_folder(processed_folder: str, language: str = "Chinese") -> List[Dict[str, Any]]:
    """
    从已处理的文件夹中提取映射规则
    
    Args:
        processed_folder: 已处理的文件夹路径
        language: 语言类型
    
    Returns:
        List[Dict[str, Any]]: 提取的映射规则列表
    """
    from src.common.tree_sitter_utils import extract_ast_mappings
    
    print(f"[INFO] 从已处理文件夹提取映射规则: {processed_folder}")
    
    # 提取AST映射
    ast_mappings = extract_ast_mappings(processed_folder)
    
    if not ast_mappings:
        print(f"[WARN]  未从文件夹 {processed_folder} 提取到任何字符串")
        return []
    
    # 生成包含未映射标记的映射规则
    yaml_mappings = generate_initial_yaml_mappings(ast_mappings, mark_unmapped=True)
    
    return yaml_mappings


def update_yaml_mapping(yaml_file: str, ast_mappings: List[Dict[str, Any]]) -> bool:
    """
    更新YAML映射文件，添加新的AST映射
    
    Args:
        yaml_file: 现有YAML文件路径
        ast_mappings: 新的AST映射列表
    
    Returns:
        bool: 是否更新成功
    """
    # 加载现有YAML映射
    existing_mappings = load_yaml_mappings(yaml_file)
    
    # 创建现有映射ID集合
    existing_ids = {item["id"] for item in existing_mappings}
    
    # 生成新的YAML映射
    new_mappings = []
    for ast_item in ast_mappings:
        if ast_item["id"] not in existing_ids:
            new_item = {
                "id": ast_item["id"],
                "original": ast_item["original"],
                "translated": "",  # 新增内容默认为未映射
                "context": ast_item.get("context"),
                "status": "unmapped",  # 新增内容标记为未映射
                "placeholders": []
            }
            new_mappings.append(new_item)
    
    if new_mappings:
        # 合并映射
        merged_mappings = existing_mappings + new_mappings
        # 更新状态
        updated_mappings = update_mapping_status(merged_mappings)
        # 保存更新后的映射
        return save_yaml_mappings(updated_mappings, yaml_file)
    
    print(f"OK YAML文件 {yaml_file} 已是最新，没有添加新映射")
    return True


def generate_unmapped_report(rules: List[Dict[str, Any]], output_file: str = None) -> Dict[str, Any]:
    """
    生成未映射内容报告
    
    Args:
        rules: 映射规则列表
        output_file: 输出报告文件路径
    
    Returns:
        Dict[str, Any]: 未映射内容报告
    """
    from datetime import datetime
    
    # 统计未映射内容
    total_rules = len(rules)
    unmapped_rules = [r for r in rules if r['status'] == 'unmapped']
    unmapped_count = len(unmapped_rules)
    mapped_count = total_rules - unmapped_count
    
    # 计算未映射比例
    unmapped_ratio = (unmapped_count / total_rules) * 100 if total_rules > 0 else 0
    
    # 按文件路径分组统计未映射内容
    file_statistics = {}
    for rule in unmapped_rules:
        # 从id中提取文件路径(格式：文件路径:行号)
        if ':' in rule['id']:
            file_path = rule['id'].split(':')[0]
        else:
            file_path = 'unknown'
        
        if file_path not in file_statistics:
            file_statistics[file_path] = {
                'unmapped_count': 0,
                'rules': []
            }
        
        file_statistics[file_path]['unmapped_count'] += 1
        file_statistics[file_path]['rules'].append(rule)
    
    # 生成报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_rules': total_rules,
        'mapped_count': mapped_count,
        'unmapped_count': unmapped_count,
        'unmapped_ratio': round(unmapped_ratio, 2),
        'file_statistics': file_statistics,
        'unmapped_rules': unmapped_rules
    }
    
    # 保存报告
    if output_file:
        import json
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 保存为JSON格式
        if output_file.endswith('.json'):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"[OK] JSON报告已保存到: {output_file}")
        # 保存为文本格式
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# 未映射内容报告\n\n")
                f.write(f"生成时间: {report['timestamp']}\n")
                f.write(f"总规则数: {report['total_rules']}\n")
                f.write(f"已映射规则: {report['mapped_count']}\n")
                f.write(f"未映射规则: {report['unmapped_count']}\n")
                f.write(f"未映射比例: {report['unmapped_ratio']}%\n\n")
                
                f.write("## 按文件统计\n\n")
                for file_path, stats in sorted(file_statistics.items(), key=lambda x: x[1]['unmapped_count'], reverse=True):
                    f.write(f"### {file_path}\n")
                    f.write(f"未映射数量: {stats['unmapped_count']}\n")
                    f.write("\n")
                    for rule in stats['rules'][:10]:  # 每个文件只显示前10个
                        f.write(f"- {rule['original']}\n")
                    if len(stats['rules']) > 10:
                        f.write(f"... 还有 {len(stats['rules']) - 10} 条未映射内容\n")
                    f.write("\n")
            print(f"[OK] 文本报告已保存到: {output_file}")
    
    return report


def generate_translation_report(rules: List[Dict[str, Any]], output_file: str = None, format: str = "markdown") -> Dict[str, Any]:
    """
    生成完整的翻译报告
    
    Args:
        rules: 映射规则列表
        output_file: 输出报告文件路径
        format: 报告格式，可选值：markdown, json
    
    Returns:
        Dict[str, Any]: 翻译报告
    """
    from datetime import datetime
    
    # 统计不同状态的规则数量
    total_rules = len(rules)
    
    # 状态统计
    status_counts = {
        'translated': 0,
        'untranslated': 0,
        'unmapped': 0,
        'needs_review': 0,
        'new': 0
    }
    
    for rule in rules:
        status = rule.get('status', 'untranslated')
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts[status] = 1
    
    # 计算翻译进度
    translated_count = status_counts['translated']
    translation_progress = (translated_count / total_rules) * 100 if total_rules > 0 else 0
    
    # 检测冲突
    detector = RuleConflictDetector()
    conflicts = detector.detect_all_conflicts(rules)
    
    # 按文件路径分组统计
    file_statistics = {}
    for rule in rules:
        if ':' in rule['id']:
            file_path = rule['id'].split(':')[0]
        else:
            file_path = 'unknown'
        
        if file_path not in file_statistics:
            file_statistics[file_path] = {
                'total': 0,
                'status_counts': status_counts.copy(),
                'rules': []
            }
        
        file_statistics[file_path]['total'] += 1
        status = rule.get('status', 'untranslated')
        file_statistics[file_path]['status_counts'][status] += 1
        file_statistics[file_path]['rules'].append(rule)
    
    # 生成报告数据
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_rules': total_rules,
        'status_counts': status_counts,
        'translation_progress': round(translation_progress, 2),
        'conflicts': conflicts,
        'file_statistics': file_statistics,
        'rules': rules
    }
    
    # 保存报告
    if output_file:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        if format == 'json' or output_file.endswith('.json'):
            # 保存为JSON格式
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"[OK] JSON报告已保存到: {output_file}")
        else:
            # 保存为Markdown格式
            with open(output_file, 'w', encoding='utf-8') as f:
                # 写入报告标题和基本信息
                f.write("# 翻译进度报告\n\n")
                f.write(f"生成时间: {report['timestamp']}\n")
                f.write(f"总规则数: {report['total_rules']}\n")
                f.write(f"翻译进度: {report['translation_progress']}%\n")
                f.write("\n")
                
                # 写入状态统计
                f.write("## 状态统计\n\n")
                f.write("| 状态 | 数量 | 占比 |\n")
                f.write("|------|------|------|\n")
                for status, count in report['status_counts'].items():
                    ratio = (count / total_rules) * 100 if total_rules > 0 else 0
                    f.write(f"| {status} | {count} | {round(ratio, 2)}% |\n")
                f.write("\n")
                
                # 写入冲突统计
                f.write("## 冲突统计\n\n")
                total_conflicts = report['conflicts']['total_conflicts']
                f.write(f"总冲突数: {total_conflicts}\n")
                
                if total_conflicts > 0:
                    f.write("\n")
                    f.write("### 冲突详情\n\n")
                    
                    # 重复ID冲突
                    if report['conflicts']['duplicate_ids']:
                        f.write("#### 重复ID冲突\n\n")
                        for conflict in report['conflicts']['duplicate_ids']:
                            f.write(f"- ID: {conflict['id']}\n")
                            for i, item in enumerate(conflict['conflicts']):
                                f.write(f"  冲突 {i+1}: {item['mapping'].get('original', 'N/A')} -> {item['mapping'].get('translated', 'N/A')}\n")
                        f.write("\n")
                    
                    # 重复原始字符串冲突
                    if report['conflicts']['duplicate_originals']:
                        f.write("#### 重复原始字符串冲突\n\n")
                        for conflict in report['conflicts']['duplicate_originals']:
                            f.write(f"- 原始字符串: {conflict['original']}\n")
                            for i, item in enumerate(conflict['conflicts']):
                                f.write(f"  冲突 {i+1}: {item['mapping'].get('translated', 'N/A')} (ID: {item['mapping'].get('id', 'N/A')})\n")
                        f.write("\n")
                    
                    # 翻译冲突
                    if report['conflicts']['translation_conflicts']:
                        f.write("#### 翻译冲突\n\n")
                        for conflict in report['conflicts']['translation_conflicts']:
                            f.write(f"- 原始字符串: {conflict['original']}\n")
                            f.write(f"  不同翻译: {', '.join(conflict['unique_translations'])}\n")
                        f.write("\n")
                else:
                    f.write("无冲突\n\n")
                
                # 写入按文件统计
                f.write("## 按文件统计\n\n")
                for file_path, stats in sorted(file_statistics.items(), key=lambda x: x[1]['total'], reverse=True):
                    f.write(f"### {file_path}\n\n")
                    f.write(f"总规则数: {stats['total']}\n")
                    
                    # 计算该文件的翻译进度
                    file_translated = stats['status_counts']['translated']
                    file_progress = (file_translated / stats['total']) * 100 if stats['total'] > 0 else 0
                    f.write(f"翻译进度: {round(file_progress, 2)}%\n")
                    
                    f.write("\n")
                    f.write("| 状态 | 数量 |\n")
                    f.write("|------|------|\n")
                    for status, count in stats['status_counts'].items():
                        if count > 0:
                            f.write(f"| {status} | {count} |\n")
                    f.write("\n")
            
            print(f"[OK] {format.upper()}报告已保存到: {output_file}")
    
    return report


def list_unmapped_content(rules: List[Dict[str, Any]], output_file: str = None) -> None:
    """
    列出所有未映射内容
    
    Args:
        rules: 映射规则列表
        output_file: 输出文件路径
    """
    # 过滤未映射规则
    unmapped_rules = [r for r in rules if r['status'] == 'unmapped']
    
    if not unmapped_rules:
        print("[INFO] 没有未映射内容")
        return
    
    output_lines = []
    output_lines.append("=" * 60)
    output_lines.append("          未映射内容列表")
    output_lines.append("=" * 60)
    output_lines.append(f"未映射内容总数: {len(unmapped_rules)}")
    output_lines.append("")
    
    for i, rule in enumerate(unmapped_rules, 1):
        output_lines.append(f"[{i}] {rule['original']}")
        output_lines.append(f"  文件: {rule['id'].split(':')[0] if ':' in rule['id'] else 'unknown'}")
        if rule.get('context'):
            output_lines.append(f"  上下文: {rule['context']}")
        output_lines.append("")
    
    output_content = "\n".join(output_lines)
    
    if output_file:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"[OK] 未映射内容列表已保存到: {output_file}")
    else:
        print(output_content)


def mark_unmapped_as_translated(rules: List[Dict[str, Any]], output_file: str = None) -> List[Dict[str, Any]]:
    """
    将所有未映射内容标记为已翻译
    
    Args:
        rules: 映射规则列表
        output_file: 输出文件路径
    
    Returns:
        List[Dict[str, Any]]: 更新后的映射规则列表
    """
    updated_rules = []
    updated_count = 0
    
    for rule in rules:
        updated_rule = rule.copy()
        if updated_rule['status'] == 'unmapped':
            updated_rule['status'] = 'translated'
            updated_rule['translated'] = updated_rule['original']
            updated_count += 1
        updated_rules.append(updated_rule)
    
    print(f"[OK] 已将 {updated_count} 条未映射内容标记为已翻译")
    
    if output_file:
        if save_yaml_mappings(updated_rules, output_file):
            print(f"[OK] 更新后的规则已保存到: {output_file}")
        else:
            print(f"[ERROR] 保存更新后的规则失败: {output_file}")
    
    return updated_rules
