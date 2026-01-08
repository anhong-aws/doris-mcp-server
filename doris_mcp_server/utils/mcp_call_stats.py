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
MCP Call Statistics Manager
Tracks and manages daily call counts for MCP methods.
"""

import threading
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional


class MCPCallStats:
    """Thread-safe MCP call statistics manager.
    
    This class tracks daily call counts for MCP methods and automatically
    cleans up statistics older than 3 months.
    """
    
    # Class variables
    _call_stats: Dict[str, Dict[str, int]] = {}  # {"2024-01-08": {"method1": 10, "method2": 20}}
    _lock: threading.RLock = threading.RLock()  # Thread-safe lock
    _stats_loaded: bool = False  # Flag to track if stats have been loaded from file
    _STATS_FILE_PATH: str = "logs/mcp_call_stats.json"  # Path to save stats file
    
    @classmethod
    def increment_call_count(cls, method_name: str) -> None:
        """Increment call count for a specific method.
        
        Args:
            method_name: Name of the method to increment count for.
        """
        cls._ensure_stats_loaded()
        with cls._lock:
            # Get current date in YYYY-MM-DD format
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Initialize today's stats if not exists
            if today not in cls._call_stats:
                cls._call_stats[today] = {}
            
            # Increment method count
            if method_name not in cls._call_stats[today]:
                cls._call_stats[today][method_name] = 0
            cls._call_stats[today][method_name] += 1
            
            # Clean up old stats
            cls.cleanup_old_stats()
    
    @classmethod
    def get_daily_stats(cls, date_str: str) -> Dict[str, int]:
        """Get call statistics for a specific date.
        
        Args:
            date_str: Date in YYYY-MM-DD format.
            
        Returns:
            Dict with method names as keys and call counts as values.
        """
        cls._ensure_stats_loaded()
        with cls._lock:
            return cls._call_stats.get(date_str, {})
    
    @classmethod
    def get_total_stats(cls) -> Dict[str, Dict[str, int]]:
        """Get all call statistics.
        
        Returns:
            Dict with dates as keys and method call counts as values.
        """
        cls._ensure_stats_loaded()
        with cls._lock:
            # Return a deep copy to prevent external modification
            return {date: methods.copy() for date, methods in cls._call_stats.items()}
    
    @classmethod
    def cleanup_old_stats(cls) -> None:
        """Clean up statistics older than 3 months.
        
        This method removes all statistics that are more than 3 months old
        from the current date.
        """
        with cls._lock:
            # Calculate cutoff date (3 months ago from today)
            cutoff_date = datetime.now() - timedelta(days=90)
            cutoff_str = cutoff_date.strftime('%Y-%m-%d')
            
            # Remove dates older than cutoff
            dates_to_remove = [date for date in cls._call_stats if date < cutoff_str]
            for date in dates_to_remove:
                del cls._call_stats[date]
    
    @classmethod
    def get_daily_total(cls, date_str: str) -> int:
        """Get total call count for a specific date.
        
        Args:
            date_str: Date in YYYY-MM-DD format.
            
        Returns:
            Total call count for the date.
        """
        cls._ensure_stats_loaded()
        with cls._lock:
            daily_stats = cls._call_stats.get(date_str, {})
            return sum(daily_stats.values())
    
    @classmethod
    def get_method_total(cls, method_name: str) -> int:
        """Get total call count for a specific method across all dates.
        
        Args:
            method_name: Name of the method.
            
        Returns:
            Total call count for the method.
        """
        cls._ensure_stats_loaded()
        with cls._lock:
            total = 0
            for daily_stats in cls._call_stats.values():
                total += daily_stats.get(method_name, 0)
            return total
    
    @classmethod
    def _ensure_stats_loaded(cls) -> None:
        """Ensure that stats have been loaded from file if not already loaded.
        This method is called internally by other methods to ensure stats are available.
        """
        if not cls._stats_loaded:
            cls.load_stats()
    
    @classmethod
    def load_stats(cls) -> None:
        """Load call statistics from file.
        
        This method reads call statistics from the specified file and updates
        the in-memory call stats dictionary.
        """
        with cls._lock:
            try:
                # Check if the stats file exists
                if os.path.exists(cls._STATS_FILE_PATH):
                    with open(cls._STATS_FILE_PATH, 'r') as f:
                        loaded_stats = json.load(f)
                        # Update call stats with loaded data
                        cls._call_stats.update(loaded_stats)
                    # Clean up old stats after loading
                    cls.cleanup_old_stats()
            except Exception as e:
                # Log the error if possible, but don't fail the application
                try:
                    from .logger import get_logger
                    logger = get_logger(__name__)
                    logger.warning(f"Failed to load MCP call stats from file: {e}")
                except:
                    pass  # Ignore if logger is not available
            finally:
                cls._stats_loaded = True
    
    @classmethod
    def save_stats(cls) -> None:
        """Save call statistics to file.
        
        This method writes the current call statistics to the specified file.
        """
        with cls._lock:
            try:
                # Ensure the logs directory exists
                os.makedirs(os.path.dirname(cls._STATS_FILE_PATH), exist_ok=True)
                
                # Write stats to file
                with open(cls._STATS_FILE_PATH, 'w') as f:
                    json.dump(cls._call_stats, f, indent=2)
            except Exception as e:
                # Log the error if possible, but don't fail the application
                try:
                    from .logger import get_logger
                    logger = get_logger(__name__)
                    logger.warning(f"Failed to save MCP call stats to file: {e}")
                except:
                    pass  # Ignore if logger is not available
