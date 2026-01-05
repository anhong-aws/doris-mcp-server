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
Metadata Extraction Tool

Responsible for extracting table structures, relationships, and other metadata from the database.
"""

import os
import json
import pandas as pd
import re
import uuid
import time
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Import unified logging configuration
from .logger import get_logger
from .sql_security_utils import (
    SQLSecurityError,
    validate_identifier,
    quote_identifier
)

# Configure logging
logger = get_logger(__name__)

METADATA_DB_NAME="information_schema"
INTERNAL_CATALOG_NAME="internal"

# Import local modules
from .db import DorisConnectionManager

class MetadataExtractor:
    """Apache Doris Metadata Extractor"""
    
    def __init__(self, db_name: str = None, catalog_name: str = None, connection_manager=None):
        """
        Initialize the metadata extractor
        
        Args:
            db_name: Default database name, uses the currently connected database if not specified
            catalog_name: Default catalog name for federation queries, uses the current catalog if not specified
            connection_manager: DorisConnectionManager instance for database operations
        """
        # Get configuration from environment variables
        self.db_name = db_name or os.getenv("DORIS_DATABASE", "")
        self.catalog_name = catalog_name or INTERNAL_CATALOG_NAME # Store catalog name for federation support
        self.metadata_db = METADATA_DB_NAME  # Use constant
        self.connection_manager = connection_manager
        
        # Caching system
        self.metadata_cache = {}
        self.metadata_cache_time = {}
        self.cache_ttl = int(os.getenv("METADATA_CACHE_TTL", "3600"))  # Default cache 1 hour
        
        # Refresh time
        self.last_refresh_time = None
        
        # Session ID for database queries
        self._session_id = f"metadata_extractor_{uuid.uuid4().hex[:8]}"
    
    def clear_cache(self, cache_type: str = "all") -> Dict[str, Any]:
        """
        Clear metadata cache
        
        Args:
            cache_type: Type of cache to clear ('all', 'table_schema', 'database_tables')
            
        Returns:
            Dictionary with operation result
        """
        try:
            cleared_keys = []
            
            if cache_type == "all":
                # Clear all cache
                cleared_keys = list(self.metadata_cache.keys())
                self.metadata_cache.clear()
                self.metadata_cache_time.clear()
            elif cache_type == "table_schema":
                # Clear only table schema cache
                for key in list(self.metadata_cache.keys()):
                    if key.startswith("table_schema:"):
                        cleared_keys.append(key)
                        del self.metadata_cache[key]
                        del self.metadata_cache_time[key]
            elif cache_type == "database_tables":
                # Clear only database tables cache
                for key in list(self.metadata_cache.keys()):
                    if key.startswith("database_tables:"):
                        cleared_keys.append(key)
                        del self.metadata_cache[key]
                        del self.metadata_cache_time[key]
            else:
                return {
                    "success": False,
                    "error": f"Invalid cache type: {cache_type}. Use 'all', 'table_schema', or 'database_tables'"
                }
            
            logger.info(f"Cleared {len(cleared_keys)} cache entries of type '{cache_type}'")
            
            return {
                "success": True,
                "message": f"Successfully cleared {len(cleared_keys)} cache entries",
                "cleared_entries": cleared_keys,
                "remaining_cache_size": len(self.metadata_cache)
            }
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to clear cache"
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            now = time.time()
            total_entries = len(self.metadata_cache)
            
            # Count entries by type
            table_schema_count = sum(1 for key in self.metadata_cache.keys() if key.startswith("table_schema:"))
            database_tables_count = sum(1 for key in self.metadata_cache.keys() if key.startswith("database_tables:"))
            
            # Calculate age of cache entries
            cache_ages = []
            expired_entries = 0
            
            for key, cache_time in self.metadata_cache_time.items():
                age = now - cache_time
                cache_ages.append(age)
                if age >= self.cache_ttl:
                    expired_entries += 1
            
            avg_age = sum(cache_ages) / len(cache_ages) if cache_ages else 0
            max_age = max(cache_ages) if cache_ages else 0
            
            return {
                "success": True,
                "cache_stats": {
                    "total_entries": total_entries,
                    "table_schema_entries": table_schema_count,
                    "database_tables_entries": database_tables_count,
                    "cache_ttl_seconds": self.cache_ttl,
                    "average_age_seconds": round(avg_age, 2),
                    "max_age_seconds": round(max_age, 2),
                    "expired_entries": expired_entries,
                    "valid_entries": total_entries - expired_entries,
                    "cache_hit_potential": f"{((total_entries - expired_entries) / max(total_entries, 1)) * 100:.1f}%"
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get cache statistics"
            }
    
    def refresh_cache_for_table(self, table_name: str, db_name: str = None) -> Dict[str, Any]:
        """
        Refresh cache for a specific table
        
        Args:
            table_name: Name of the table to refresh
            db_name: Database name (optional)
            
        Returns:
            Dictionary with operation result
        """
        try:
            effective_db = db_name or self.db_name
            
            # Generate cache key for table schema
            cache_key = f"table_schema:{effective_db}:{table_name}"
            
            if cache_key in self.metadata_cache:
                del self.metadata_cache[cache_key]
                del self.metadata_cache_time[cache_key]
                logger.info(f"Removed cache entry for table: {effective_db}.{table_name}")
                return {
                    "success": True,
                    "message": f"Cache refreshed for table: {effective_db}.{table_name}",
                    "table_name": table_name,
                    "db_name": effective_db
                }
            else:
                logger.info(f"No cache entry found for table: {effective_db}.{table_name}")
                return {
                    "success": True,
                    "message": f"No cache entry found for table: {effective_db}.{table_name}",
                    "table_name": table_name,
                    "db_name": effective_db
                }
                
        except Exception as e:
            logger.error(f"Failed to refresh cache for table {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to refresh cache for table: {table_name}"
            }
    
    def refresh_cache_for_database(self, db_name: str = None) -> Dict[str, Any]:
        """
        Refresh cache for all tables in a specific database
        
        Args:
            db_name: Database name (optional)
            
        Returns:
            Dictionary with operation result
        """
        try:
            effective_db = db_name or self.db_name
            
            # Remove database tables cache
            db_cache_key = f"database_tables:{effective_db}"
            removed_db_cache = False
            if db_cache_key in self.metadata_cache:
                del self.metadata_cache[db_cache_key]
                del self.metadata_cache_time[db_cache_key]
                removed_db_cache = True
            
            # Remove all table schema caches for this database
            removed_table_caches = []
            for key in list(self.metadata_cache.keys()):
                if key.startswith(f"table_schema:{effective_db}:"):
                    removed_table_caches.append(key)
                    del self.metadata_cache[key]
                    del self.metadata_cache_time[key]
            
            total_removed = len(removed_table_caches) + (1 if removed_db_cache else 0)
            
            logger.info(f"Removed {total_removed} cache entries for database: {effective_db}")
            
            return {
                "success": True,
                "message": f"Cache refreshed for database: {effective_db}",
                "db_name": effective_db,
                "removed_entries": {
                    "database_tables": 1 if removed_db_cache else 0,
                    "table_schemas": len(removed_table_caches),
                    "total": total_removed
                }
            }
                
        except Exception as e:
            logger.error(f"Failed to refresh cache for database {db_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to refresh cache for database: {db_name}"
            }
    

    # Removed sync _execute_query_with_catalog; use async variant instead

    async def _execute_query_with_catalog_async(self, query: str, db_name: str = None, catalog_name: str = None):
        """
        Async version of _execute_query_with_catalog to avoid cross-event-loop issues.

        When catalog_name is provided and the SQL targets information_schema, we rewrite
        the SQL to use three-part naming: `{catalog}.information_schema` and execute it
        via the same running event loop.
        """
        try:
            if catalog_name and 'information_schema' in query.lower():
                modified_query = query.replace('information_schema', f'{catalog_name}.information_schema')
                logger.info(f"Modified query for catalog {catalog_name}: {modified_query}")
                return await self._execute_query_async(modified_query, db_name)
            else:
                return await self._execute_query_async(query, db_name)
        except Exception as e:
            logger.error(f"Error executing async query with catalog: {str(e)}")
            raise

    async def _execute_query_async(self, query: str, db_name: str = None, return_dataframe: bool = False):
        """
        Execute database query asynchronously
        
        Args:
            query: SQL query to execute
            db_name: Database name to use (optional)
            return_dataframe: Whether to return a pandas DataFrame instead of list
            
        Returns:
            Query result data (list of dictionaries or pandas DataFrame)
        """
        try:
            if self.connection_manager:
                # Use the injected connection manager directly (async)
                result = await self.connection_manager.execute_query(self._session_id, query, None)
                
                # Extract data from QueryResult
                if hasattr(result, 'data'):
                    data = result.data
                else:
                    data = result
                
                # Convert to DataFrame if requested
                if return_dataframe and data:
                    import pandas as pd
                    return pd.DataFrame(data)
                elif return_dataframe:
                    import pandas as pd
                    return pd.DataFrame()
                else:
                    return data
            else:
                # Fallback: Return empty result
                logger.warning("No connection manager provided, returning empty result")
                if return_dataframe:
                    import pandas as pd
                    return pd.DataFrame()
                else:
                    return []
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            # Return empty result instead of raising exception to prevent cascade failures
            if return_dataframe:
                import pandas as pd
                return pd.DataFrame()
            else:
                return []

    # Removed sync _execute_query; use async methods exclusively

    async def get_bi_table_schema_async(self, table_name: str, db_name: str = None) -> List[Dict[str, Any]]:
        """Asynchronously get table schema information with caching"""
        try:
            # Use async query method
            effective_db = db_name or self.db_name
            
            # SECURITY FIX: Validate identifiers
            try:
                validate_identifier(table_name, "table name")
                if effective_db:
                    validate_identifier(effective_db, "database name")
            except SQLSecurityError as e:
                logger.warning(f"Invalid identifier rejected: {e}")
                return []
            
            # Generate cache key for table schema
            cache_key = f"table_schema:{effective_db}:{table_name}"
            
            # Check cache first
            if cache_key in self.metadata_cache:
                cache_time = self.metadata_cache_time.get(cache_key, 0)
                if time.time() - cache_time < self.cache_ttl:
                    logger.debug(f"Cache hit for table schema: {effective_db}.{table_name}")
                    return self.metadata_cache[cache_key]
                else:
                    logger.debug(f"Cache expired for table schema: {effective_db}.{table_name}")
                    # Remove expired cache entry
                    del self.metadata_cache[cache_key]
                    del self.metadata_cache_time[cache_key]
            
            logger.debug(f"Cache miss for table schema: {effective_db}.{table_name}, querying database")
            
            query = f"""
            SELECT 
                COLUMN_NAME AS `Field`,
                COLUMN_TYPE AS `Type`,
                CASE WHEN COLUMN_KEY = 'PRI' THEN 'YES' ELSE '' END AS `Key`,
                IS_NULLABLE AS `Null`,
                COLUMN_DEFAULT AS `Default`,
                EXTRA,
                COLUMN_COMMENT AS `Comment`  
            FROM 
                information_schema.columns 
            WHERE 
                TABLE_SCHEMA = '{effective_db}' 
                AND TABLE_NAME = '{table_name}'
            ORDER BY 
                ORDINAL_POSITION
            """
            result = await self._execute_query_with_catalog_async(query, effective_db)

            # Use the result from the catalog-aware query
            # result = await self._execute_query_async(query, db_name)  # BUGFIX: Removed redundant query that overwrote results
            
            if not result:
                return []
            
            # Process results
            schema = []
            for row in result:
                if isinstance(row, dict):
                    schema.append({
                        'column_name': row.get('Field', ''),
                        'data_type': row.get('Type', ''),
                        'is_nullable': row.get('Null', 'NO') == 'YES',
                        'default_value': row.get('Default', None),
                        'comment': row.get('Comment', ''),
                        'key': row.get('Key', ''),
                        'extra': row.get('Extra', ''),
                        'comment': row.get('Comment', '')
                    })
            
            # Store result in cache
            self.metadata_cache[cache_key] = schema
            self.metadata_cache_time[cache_key] = time.time()
            logger.debug(f"Cached table schema for: {effective_db}.{table_name}")
            
            return schema
            
        except Exception as e:
            logger.error(f"Failed to get table schema: {e}")
            return []
    


    async def get_bi_database_tables_async(self, db_name: str = None) -> List[Dict[str, Any]]:
        """Asynchronously get table list in database with caching"""
        try:
            effective_db = db_name or self.db_name
            
            # SECURITY FIX: Validate identifiers
            try:
                if effective_db:
                    validate_identifier(effective_db, "database name")
            except SQLSecurityError as e:
                logger.warning(f"Invalid identifier rejected: {e}")
                return []
            
            # Generate cache key for database tables
            cache_key = f"database_tables:{effective_db}"
            
            # Check cache first
            if cache_key in self.metadata_cache:
                cache_time = self.metadata_cache_time.get(cache_key, 0)
                if time.time() - cache_time < self.cache_ttl:
                    logger.debug(f"Cache hit for database tables: {effective_db}")
                    return self.metadata_cache[cache_key]
                else:
                    logger.debug(f"Cache expired for database tables: {effective_db}")
                    # Remove expired cache entry
                    del self.metadata_cache[cache_key]
                    del self.metadata_cache_time[cache_key]
            
            logger.debug(f"Cache miss for database tables: {effective_db}, querying database")
            
            query = f"""
            SELECT 
                TABLE_NAME AS `TABLE_NAME`,
                TABLE_COMMENT AS `TABLE_COMMENT`  
            FROM 
                information_schema.tables 
            WHERE 
                TABLE_SCHEMA = '{effective_db}' 
                AND TABLE_TYPE = 'BASE TABLE'
            """
            result = await self._execute_query_with_catalog_async(query, effective_db)

            
            if not result:
                return []
            
            # Extract table names
            tables = []
            for row in result:
                if isinstance(row, dict):
                    tables.append({
                        'table_name': row.get('TABLE_NAME', ''),
                        'table_comment': row.get('TABLE_COMMENT', '')
                    })
            
            # Store result in cache
            self.metadata_cache[cache_key] = tables
            self.metadata_cache_time[cache_key] = time.time()
            logger.debug(f"Cached database tables for: {effective_db}")
            
            return tables
            
        except Exception as e:
            logger.error(f"Failed to get table list: {e}")
            return []



    # ==================== Business layer methods (original metadata_tools.py functionality) ====================
    
    def _format_response(self, success: bool, result: Any = None, error: str = None, message: str = "") -> Dict[str, Any]:
        """Format response result"""
        response_data = {
            "success": success,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        if success and result is not None:
            response_data["result"] = result
            response_data["message"] = message or "Operation successful"
        elif not success:
            response_data["error"] = error or "Unknown error"
            response_data["message"] = message or "Operation failed"
        
        return response_data

    async def exec_query_for_mcp(
        self,
        sql: str,
        db_name: str = None,
        catalog_name: str = None,
        max_rows: int = 100,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Execute SQL query and return results, supports catalog federation queries
        Unified interface for MCP tools

        FIX for Issue #62 Bug 1: Now retrieves auth_context from context variable to support token-bound database configuration
        FIX for Issue #62 Bug 3: Now uses db_name and catalog_name parameters to switch database context
        """
        logger.info(f"Executing SQL query: {sql}, DB: {db_name}, Catalog: {catalog_name}, MaxRows: {max_rows}, Timeout: {timeout}")

        try:
            if not sql:
                return self._format_response(success=False, error="No SQL statement provided", message="Please provide SQL statement to execute")

            
            logger.debug(f"Using effective parameters - DB: {db_name}, Catalog: {catalog_name}")

            # FIX for Issue #62 Bug 3: Build context switching SQL if db_name or catalog_name is specified
            # SECURITY FIX: Validate catalog_name and db_name to prevent SQL injection
            final_sql = sql
            context_statements = []
            if catalog_name or db_name:
                # Validate and sanitize catalog_name
                if catalog_name:
                    try:
                        validate_identifier(catalog_name, "catalog name")
                    except SQLSecurityError as e:
                        logger.warning(f"Invalid catalog name rejected: {e}")
                        return self._format_response(
                            success=False, 
                            error=f"Invalid catalog name: {catalog_name}", 
                            message="Catalog name contains invalid characters"
                        )
                    # Use quote_identifier to safely escape the catalog name
                    # safe_catalog = quote_identifier(effective_catalog, "catalog name")
                    # context_statements.append(f"USE CATALOG {safe_catalog}")
                    # logger.debug(f"Switching to catalog: {effective_catalog}")

                # Validate and sanitize db_name
                if db_name:
                    try:
                        validate_identifier(db_name, "database name")
                    except SQLSecurityError as e:
                        logger.warning(f"Invalid database name rejected: {e}")
                        return self._format_response(
                            success=False, 
                            error=f"Invalid database name: {db_name}", 
                            message="Database name contains invalid characters"
                        )
                    # Use quote_identifier to safely escape the database name
                    # safe_db = quote_identifier(effective_db, "database name")
                    # if effective_catalog:
                    #     safe_catalog = quote_identifier(effective_catalog, "catalog name")
                    #     context_statements.append(f"USE {safe_catalog}.{safe_db}")
                    # else:
                    #     context_statements.append(f"USE {safe_db}")
                    # logger.debug(f"Switching to database: {effective_db}")


                # Combine context switching with original SQL
                if context_statements:
                    # Remove trailing semicolon from context statements if present
                    context_sql = "; ".join(context_statements)
                    # Ensure original SQL doesn't start with semicolon
                    sql_clean = sql.lstrip(";").strip()
                    final_sql = f"{context_sql}; {sql_clean}"
                    logger.debug(f"Modified SQL with context switching: {final_sql[:200]}...")

            # FIX: Try to get auth_context from context variable (set by HTTP middleware)
            # This allows token-bound database configuration to work
            auth_context = None
            try:
                from contextvars import ContextVar
                from .security import AuthContext

                # Try to get auth_context from context variable
                # This will be set by the HTTP request handler in main.py
                auth_context_var: ContextVar = ContextVar('mcp_auth_context', default=None)
                auth_context = auth_context_var.get()

                if auth_context:
                    logger.debug(f"Retrieved auth_context from context variable with token: {bool(hasattr(auth_context, 'token') and auth_context.token)}")
                else:
                    logger.debug("No auth_context found in context variable, using default")
            except Exception as ctx_error:
                logger.debug(f"Could not retrieve auth_context from context variable: {ctx_error}")
                auth_context = None

            # Import query executor
            from .query_executor import execute_sql_query

            # Call execute_sql_query to execute query with auth_context
            exec_result = await execute_sql_query(
                sql=final_sql,  # Use modified SQL with context switching
                connection_manager=self.connection_manager,
                limit=max_rows,
                timeout=timeout,
                auth_context=auth_context  # FIX: Pass auth_context with token
            )

            return exec_result

        except Exception as e:
            logger.error(f"Failed to execute SQL query: {str(e)}", exc_info=True)
            return self._format_response(success=False, error=str(e), message="Error occurred while executing SQL query")

    async def get_table_schema_for_mcp(
        self, 
        table_name: str, 
        db_name: str = None
    ) -> Dict[str, Any]:
        """Get detailed schema information for specified table (columns, types, comments, etc.) - MCP interface"""
        logger.info(f"Getting table schema: Table: {table_name}, DB: {db_name}")
        
        if not table_name:
            return self._format_response(success=False, error="Missing table_name parameter")
        
        # SECURITY: Validate identifiers before processing
        try:
            validate_identifier(table_name, "table name")
        except SQLSecurityError as e:
            return self._format_response(
                success=False, 
                error=f"Invalid table name: {table_name}",
                message="Table name contains invalid characters"
            )
        
        if db_name:
            try:
                validate_identifier(db_name, "database name")
            except SQLSecurityError as e:
                return self._format_response(
                    success=False,
                    error=f"Invalid database name: {db_name}",
                    message="Database name contains invalid characters"
                )
        
        effective_db = db_name or self.db_name
        
        logger.info(f"Using effective parameters - DB: {effective_db}, Table: {table_name}")
        
        try:
            schema = await self.get_bi_table_schema_async(table_name=table_name, db_name=effective_db)
            
            if not schema:
                return self._format_response(
                    success=False, 
                    error="Table does not exist or has no columns", 
                    message=f"Unable to get schema for {effective_db}.{table_name}"
                )
            
            return self._format_response(success=True, result=schema)
        except Exception as e:
            logger.error(f"Failed to get table schema: {str(e)}", exc_info=True)
            return self._format_response(success=False, error=str(e), message="Error occurred while getting table schema")

    async def get_db_table_list_for_mcp(
        self, 
        db_name: str = None
    ) -> Dict[str, Any]:
        """Get list of all table names in specified database - MCP interface"""
        logger.info(f"Getting database table list: DB: {db_name}")
        
        # SECURITY: Validate identifiers
        if db_name:
            try:
                validate_identifier(db_name, "database name")
            except SQLSecurityError as e:
                return self._format_response(
                    success=False,
                    error=f"Invalid database name: {db_name}",
                    message="Database name contains invalid characters"
                )
        
        
        # Initialize overrides for None or empty values
        effective_db = db_name or self.db_name
        
        logger.info(f"Using effective parameters - DB: {effective_db}")
        
        try:
            tables = await self.get_bi_database_tables_async(db_name=effective_db)
            return self._format_response(success=True, result=tables)
        except Exception as e:
            logger.error(f"Failed to get database table list: {str(e)}", exc_info=True)
            return self._format_response(success=False, error=str(e), message="Error occurred while getting database table list")
