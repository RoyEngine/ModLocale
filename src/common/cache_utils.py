# -*- coding: utf-8 -*-
"""
缓存管理工具模块

该模块提供了文件哈希计算、缓存数据管理和增量更新支持功能，用于优化ModLocale的性能。
"""

import os
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime


class FileCacheManager:
    """
    文件缓存管理器，用于跟踪文件变更和管理缓存数据
    """
    
    def __init__(self, cache_dir: str = ".cache"):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "file_cache.json")
        self.cache_data: Dict[str, Any] = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "files": {}
        }
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 加载现有缓存数据
        self._load_cache()
    
    def _load_cache(self) -> None:
        """
        加载现有缓存数据
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.cache_data = json.load(f)
                    # 确保缓存结构完整
                    if "files" not in self.cache_data:
                        self.cache_data["files"] = {}
            except (json.JSONDecodeError, IOError) as e:
                print(f"[WARN] 加载缓存失败: {e}，将使用新缓存")
    
    def _save_cache(self) -> None:
        """
        保存缓存数据到文件
        """
        self.cache_data["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[WARN] 保存缓存失败: {e}")
    
    def calculate_file_hash(self, file_path: str) -> Optional[str]:
        """
        计算文件的SHA-256哈希值
        
        Args:
            file_path: 文件路径
        
        Returns:
            Optional[str]: 文件的SHA-256哈希值，如果文件不存在或无法读取则返回None
        """
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, "rb") as f:
                hasher = hashlib.sha256()
                while chunk := f.read(4096):
                    hasher.update(chunk)
                return hasher.hexdigest()
        except IOError as e:
            print(f"[WARN] 计算文件哈希失败: {file_path} - {e}")
            return None
    
    def is_file_changed(self, file_path: str) -> bool:
        """
        检查文件是否已变更
        
        Args:
            file_path: 文件路径
        
        Returns:
            bool: True表示文件已变更，False表示文件未变更
        """
        current_hash = self.calculate_file_hash(file_path)
        if current_hash is None:
            return True
        
        file_key = os.path.abspath(file_path)
        cached_hash = self.cache_data["files"].get(file_key, {}).get("hash")
        
        return current_hash != cached_hash
    
    def update_file_cache(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        更新文件缓存信息
        
        Args:
            file_path: 文件路径
            metadata: 额外的元数据信息
        """
        current_hash = self.calculate_file_hash(file_path)
        if current_hash is None:
            return
        
        file_key = os.path.abspath(file_path)
        self.cache_data["files"][file_key] = {
            "hash": current_hash,
            "last_modified": os.path.getmtime(file_path),
            "size": os.path.getsize(file_path),
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        # 保存缓存
        self._save_cache()
    
    def get_changed_files(self, file_paths: list[str]) -> list[str]:
        """
        获取已变更的文件列表
        
        Args:
            file_paths: 文件路径列表
        
        Returns:
            list[str]: 已变更的文件路径列表
        """
        changed_files = []
        for file_path in file_paths:
            if self.is_file_changed(file_path):
                changed_files.append(file_path)
        return changed_files
    
    def clear_cache(self) -> None:
        """
        清空所有缓存数据
        """
        self.cache_data["files"] = {}
        self._save_cache()
    
    def remove_file_cache(self, file_path: str) -> None:
        """
        移除单个文件的缓存记录
        
        Args:
            file_path: 文件路径
        """
        file_key = os.path.abspath(file_path)
        if file_key in self.cache_data["files"]:
            del self.cache_data["files"][file_key]
            self._save_cache()
    
    def get_cached_files(self) -> Dict[str, Any]:
        """
        获取所有缓存的文件信息
        
        Returns:
            Dict[str, Any]: 缓存的文件信息字典
        """
        return self.cache_data["files"]
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict[str, Any]: 缓存统计信息
        """
        files = self.cache_data["files"]
        total_size = sum(info.get("size", 0) for info in files.values())
        
        return {
            "total_files": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "last_updated": self.cache_data["last_updated"],
            "cache_version": self.cache_data["version"]
        }


def get_cached_files(root_dir: str, extensions: list[str]) -> list[str]:
    """
    获取指定目录下所有符合扩展名要求的文件路径列表
    
    Args:
        root_dir: 根目录路径
        extensions: 文件扩展名列表
    
    Returns:
        list[str]: 文件路径列表
    """
    file_paths = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_paths.append(os.path.join(root, file))
    return file_paths


def create_cache_directory(cache_dir: str = ".cache") -> None:
    """
    创建缓存目录
    
    Args:
        cache_dir: 缓存目录路径
    """
    os.makedirs(cache_dir, exist_ok=True)
