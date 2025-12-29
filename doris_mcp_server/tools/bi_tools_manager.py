
"""
Apache Doris MCP Tools Manager
Responsible for tool registration, management, scheduling and routing, does not contain specific business logic implementation
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List

from mcp.types import Tool

from ..utils.db import DorisConnectionManager
from ..utils.query_executor import DorisQueryExecutor
from ..utils.monitoring_tools import DorisMonitoringTools
from ..utils.schema_extractor import MetadataExtractor
from ..utils.logger import get_logger

logger = get_logger(__name__)



class DorisToolsManager:
    """Apache Doris Tools Manager"""
    
    def __init__(self, connection_manager: DorisConnectionManager):
        self.connection_manager = connection_manager
        
        # Initialize business logic processors
        self.query_executor = DorisQueryExecutor(connection_manager)
        self.metadata_extractor = MetadataExtractor(connection_manager=connection_manager)
        self.monitoring_tools = DorisMonitoringTools(connection_manager)
 

    async def list_tools(self) -> List[Tool]:
        """List all available query tools (for stdio mode)"""
        # Get ADBC configuration defaults
        adbc_config = self.connection_manager.config.adbc
        
        tools = [
            Tool(
                name="exec_query",
                description="""[Function Description]: Execute SQL query and return result command with catalog federation support.

[Parameter Content]:

- sql (string) [Required] - SQL statement to execute. MUST use three-part naming for all table references: 'catalog_name.db_name.table_name'. For internal tables use 'internal.db_name.table_name', for external tables use 'catalog_name.db_name.table_name'

- db_name (string) [Optional] - Target database name, defaults to the current database

- catalog_name (string) [Optional] - Reference catalog name for context, defaults to current catalog

- max_rows (integer) [Optional] - Maximum number of rows to return, default 100

- timeout (integer) [Optional] - Query timeout in seconds, default 30
""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sql": {"type": "string", "description": "SQL statement to execute, must use three-part naming"},
                        "db_name": {"type": "string", "description": "Target database name"},
                        "catalog_name": {"type": "string", "description": "Catalog name"},
                        "max_rows": {"type": "integer", "description": "Maximum number of rows to return", "default": 100},
                        "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30},
                    },
                    "required": ["sql"],
                },
            ),
            Tool(
                name="get_table_schema",
                description="""[Function Description]: Get detailed structure information of the specified table (columns, types, comments, etc.).

[Parameter Content]:

- table_name (string) [Required] - Name of the table to query

- db_name (string) [Optional] - Target database name, defaults to the current database

- catalog_name (string) [Optional] - Target catalog name for federation queries, defaults to current catalog
""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Table name"},
                        "db_name": {"type": "string", "description": "Database name"},
                        "catalog_name": {"type": "string", "description": "Catalog name"},
                    },
                    "required": ["table_name"],
                },
            ),
            Tool(
                name="get_db_table_list",
                description="""[Function Description]: Get a list of all table names in the specified database.

[Parameter Content]:

- db_name (string) [Optional] - Target database name, defaults to the current database

- catalog_name (string) [Optional] - Target catalog name for federation queries, defaults to current catalog
""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "db_name": {"type": "string", "description": "Database name"},
                        "catalog_name": {"type": "string", "description": "Catalog name"},
                    },
                },
            ),
            Tool(
                name="get_db_list",
                description="""[Function Description]: Get a list of all database names on the server.

[Parameter Content]:

- catalog_name (string) [Optional] - Target catalog name for federation queries, defaults to current catalog
""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "catalog_name": {"type": "string", "description": "Catalog name"},
                    },
                },
            ),
            Tool(
                name="get_table_comment",
                description="""[Function Description]: Get the comment information for the specified table.

[Parameter Content]:

- table_name (string) [Required] - Name of the table to query

- db_name (string) [Optional] - Target database name, defaults to the current database

- catalog_name (string) [Optional] - Target catalog name for federation queries, defaults to current catalog
""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Table name"},
                        "db_name": {"type": "string", "description": "Database name"},
                        "catalog_name": {"type": "string", "description": "Catalog name"},
                    },
                    "required": ["table_name"],
                },
            ),
        ]
        
        return tools
        
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """
        Call the specified query tool (tool routing and scheduling center)
        """
        try:
            start_time = time.time()
            
            # Tool routing - dispatch requests to corresponding business logic processors
            if name == "exec_query":
                result = await self._exec_query_tool(arguments)
            elif name == "get_table_schema":
                result = await self._get_table_schema_tool(arguments)
            elif name == "get_db_table_list":
                result = await self._get_db_table_list_tool(arguments)
            elif name == "get_db_list":
                result = await self._get_db_list_tool(arguments)
            elif name == "get_table_comment":
                result = await self._get_table_comment_tool(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            execution_time = time.time() - start_time
            
            # Add execution information
            if isinstance(result, dict):
                result["_execution_info"] = {
                    "tool_name": name,
                    "execution_time": round(execution_time, 3),
                    "timestamp": datetime.now().isoformat(),
                }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Tool call failed {name}: {str(e)}")
            error_result = {
                "error": str(e),
                "tool_name": name,
                "arguments": arguments,
                "timestamp": datetime.now().isoformat(),
            }
            return json.dumps(error_result, ensure_ascii=False, indent=2)
    
    
    async def _exec_query_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """SQL query execution tool routing (supports federation queries)"""
        sql = arguments.get("sql")
        db_name = arguments.get("db_name")
        catalog_name = arguments.get("catalog_name")
        max_rows = arguments.get("max_rows", 100)
        timeout = arguments.get("timeout", 30)
        
        # Delegate to metadata extractor for processing
        return await self.metadata_extractor.exec_query_for_mcp(
            sql, db_name, catalog_name, max_rows, timeout
        )
    
    async def _get_table_schema_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get table schema tool routing"""
        table_name = arguments.get("table_name")
        db_name = arguments.get("db_name")
        catalog_name = arguments.get("catalog_name")
        
        # Delegate to metadata extractor for processing
        return await self.metadata_extractor.get_table_schema_for_mcp(
            table_name, db_name, catalog_name
        )
    
    async def _get_db_table_list_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get database table list tool routing"""
        db_name = arguments.get("db_name")
        catalog_name = arguments.get("catalog_name")
        
        # Delegate to metadata extractor for processing
        return await self.metadata_extractor.get_db_table_list_for_mcp(db_name, catalog_name)
    
    async def _get_db_list_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get database list tool routing"""
        catalog_name = arguments.get("catalog_name")
        
        # Delegate to metadata extractor for processing
        return await self.metadata_extractor.get_db_list_for_mcp(catalog_name)
    
    async def _get_table_comment_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get table comment tool routing"""
        table_name = arguments.get("table_name")
        db_name = arguments.get("db_name")
        catalog_name = arguments.get("catalog_name")
        
        # Delegate to metadata extractor for processing
        return await self.metadata_extractor.get_table_comment_for_mcp(
            table_name, db_name, catalog_name
        )
    