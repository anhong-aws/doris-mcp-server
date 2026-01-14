import fnmatch
from typing import List, Dict, Any


class FilterManager:
    """
    Manages table and column filtering based on configuration
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize filter manager with configuration
        
        Args:
            config: Dictionary containing filter configurations
        """
        # Parse table include filters
        self.table_include_patterns = self._parse_list_config(
            config.get('TABLE_FILTER_INCLUDE', '')
        )
        
        # Parse table exclude filters
        self.table_exclude_names = self._parse_list_config(
            config.get('TABLE_FILTER_EXCLUDE', '')
        )
        
        # Parse column exclude filters
        self.column_exclude_map = self._parse_column_filters(
            config.get('COLUMN_FILTER_EXCLUDE', '')
        )
    
    def _parse_list_config(self, config_value: str) -> List[str]:
        """
        Parse a comma-separated configuration value into a list
        
        Args:
            config_value: Comma-separated string
            
        Returns:
            List of trimmed strings
        """
        if not config_value:
            return []
        return [item.strip() for item in config_value.split(',') if item.strip()]
    
    def _parse_column_filters(self, config_value: str) -> Dict[str, List[str]]:
        """
        Parse column filter configuration
        
        Format: table1:col1,col2;table2:col3,col4
        
        Args:
            config_value: String containing column filters
            
        Returns:
            Dictionary mapping table names to list of excluded columns
        """
        column_map = {}
        
        if not config_value:
            return column_map
        
        # Split by semicolon to get table:columns pairs
        table_pairs = [item.strip() for item in config_value.split(';') if item.strip()]
        
        for table_pair in table_pairs:
            if ':' in table_pair:
                table_name, columns_str = table_pair.split(':', 1)
                table_name = table_name.strip()
                columns = [col.strip() for col in columns_str.split(',') if col.strip()]
                if table_name and columns:
                    column_map[table_name] = columns
        
        return column_map
    
    def is_table_allowed(self, table_name: str) -> bool:
        """
        Check if a table is allowed based on include/exclude filters
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table is allowed, False otherwise
        """
        # First check exclude list
        if table_name in self.table_exclude_names:
            return False
        
        # If no include patterns, allow all tables (except excluded ones)
        if not self.table_include_patterns:
            return True
        
        # Check if table matches any include pattern
        for pattern in self.table_include_patterns:
            if fnmatch.fnmatch(table_name, pattern):
                return True
        
        # Table doesn't match any include pattern
        return False
    
    def filter_columns(self, table_name: str, columns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter columns based on column filters
        
        Args:
            table_name: Name of the table
            columns: List of column dictionaries
            
        Returns:
            List of allowed columns
        """
        # Get excluded columns for this table
        excluded_columns = self.column_exclude_map.get(table_name, [])
        
        if not excluded_columns:
            return columns
        
        # Filter out excluded columns
        return [
            column for column in columns 
            if column.get('column_name', '') not in excluded_columns
        ]
