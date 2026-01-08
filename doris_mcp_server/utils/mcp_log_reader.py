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
MCP Log Reader
Responsible for reading, parsing and analyzing MCP logs
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

from ..utils.logger import get_logger
from ..utils.mcp_call_stats import MCPCallStats


class MCPLogReader:
    """MCP Log Reader for reading, parsing and analyzing MCP logs"""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize MCP Log Reader
        
        Args:
            log_dir: Directory containing log files
        """
        self.logger = get_logger(__name__)
        self.log_dir = Path(log_dir)
        self.mcp_log_file = self.log_dir / "doris_mcp_server_mcp.log"
    
    def get_logs(self, 
                days: int = 7, 
                limit: int = 100, 
                method: Optional[str] = None, 
                search: Optional[str] = None) -> Dict[str, Any]:
        """Get MCP logs with filtering options
        
        Args:
            days: Number of days to look back
            limit: Maximum number of logs to return
            method: Filter by specific method name
            search: Search term in log messages
            
        Returns:
            Dict containing logs and metadata
        """
        try:
            if not self.mcp_log_file.exists():
                return {
                    "success": False,
                    "error": "MCP log file not found"
                }
            
            logs = []
            log_pattern = r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \[(\w+)\] (\w+) - (.*)$"
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Read log file
            with open(self.mcp_log_file, 'r', encoding='utf-8') as f:
                for line in reversed(list(f)):  # Read from end to start for efficiency
                    line = line.strip()
                    if not line:
                        continue
                    
                    match = re.match(log_pattern, line)
                    if match:
                        timestamp_str, level, logger_name, message = match.groups()
                        log_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                        
                        # Apply time filter
                        if log_time < cutoff_date:
                            continue
                        
                        # Parse message to get method info
                        method_info = self._parse_method_info(message)
                        log_method = method_info["method"]
                        
                        # Apply method filter
                        if method and log_method != method:
                            continue
                        
                        # Apply search filter
                        if search and search.lower() not in message.lower():
                            continue
                        
                        # Create log entry
                        log_entry = {
                            "timestamp": timestamp_str,
                            "level": level,
                            "logger": logger_name,
                            "message": message,
                            "method": log_method,
                            "arguments": method_info["arguments"],
                            "raw": line
                        }
                        
                        logs.append(log_entry)
                        
                        if len(logs) >= limit:
                            break
            
            # Reverse to get chronological order
            logs.reverse()
            
            return {
                "success": True,
                "logs": logs,
                "total": len(logs),
                "days": days,
                "limit": limit,
                "method": method,
                "search": search,
                "log_file": str(self.mcp_log_file)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting MCP logs: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_method_info(self, message: str) -> Dict[str, Any]:
        """Parse log message to extract method name and arguments
        
        Args:
            message: Log message
            
        Returns:
            Dict containing method name and arguments
        """
        # Match "Tool called: method_name, Arguments: {...}"
        method_pattern = r"Tool called: ([\w_]+), Arguments: ({.*?})$"
        match = re.search(method_pattern, message)
        
        if match:
            method = match.group(1)
            args_str = match.group(2)
            
            try:
                # Use eval to safely parse dictionary string
                args = eval(args_str)
            except:
                args = {}
            
            return {
                "method": method,
                "arguments": args
            }
        
        return {
            "method": "unknown",
            "arguments": {}
        }
    
    def get_call_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get MCP call statistics
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict containing call statistics
        """
        try:
            # Get all stats from MCPCallStats
            all_stats = MCPCallStats.get_total_stats()
            
            # Filter by days
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_stats = {}
            
            for date_str, method_stats in all_stats.items():
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    if date >= cutoff_date:
                        filtered_stats[date_str] = method_stats
                except ValueError:
                    continue
            
            # Calculate total calls per method
            method_totals = defaultdict(int)
            for date_stats in filtered_stats.values():
                for method, count in date_stats.items():
                    method_totals[method] += count
            
            # Sort methods by call count
            sorted_methods = dict(sorted(method_totals.items(), key=lambda x: x[1], reverse=True))
            
            return {
                "success": True,
                "daily_stats": filtered_stats,
                "method_totals": sorted_methods,
                "days": days
            }
            
        except Exception as e:
            self.logger.error(f"Error getting call statistics: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_daily_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get daily call statistics
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict containing daily call counts
        """
        try:
            all_stats = MCPCallStats.get_total_stats()
            
            # Filter by days
            cutoff_date = datetime.now() - timedelta(days=days)
            daily_counts = {}
            
            # Generate all dates in range
            current_date = datetime.now().date()
            for i in range(days):
                date = current_date - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                daily_counts[date_str] = 0
            
            # Fill in actual counts
            for date_str, method_stats in all_stats.items():
                if date_str in daily_counts:
                    total = sum(method_stats.values())
                    daily_counts[date_str] = total
            
            # Sort by date ascending
            sorted_daily_counts = dict(sorted(daily_counts.items()))
            
            return {
                "success": True,
                "daily_counts": sorted_daily_counts,
                "days": days
            }
            
        except Exception as e:
            self.logger.error(f"Error getting daily stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_log_file_info(self) -> Dict[str, Any]:
        """Get MCP log file information
        
        Returns:
            Dict containing file metadata
        """
        try:
            if not self.mcp_log_file.exists():
                return {
                    "success": False,
                    "error": "MCP log file not found"
                }
            
            file_stat = self.mcp_log_file.stat()
            
            return {
                "success": True,
                "file_path": str(self.mcp_log_file),
                "file_size": file_stat.st_size,
                "file_size_human": f"{file_stat.st_size / 1024:.2f} KB",
                "created_at": datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                "modified_at": datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting log file info: {e}")
            return {
                "success": False,
                "error": str(e)
            }