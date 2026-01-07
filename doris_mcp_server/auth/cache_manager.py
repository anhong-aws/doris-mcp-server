#!/usr/bin/env python3
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
Apache Doris Cache Management Module

Provides core cache management functionality including cache inspection,
clearing, statistics, and optimization recommendations.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


class DorisCacheManager:
    """Apache Doris缓存管理器"""
    
    def __init__(self, metadata_extractor):
        """
        初始化缓存管理器
        
        Args:
            metadata_extractor: MetadataExtractor实例，用于访问其缓存系统
        """
        self.metadata_extractor = metadata_extractor
        
    def get_cache_details(self, include_values: bool = False) -> Dict[str, Any]:
        """
        获取缓存详情
        
        Args:
            include_values: 是否包含缓存值（可能很大），默认False
            
        Returns:
            包含缓存详情的字典
        """
        try:
            cache_details = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "cache_summary": {},
                "cache_entries": []
            }
            
            if not hasattr(self.metadata_extractor, 'metadata_cache'):
                cache_details["success"] = False
                cache_details["error"] = "No cache system found in metadata extractor"
                return cache_details
            
            cache = self.metadata_extractor.metadata_cache
            cache_time = self.metadata_extractor.metadata_cache_time
            cache_ttl = getattr(self.metadata_extractor, 'cache_ttl', 3600)
            
            now = time.time()
            
            total_entries = len(cache)
            expired_entries = 0
            valid_entries = 0
            
            cache_types = {}
            for key in cache.keys():
                if ':' in key:
                    cache_type = key.split(':')[0]
                    cache_types[cache_type] = cache_types.get(cache_type, 0) + 1
                else:
                    cache_types['other'] = cache_types.get('other', 0) + 1
            
            cache_details["cache_summary"] = {
                "total_entries": total_entries,
                "cache_ttl_seconds": cache_ttl,
                "cache_types": cache_types,
                "generated_at": datetime.now().isoformat()
            }
            
            for key, value in cache.items():
                cache_time_val = cache_time.get(key, 0)
                age_seconds = now - cache_time_val
                is_expired = age_seconds >= cache_ttl
                
                if is_expired:
                    expired_entries += 1
                else:
                    valid_entries += 1
                
                entry = {
                    "key": key,
                    "age_seconds": round(age_seconds, 2),
                    "age_human": str(timedelta(seconds=int(age_seconds))),
                    "created_at": datetime.fromtimestamp(cache_time_val).isoformat() if cache_time_val > 0 else None,
                    "is_expired": is_expired,
                    "cache_type": key.split(':')[0] if ':' in key else 'other',
                    "value_size": len(str(value)) if value is not None else 0,
                    "value_type": type(value).__name__,
                    "hits": getattr(self.metadata_extractor, 'metadata_cache_hits', {}).get(key, 0)
                }
                
                if include_values and entry["value_size"] < 10240:
                    try:
                        if isinstance(value, (list, dict)):
                            entry["value_preview"] = json.dumps(value, ensure_ascii=False, indent=2)[:1000] + "..." if len(str(value)) > 1000 else json.dumps(value, ensure_ascii=False, indent=2)
                        else:
                            entry["value_preview"] = str(value)[:1000] + "..." if len(str(value)) > 1000 else str(value)
                    except Exception:
                        entry["value_preview"] = f"<{type(value).__name__} object>"
                elif include_values:
                    entry["value_preview"] = f"<Large {entry['value_type']} object - {entry['value_size']} bytes>"
                
                cache_details["cache_entries"].append(entry)
            
            cache_details["statistics"] = {
                "valid_entries": valid_entries,
                "expired_entries": expired_entries,
                "cache_efficiency": f"{(valid_entries / max(total_entries, 1)) * 100:.1f}%",
                "oldest_entry_age": max([entry["age_seconds"] for entry in cache_details["cache_entries"]]) if cache_details["cache_entries"] else 0,
                "newest_entry_age": min([entry["age_seconds"] for entry in cache_details["cache_entries"]]) if cache_details["cache_entries"] else 0
            }
            
            cache_details["cache_entries"].sort(key=lambda x: x["age_seconds"], reverse=True)
            
            return cache_details
            
        except Exception as e:
            logger.error(f"Failed to get cache details: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _remove_cache_entry(self, cache_key: str) -> None:
        """Remove a cache entry from all cache dictionaries."""
        cache = self.metadata_extractor.metadata_cache
        cache_time = self.metadata_extractor.metadata_cache_time
        cache_hits = getattr(self.metadata_extractor, 'metadata_cache_hits', {})
        
        cache.pop(cache_key, None)
        cache_time.pop(cache_key, None)
        cache_hits.pop(cache_key, None)
    
    def get_cache_entry(self, key: str, include_value: bool = True) -> Dict[str, Any]:
        """
        获取单个缓存条目的详情
        
        Args:
            key: 缓存键
            include_value: 是否包含缓存值，默认True
            
        Returns:
            缓存条目详情
        """
        try:
            if not hasattr(self.metadata_extractor, 'metadata_cache'):
                return {
                    "success": False,
                    "error": "No cache system found in metadata extractor"
                }
            
            cache = self.metadata_extractor.metadata_cache
            cache_time = self.metadata_extractor.metadata_cache_time
            cache_ttl = getattr(self.metadata_extractor, 'cache_ttl', 3600)
            
            if key not in cache:
                return {
                    "success": False,
                    "error": f"Cache key not found: {key}"
                }
            
            value = cache[key]
            cache_time_val = cache_time.get(key, 0)
            now = time.time()
            age_seconds = now - cache_time_val
            is_expired = age_seconds >= cache_ttl
            
            entry = {
                "success": True,
                "key": key,
                "age_seconds": round(age_seconds, 2),
                "age_human": str(timedelta(seconds=int(age_seconds))),
                "created_at": datetime.fromtimestamp(cache_time_val).isoformat() if cache_time_val > 0 else None,
                "is_expired": is_expired,
                "cache_type": key.split(':')[0] if ':' in key else 'other',
                "value_size": len(str(value)) if value is not None else 0,
                "value_type": type(value).__name__,
                "hits": getattr(self.metadata_extractor, 'metadata_cache_hits', {}).get(key, 0)
            }
            
            if include_value:
                try:
                    if isinstance(value, (list, dict)):
                        entry["value"] = json.dumps(value, ensure_ascii=False, indent=2)
                    else:
                        entry["value"] = str(value)
                except Exception:
                    entry["value"] = f"<{type(value).__name__} object>"
            
            return entry
            
        except Exception as e:
            logger.error(f"Failed to get cache entry {key}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def clear_cache(self, cache_type: Optional[str] = None, specific_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        清除缓存
        
        Args:
            cache_type: 要清除的缓存类型 ('all', 'table_schema', 'database_tables', None)
            specific_keys: 要清除的特定缓存键列表
            
        Returns:
            操作结果字典
        """
        try:
            if not hasattr(self.metadata_extractor, 'metadata_cache'):
                return {
                    "success": False,
                    "error": "No cache system found in metadata extractor"
                }
            
            cache = self.metadata_extractor.metadata_cache
            cache_time = self.metadata_extractor.metadata_cache_time
            cache_hits = getattr(self.metadata_extractor, 'metadata_cache_hits', {})
            
            cleared_entries = []
            
            if specific_keys:
                for key in specific_keys:
                    if key in cache:
                        cleared_entries.append(key)
                        self._remove_cache_entry(key)
                        
            elif cache_type == "all":
                cleared_entries = list(cache.keys())
                cache.clear()
                cache_time.clear()
                cache_hits.clear()
                
            elif cache_type == "table_schema":
                for key in list(cache.keys()):
                    if key.startswith("table_schema:"):
                        cleared_entries.append(key)
                        self._remove_cache_entry(key)
                            
            elif cache_type == "database_tables":
                for key in list(cache.keys()):
                    if key.startswith("database_tables:"):
                        cleared_entries.append(key)
                        self._remove_cache_entry(key)
                            
            elif cache_type is None:
                now = time.time()
                cache_ttl = getattr(self.metadata_extractor, 'cache_ttl', 3600)
                
                for key, cache_time_val in list(cache_time.items()):
                    if now - cache_time_val >= cache_ttl:
                        cleared_entries.append(key)
                        self._remove_cache_entry(key)
            else:
                return {
                    "success": False,
                    "error": f"Invalid cache type: {cache_type}. Use 'all', 'table_schema', 'database_tables', or None for expired cache"
                }
            
            logger.info(f"Cleared {len(cleared_entries)} cache entries")
            
            return {
                "success": True,
                "message": f"Successfully cleared {len(cleared_entries)} cache entries",
                "cleared_entries": cleared_entries,
                "cleared_count": len(cleared_entries),
                "remaining_cache_size": len(cache),
                "operation": f"clear_{cache_type or 'expired'}_cache",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        try:
            cache_details = self.get_cache_details(include_values=False)
            
            if not cache_details["success"]:
                return cache_details
            
            stats = cache_details["statistics"]
            cache_summary = cache_details["cache_summary"]
            
            type_stats = {}
            for entry in cache_details["cache_entries"]:
                cache_type = entry["cache_type"]
                if cache_type not in type_stats:
                    type_stats[cache_type] = {
                        "count": 0,
                        "valid_count": 0,
                        "expired_count": 0,
                        "total_size": 0
                    }
                
                type_stats[cache_type]["count"] += 1
                type_stats[cache_type]["total_size"] += entry["value_size"]
                
                if entry["is_expired"]:
                    type_stats[cache_type]["expired_count"] += 1
                else:
                    type_stats[cache_type]["valid_count"] += 1
            
            total_size = sum(entry["value_size"] for entry in cache_details["cache_entries"])
            
            extended_stats = {
                "cache_performance": {
                    "hit_potential": stats["cache_efficiency"],
                    "memory_usage": {
                        "total_size_bytes": total_size,
                        "total_size_human": self._format_bytes(total_size),
                        "average_entry_size": total_size // max(len(cache_details["cache_entries"]), 1)
                    }
                },
                "cache_types": type_stats,
                "recommendations": self._generate_recommendations(cache_details["cache_entries"], cache_summary["cache_ttl_seconds"])
            }
            
            stats.update(extended_stats)
            return {
                "success": True,
                "statistics": stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def search_cache_keys(self, pattern: str) -> Dict[str, Any]:
        """
        搜索缓存键
        
        Args:
            pattern: 搜索模式（支持简单的字符串匹配）
            
        Returns:
            匹配的缓存键列表
        """
        try:
            if not hasattr(self.metadata_extractor, 'metadata_cache'):
                return {
                    "success": False,
                    "error": "No cache system found in metadata extractor"
                }
            
            cache = self.metadata_extractor.metadata_cache
            matched_keys = []
            
            pattern_lower = pattern.lower()
            for key in cache.keys():
                if pattern_lower in key.lower():
                    matched_keys.append(key)
            
            return {
                "success": True,
                "pattern": pattern,
                "matched_keys": matched_keys,
                "match_count": len(matched_keys),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to search cache keys: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _format_bytes(self, bytes_size: int) -> str:
        """格式化字节大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    def _generate_recommendations(self, cache_entries: List[Dict], cache_ttl: int) -> List[str]:
        """生成缓存优化建议"""
        recommendations = []
        
        if not cache_entries:
            recommendations.append("No cache entries found. Consider configuring cache TTL.")
            return recommendations
        
        expired_count = sum(1 for entry in cache_entries if entry["is_expired"])
        expired_ratio = expired_count / len(cache_entries)
        
        if expired_ratio > 0.8:
            recommendations.append(f"High expiration rate ({expired_ratio:.1%}). Consider increasing cache TTL from {cache_ttl} seconds.")
        elif expired_ratio < 0.1:
            recommendations.append(f"Low expiration rate ({expired_ratio:.1%}). Consider reducing cache TTL to free up memory.")
        
        total_size = sum(entry["value_size"] for entry in cache_entries)
        if total_size > 50 * 1024 * 1024:
            recommendations.append(f"Large cache size ({self._format_bytes(total_size)}). Consider implementing cache size limits.")
        
        large_entries = [entry for entry in cache_entries if entry["value_size"] > 1024 * 1024]
        if large_entries:
            recommendations.append(f"Found {len(large_entries)} large cache entries (>1MB). Consider optimizing these.")
        
        if not recommendations:
            recommendations.append("Cache performance looks good.")
        
        return recommendations
