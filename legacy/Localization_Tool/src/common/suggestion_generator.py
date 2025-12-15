#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能建议生成器

该模块包含基于上下文和相似度的智能建议生成功能。
"""

import os
import json
from typing import List, Dict, Any, Optional
from src.common.tree_sitter_utils import extract_ast_mappings, extract_strings_from_file
from src.common.yaml_utils import load_yaml_mappings, save_yaml_mappings, generate_initial_yaml_mappings
from src.common.levenshtein_utils import (
    get_contextual_suggestions,
    get_fuzzy_suggestions,
    get_combined_suggestions,
    calculate_similarity
)


class SuggestionGenerator:
    """
    智能建议生成器类
    """
    
    def __init__(self, localization_db: Optional[List[Dict[str, Any]]] = None):
        """
        初始化建议生成器
        
        Args:
            localization_db: 本地化数据库，包含已有的翻译映射
        """
        self.localization_db = localization_db or []
    
    def load_localization_db(self, file_path: str) -> bool:
        """
        从文件加载本地化数据库
        
        Args:
            file_path: 本地化数据库文件路径，支持JSON和YAML格式
        
        Returns:
            bool: 是否加载成功
        """
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.localization_db = json.load(f)
            elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                from src.common.yaml_utils import load_yaml_mappings
                self.localization_db = load_yaml_mappings(file_path)
            else:
                print(f"[WARN]  不支持的文件格式: {file_path}")
                return False
            
            print(f"OK 成功加载本地化数据库，共 {len(self.localization_db)} 条记录")
            return True
        except Exception as e:
            print(f"[WARN]  加载本地化数据库失败: {file_path} - {e}")
            return False
    
    def save_localization_db(self, file_path: str) -> bool:
        """
        保存本地化数据库到文件
        
        Args:
            file_path: 文件路径，支持JSON和YAML格式
        
        Returns:
            bool: 是否保存成功
        """
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.localization_db, f, ensure_ascii=False, indent=2)
            elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                from src.common.yaml_utils import save_yaml_mappings
                return save_yaml_mappings(self.localization_db, file_path)
            else:
                print(f"[WARN]  不支持的文件格式: {file_path}")
                return False
            
            print(f"OK 成功保存本地化数据库到: {file_path}")
            return True
        except Exception as e:
            print(f"[WARN]  保存本地化数据库失败: {file_path} - {e}")
            return False
    
    def add_to_localization_db(self, mappings: List[Dict[str, Any]]) -> None:
        """
        向本地化数据库添加映射
        
        Args:
            mappings: 映射列表
        """
        # 创建现有映射ID集合
        existing_ids = {item["id"] for item in self.localization_db}
        
        # 添加新映射
        for mapping in mappings:
            if mapping["id"] not in existing_ids:
                self.localization_db.append(mapping)
                existing_ids.add(mapping["id"])
        
        print(f"OK 成功向本地化数据库添加 {len(mappings)} 条记录")
    
    def generate_suggestions(self, yaml_item: Dict[str, Any], threshold: float = 0.8, max_suggestions: int = 5) -> List[Dict[str, Any]]:
        """
        为指定YAML映射项生成智能建议
        
        Args:
            yaml_item: YAML映射项
            threshold: 相似度阈值
            max_suggestions: 最大建议数量
        
        Returns:
            List[Dict[str, Any]]: 智能建议列表
        """
        return get_combined_suggestions(yaml_item, self.localization_db, threshold, max_suggestions)
    
    def generate_suggestions_for_file(self, file_path: str, threshold: float = 0.8, max_suggestions: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        为文件中的所有字符串生成智能建议
        
        Args:
            file_path: 文件路径
            threshold: 相似度阈值
            max_suggestions: 最大建议数量
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: 建议字典，键为字符串ID，值为建议列表
        """
        # 从文件提取字符串
        ast_mappings = extract_strings_from_file(file_path)
        
        # 生成初始YAML映射
        yaml_mappings = generate_initial_yaml_mappings(ast_mappings)
        
        # 为每个YAML映射项生成建议
        suggestions_dict = {}
        for yaml_item in yaml_mappings:
            suggestions = self.generate_suggestions(yaml_item, threshold, max_suggestions)
            suggestions_dict[yaml_item["id"]] = suggestions
        
        return suggestions_dict
    
    def generate_suggestions_for_directory(self, root_dir: str, threshold: float = 0.8, max_suggestions: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        为目录中的所有字符串生成智能建议
        
        Args:
            root_dir: 目录路径
            threshold: 相似度阈值
            max_suggestions: 最大建议数量
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: 建议字典，键为字符串ID，值为建议列表
        """
        # 从目录提取字符串
        ast_mappings = extract_ast_mappings(root_dir)
        
        # 生成初始YAML映射
        yaml_mappings = generate_initial_yaml_mappings(ast_mappings)
        
        # 为每个YAML映射项生成建议
        suggestions_dict = {}
        for yaml_item in yaml_mappings:
            suggestions = self.generate_suggestions(yaml_item, threshold, max_suggestions)
            suggestions_dict[yaml_item["id"]] = suggestions
        
        return suggestions_dict
    
    def update_mapping_with_suggestion(self, yaml_item: Dict[str, Any], suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用建议更新YAML映射项
        
        Args:
            yaml_item: 原始YAML映射项
            suggestion: 建议映射项
        
        Returns:
            Dict[str, Any]: 更新后的YAML映射项
        """
        updated_item = yaml_item.copy()
        if "translated" in suggestion:
            updated_item["translated"] = suggestion["translated"]
        if "status" in suggestion:
            updated_item["status"] = suggestion["status"]
        if "placeholders" in suggestion:
            updated_item["placeholders"] = suggestion["placeholders"]
        
        return updated_item
    
    def auto_complete_mappings(self, yaml_mappings: List[Dict[str, Any]], threshold: float = 0.9) -> List[Dict[str, Any]]:
        """
        自动补全YAML映射项，使用高相似度的建议
        
        Args:
            yaml_mappings: YAML映射列表
            threshold: 自动补全的相似度阈值
        
        Returns:
            List[Dict[str, Any]]: 自动补全后的YAML映射列表
        """
        updated_mappings = []
        auto_completed_count = 0
        
        for yaml_item in yaml_mappings:
            if yaml_item.get("status") != "untranslated":
                updated_mappings.append(yaml_item)
                continue
            
            suggestions = self.generate_suggestions(yaml_item, threshold, max_suggestions=1)
            if suggestions and suggestions[0]["similarity"] >= threshold:
                updated_item = self.update_mapping_with_suggestion(yaml_item, suggestions[0]["item"])
                updated_item["status"] = "needs_review"
                updated_mappings.append(updated_item)
                auto_completed_count += 1
            else:
                updated_mappings.append(yaml_item)
        
        print(f"OK 自动补全完成，共处理 {len(yaml_mappings)} 项，自动补全 {auto_completed_count} 项")
        return updated_mappings
    
    def get_similarity_stats(self, yaml_mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取相似度统计信息
        
        Args:
            yaml_mappings: YAML映射列表
        
        Returns:
            Dict[str, Any]: 相似度统计信息
        """
        stats = {
            "total_items": len(yaml_mappings),
            "with_suggestions": 0,
            "avg_similarity": 0.0,
            "similarity_distribution": {
                "high": 0,    # >= 0.9
                "medium": 0,  # >= 0.7 < 0.9
                "low": 0,     # >= 0.5 < 0.7
                "very_low": 0 # < 0.5
            }
        }
        
        total_similarity = 0.0
        for yaml_item in yaml_mappings:
            suggestions = self.generate_suggestions(yaml_item, threshold=0.5, max_suggestions=1)
            if suggestions:
                stats["with_suggestions"] += 1
                similarity = suggestions[0]["similarity"]
                total_similarity += similarity
                
                if similarity >= 0.9:
                    stats["similarity_distribution"]["high"] += 1
                elif similarity >= 0.7:
                    stats["similarity_distribution"]["medium"] += 1
                elif similarity >= 0.5:
                    stats["similarity_distribution"]["low"] += 1
                else:
                    stats["similarity_distribution"]["very_low"] += 1
        
        if stats["with_suggestions"] > 0:
            stats["avg_similarity"] = total_similarity / stats["with_suggestions"]
        
        return stats


def generate_suggestions_for_yaml_file(yaml_file: str, localization_db: List[Dict[str, Any]], output_file: str, threshold: float = 0.8, max_suggestions: int = 5) -> bool:
    """
    为YAML文件中的所有映射项生成智能建议
    
    Args:
        yaml_file: 输入YAML文件路径
        localization_db: 本地化数据库
        output_file: 输出文件路径
        threshold: 相似度阈值
        max_suggestions: 最大建议数量
    
    Returns:
        bool: 是否生成成功
    """
    # 加载YAML文件
    from src.common.yaml_utils import load_yaml_mappings, save_yaml_mappings
    yaml_mappings = load_yaml_mappings(yaml_file)
    
    if not yaml_mappings:
        print(f"[WARN]  未从文件 {yaml_file} 加载到任何映射项")
        return False
    
    # 创建建议生成器
    generator = SuggestionGenerator(localization_db)
    
    # 为每个YAML映射项生成建议
    suggestions_dict = {}
    for yaml_item in yaml_mappings:
        suggestions = generator.generate_suggestions(yaml_item, threshold, max_suggestions)
        suggestions_dict[yaml_item["id"]] = suggestions
    
    # 保存建议到文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(suggestions_dict, f, ensure_ascii=False, indent=2)
        
        print(f"OK 成功生成建议并保存到: {output_file}")
        return True
    except Exception as e:
        print(f"[ERROR] 保存建议失败: {output_file} - {e}")
        return False


def create_localization_db_from_directory(root_dir: str, output_file: str) -> bool:
    """
    从目录创建本地化数据库
    
    Args:
        root_dir: 源代码目录
        output_file: 输出文件路径
    
    Returns:
        bool: 是否创建成功
    """
    # 提取AST映射
    from src.common.tree_sitter_utils import extract_ast_mappings
    ast_mappings = extract_ast_mappings(root_dir)
    
    if not ast_mappings:
        print(f"[WARN]  未从目录 {root_dir} 提取到任何字符串")
        return False
    
    # 生成初始YAML映射
    from src.common.yaml_utils import generate_initial_yaml_mappings, save_yaml_mappings
    yaml_mappings = generate_initial_yaml_mappings(ast_mappings)
    
    # 保存到文件
    return save_yaml_mappings(yaml_mappings, output_file)
