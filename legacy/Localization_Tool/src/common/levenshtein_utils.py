#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Levenshtein模糊匹配工具

该模块包含字符串相似度计算和模糊匹配功能。
"""

import re
from typing import List, Dict, Any, Tuple

# 尝试导入Levenshtein库，如果不存在则使用自定义实现
HAS_LEVENSHTEIN = False

# 模块级初始化，确保只执行一次
try:
    import Levenshtein
    HAS_LEVENSHTEIN = True
    print("[OK] 使用python-Levenshtein库进行相似度计算")
except ImportError:
    HAS_LEVENSHTEIN = False
    print("[WARN] python-Levenshtein库未安装，将使用自定义实现")


class LevenshteinDistance:
    """
    Levenshtein距离计算器
    """
    
    @staticmethod
    def calculate(a: str, b: str) -> int:
        """
        计算两个字符串之间的Levenshtein距离
        
        Args:
            a: 第一个字符串
            b: 第二个字符串
        
        Returns:
            int: Levenshtein距离
        """
        if HAS_LEVENSHTEIN:
            return Levenshtein.distance(a, b)
        else:
            # 自定义Levenshtein距离实现
            m, n = len(a), len(b)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            
            for i in range(m + 1):
                dp[i][0] = i
            for j in range(n + 1):
                dp[0][j] = j
            
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    cost = 0 if a[i-1] == b[j-1] else 1
                    dp[i][j] = min(
                        dp[i-1][j] + 1,      # 删除
                        dp[i][j-1] + 1,      # 插入
                        dp[i-1][j-1] + cost  # 替换
                    )
            
            return dp[m][n]
    
    @staticmethod
    def ratio(a: str, b: str) -> float:
        """
        计算两个字符串之间的相似度比例(0到1之间)
        
        Args:
            a: 第一个字符串
            b: 第二个字符串
        
        Returns:
            float: 相似度比例
        """
        if HAS_LEVENSHTEIN:
            return Levenshtein.ratio(a, b)
        else:
            # 自定义相似度比例计算
            if not a and not b:
                return 1.0
            if not a or not b:
                return 0.0
            
            distance = LevenshteinDistance.calculate(a, b)
            max_length = max(len(a), len(b))
            return 1.0 - (distance / max_length)


def calculate_similarity(a: str, b: str, clean_placeholders: bool = True) -> float:
    """
    计算字符串相似度，支持去除占位符后比较
    
    Args:
        a: 第一个字符串
        b: 第二个字符串
        clean_placeholders: 是否去除占位符后比较
    
    Returns:
        float: 相似度比例(0到1之间)
    """
    if clean_placeholders:
        # 预处理：移除占位符后比较
        a_clean = re.sub(r'[%]\w+|\$\{.*?\}|\{.*?\}', '', a)
        b_clean = re.sub(r'[%]\w+|\$\{.*?\}|\{.*?\}', '', b)
        return LevenshteinDistance.ratio(a_clean, b_clean)
    else:
        return LevenshteinDistance.ratio(a, b)


def get_fuzzy_suggestions(query: str, localization_db: List[Dict[str, Any]], threshold: float = 0.8, clean_placeholders: bool = True) -> List[Dict[str, Any]]:
    """
    根据模糊匹配获取建议
    
    Args:
        query: 查询字符串
        localization_db: 本地化数据库
        threshold: 相似度阈值
        clean_placeholders: 是否去除占位符后比较
    
    Returns:
        List[Dict[str, Any]]: 模糊匹配建议列表，按相似度降序排序
    """
    suggestions = []
    
    for item in localization_db:
        similarity = calculate_similarity(query, item["original"], clean_placeholders)
        if similarity >= threshold:
            suggestions.append({
                "item": item,
                "similarity": similarity
            })
    
    # 按相似度降序排序
    suggestions.sort(key=lambda x: x["similarity"], reverse=True)
    
    return suggestions


def get_contextual_suggestions(yaml_item: Dict[str, Any], localization_db: List[Dict[str, Any]], max_suggestions: int = 5) -> List[Dict[str, Any]]:
    """
    根据上下文获取建议
    
    Args:
        yaml_item: YAML映射项
        localization_db: 本地化数据库
        max_suggestions: 最大建议数量
    
    Returns:
        List[Dict[str, Any]]: 上下文匹配建议列表
    """
    suggestions = []
    
    # 检查yaml_item是否包含上下文信息
    if "context" not in yaml_item:
        return suggestions
    
    yaml_context = yaml_item["context"]
    
    # 根据上下文过滤已有翻译
    if "parent_types" in yaml_context:
        for entry in localization_db:
            if "context" in entry and "parent_types" in entry["context"]:
                # 检查yaml_item的父节点类型是否是entry父节点类型的子集
                if set(yaml_context["parent_types"]).issubset(set(entry["context"]["parent_types"])):
                    suggestions.append(entry)
    
    # 根据节点类型进一步筛选
    if "node_type" in yaml_context:
        suggestions = [e for e in suggestions if 
                     "context" in e and "node_type" in e["context"] and 
                     e["context"]["node_type"] == yaml_context["node_type"]]
    
    # 返回前N个最相关建议
    return suggestions[:max_suggestions]


def get_combined_suggestions(yaml_item: Dict[str, Any], localization_db: List[Dict[str, Any]], threshold: float = 0.8, max_suggestions: int = 5) -> List[Dict[str, Any]]:
    """
    获取综合建议(上下文匹配 + 模糊匹配)
    
    Args:
        yaml_item: YAML映射项
        localization_db: 本地化数据库
        threshold: 模糊匹配阈值
        max_suggestions: 最大建议数量
    
    Returns:
        List[Dict[str, Any]]: 综合建议列表
    """
    # 获取上下文建议
    contextual_suggestions = get_contextual_suggestions(yaml_item, localization_db, max_suggestions)
    
    # 获取模糊匹配建议
    fuzzy_suggestions = get_fuzzy_suggestions(yaml_item["original"], localization_db, threshold)
    
    # 合并结果(优先显示上下文匹配)
    all_suggestions = []
    
    # 添加上下文建议
    for suggestion in contextual_suggestions:
        all_suggestions.append({
            "item": suggestion,
            "type": "contextual",
            "similarity": 1.0  # 上下文匹配的相似度设为1.0
        })
    
    # 添加模糊匹配建议，去除重复项
    seen_ids = {s["item"]["id"] for s in all_suggestions}
    for suggestion in fuzzy_suggestions:
        if suggestion["item"]["id"] not in seen_ids:
            all_suggestions.append({
                "item": suggestion["item"],
                "type": "fuzzy",
                "similarity": suggestion["similarity"]
            })
    
    # 按相似度降序排序
    all_suggestions.sort(key=lambda x: x["similarity"], reverse=True)
    
    # 去重并返回前N个建议
    unique_suggestions = []
    seen_ids = set()
    for suggestion in all_suggestions:
        if suggestion["item"]["id"] not in seen_ids:
            unique_suggestions.append(suggestion)
            seen_ids.add(suggestion["item"]["id"])
            if len(unique_suggestions) >= max_suggestions:
                break
    
    return unique_suggestions


def get_combined_score(context_match: float, similarity: float, context_weight: float = 0.7, similarity_weight: float = 0.3) -> float:
    """
    计算综合评分
    
    Args:
        context_match: 上下文匹配度(0到1之间)
        similarity: 相似度(0到1之间)
        context_weight: 上下文权重
        similarity_weight: 相似度权重
    
    Returns:
        float: 综合评分(0到1之间)
    """
    return (context_match * context_weight) + (similarity * similarity_weight)


def find_best_match(query: str, candidates: List[str], clean_placeholders: bool = True) -> Tuple[str, float]:
    """
    找到与查询字符串最匹配的候选字符串
    
    Args:
        query: 查询字符串
        candidates: 候选字符串列表
        clean_placeholders: 是否去除占位符后比较
    
    Returns:
        Tuple[str, float]: (最佳匹配字符串, 相似度)
    """
    best_match = None
    best_similarity = 0.0
    
    for candidate in candidates:
        similarity = calculate_similarity(query, candidate, clean_placeholders)
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = candidate
    
    return best_match, best_similarity
