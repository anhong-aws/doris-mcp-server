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
Apache Doris Database Connection Management Module

Provides high-performance database connection pool management, automatic reconnection mechanism and connection health check functionality
Supports asynchronous operations and concurrent connection management, ensuring stability and performance for enterprise applications
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

import aiomysql
from aiomysql import Connection, Pool

from .logger import get_logger




@dataclass
class ConnectionMetrics:
    """Connection pool performance metrics"""

    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    connection_errors: int = 0
    acquisition_timeouts: int = 0
    query_timeouts: int = 0
    validation_errors: int = 0
    avg_connection_time: float = 0.0
    last_health_check: datetime | None = None
    last_error_time: datetime | None = None
    error_log: list[dict] = field(default_factory=list)


@dataclass
class QueryResult:
    """Query result wrapper"""

    data: list[dict[str, Any]]
    metadata: dict[str, Any]
    execution_time: float
    row_count: int


class DorisConnection:
    """Doris database connection wrapper class"""

    def __init__(self, connection: Connection, session_id: str, security_manager=None):
        self.connection = connection
        self.session_id = session_id
        self.created_at = datetime.utcnow()
        self.last_used = datetime.utcnow()
        self.query_count = 0
        self.last_sql = None
        self.is_healthy = True
        self.security_manager = security_manager
        self.logger = get_logger(__name__)

    async def execute(self, sql: str, params: tuple | None = None, auth_context=None) -> QueryResult:
        """Execute SQL query"""
        start_time = time.time()

        try:
            # If security manager exists, perform SQL security check
            security_result = None
            if self.security_manager and auth_context:
                validation_result = await self.security_manager.validate_sql_security(sql, auth_context)
                if not validation_result.is_valid:
                    raise ValueError(f"SQL security validation failed: {validation_result.error_message}")
                security_result = {
                    "is_valid": validation_result.is_valid,
                    "risk_level": validation_result.risk_level,
                    "blocked_operations": validation_result.blocked_operations
                }

            async with self.connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(sql, params)

                # Check if it's a query statement (statement that returns result set)
                # FIX for Issue #62 Bug 5: Added WITH support for Common Table Expressions (CTE)
                sql_upper = sql.strip().upper()
                if (sql_upper.startswith("SELECT") or
                    sql_upper.startswith("SHOW") or
                    sql_upper.startswith("DESCRIBE") or
                    sql_upper.startswith("DESC") or
                    sql_upper.startswith("EXPLAIN") or
                    sql_upper.startswith("WITH")):  # FIX: Support CTE queries
                    data = await cursor.fetchall()
                    row_count = len(data)
                else:
                    data = []
                    row_count = cursor.rowcount

                execution_time = time.time() - start_time
                self.last_used = datetime.utcnow()
                self.query_count += 1
                self.last_sql = sql


                # Get column information
                columns = []
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]

                # If security manager exists and has auth context, apply data masking
                final_data = list(data) if data else []
                if self.security_manager and auth_context and final_data:
                    final_data = await self.security_manager.apply_data_masking(final_data, auth_context)

                metadata = {"columns": columns, "query": sql, "params": params}
                if security_result:
                    metadata["security_check"] = security_result

                return QueryResult(
                    data=final_data,
                    metadata=metadata,
                    execution_time=execution_time,
                    row_count=row_count,
                )

        except Exception as e:
            self.is_healthy = False
            logging.error(f"Query execution failed: {e}")
            raise

    async def ping(self) -> bool:
        """Check connection health status with enhanced at_eof error detection"""
        try:
            # Check 1: Connection exists and is not closed
            if not self.connection or self.connection.closed:
                self.is_healthy = False
                return False
            
            # Check 2: Use ONLY safe operations - avoid internal state access
            # Instead of checking _reader state directly, use a simple query test
            try:
                # Use a simple query with timeout instead of ping() to avoid at_eof issues
                async with asyncio.timeout(3):  # 3 second timeout
                    async with self.connection.cursor() as cursor:
                        await cursor.execute("SELECT 1")
                        result = await cursor.fetchone()
                        if result and result[0] == 1:
                            self.is_healthy = True
                            return True
                        else:
                            self.logger.debug(f"Connection {self.session_id} ping query returned unexpected result")
                            self.is_healthy = False
                            return False
            
            except asyncio.TimeoutError:
                self.logger.debug(f"Connection {self.session_id} ping timed out")
                self.is_healthy = False
                return False
            except Exception as query_error:
                # Check for specific at_eof related errors
                error_str = str(query_error).lower()
                if 'at_eof' in error_str or 'nonetype' in error_str:
                    self.logger.debug(f"Connection {self.session_id} ping failed with at_eof error: {query_error}")
                else:
                    self.logger.debug(f"Connection {self.session_id} ping failed: {query_error}")
                self.is_healthy = False
                return False
            
        except Exception as e:
            # Catch any other unexpected errors
            self.logger.debug(f"Connection {self.session_id} ping failed with unexpected error: {e}")
            self.is_healthy = False
            return False

    async def close(self):
        """Close connection"""
        try:
            if self.connection and not self.connection.closed:
                await self.connection.ensure_closed()
        except Exception as e:
            logging.error(f"Error occurred while closing connection: {e}")


class DorisSessionCache:
    """Doris database session cache

    Save doris session in memory and get session by session id.
    Provide cache_system_session/cache_user_session to specify whether to save system/user type sessions.
    By default, only session_id is "query" or "system" will be saved.
    """

    def __init__(self, connection_manager=None, cache_system_session=True, cache_user_session=False):
        self.logger = get_logger(__name__)
        self.cached = {}
        self.connection_manager = connection_manager
        self.cache_system_session = cache_system_session
        self.cache_user_session = cache_user_session
        self.logger.info(f"Session  Cache initialized, save system session: {self.cache_system_session}, save user session: {self.cache_user_session}")

    def save(self, connection: DorisConnection):
        if self._should_cache(connection.session_id):
            self.cached[connection.session_id] = connection

    def get(self, session_id: str) -> Optional[DorisConnection]:
        self.logger.debug(f"Use cached connection: {session_id}")
        return self.cached.get(session_id)

    def get_all_sessions(self):
        """Get all cached sessions"""
        return self.cached.copy()

    def remove(self, session_id):
        if session_id in self.cached:
            del self.cached[session_id]
            self.logger.debug(f"Removed session {session_id} from cache.")
        else:
            if self._should_cache(session_id):
                self.logger.warning(f"Session {session_id} is not existed.")

    def clear(self):
        if self.connection_manager:
            for k, v in self.cached.items():
                self.connection_manager.release_connection(k, v)
        self.cached = {}

    def _is_system_session(self, session_id) -> bool:
        return session_id in ["query", "system"]

    def _should_cache(self, session_id):
        return (self.cache_system_session and self._is_system_session(session_id)) or (self.cache_user_session and not self._is_system_session(session_id))


class DorisConnectionManager:
    """Doris database connection manager - Enhanced Strategy

    Uses direct connection pool management with proper synchronization
    Implements connection pool health monitoring and proactive cleanup
    Supports token-bound database configurations for multi-tenant access
    """


    def __init__(self, config, security_manager=None, token_manager=None):
        self.config = config
        self.pool: Pool | None = None
        self.logger = get_logger(__name__)
        self.security_manager = security_manager
        self.token_manager = token_manager  # Token manager for token-bound DB config

        # FIX for Issue #58 Problem 1: Disable session caching to prevent connection sharing
        # Session caching causes multiple threads to share the same MySQL connection,
        # leading to race conditions and deadlocks in multi-threaded environments
        # By disabling caching, each request gets a fresh connection from the pool
        self.session_cache = DorisSessionCache(
            self,
            cache_system_session=False,  # Disabled to prevent multi-thread issues
            cache_user_session=False     # Disabled to prevent multi-thread issues
        )
        
        # Store original database config for fallback
        self.original_db_config = {
            'host': config.database.host,
            'port': config.database.port, 
            'user': config.database.user,
            'password': config.database.password,
            'database': config.database.database,
            'charset': config.database.charset
        }
        
        # Current active database config (may be overridden by token-bound config)
        self.active_db_config = self.original_db_config.copy()

        # Connection pool state management
        self.pool_recovering = False
        self.pool_health_check_task = None
        self._health_check_in_progress = False  # Flag to prevent concurrent health checks
        
        # Metrics tracking
        self.metrics = ConnectionMetrics()
        
        # 🔧 FIX: Add connection acquisition lock to prevent race conditions
        self._connection_lock = asyncio.Lock()
        self._recovery_lock = asyncio.Lock()
        
        # 🔧 FIX: Add connection acquisition queue to serialize requests
        self._connection_semaphore = asyncio.Semaphore(value=20)  # Max concurrent acquisitions
        
        # Database connection parameters from config.database
        self.pool_recovery_lock = self._recovery_lock  # Compatibility alias
        self._update_db_params_from_config(self.active_db_config)
        self.connect_timeout = config.database.connection_timeout
        
        # Connection pool parameters - more conservative settings
        self.minsize = config.database.min_connections  # This is always 0
        self.maxsize = config.database.max_connections or 20
        self.pool_recycle = config.database.max_connection_age or 3600  # 1 hour, more conservative
        
        # 🔧 FIX: Add missing monitoring parameters that were removed during refactoring
        self.health_check_interval = 30  # seconds
        self.pool_warmup_size = 3  # connections to maintain
        
        # 🔧 ADD: Track all connections (active and idle) with details
        self._all_connections = {}  # connection_id -> connection_details
        self._connection_counter = 0  # Counter for unique connection IDs (fallback)
        self._connections_lock = asyncio.Lock()
        
        # 🔧 ADD: Connection cleanup mechanism
        self.connection_cleanup_interval = 300  # 5 minutes
        self.connection_cleanup_task = None
        self.connection_cleanup_lock = asyncio.Lock()
    
    def _update_db_params_from_config(self, db_config: dict):
        """Update database connection parameters from config dictionary"""
        self.host = db_config['host']
        self.port = db_config['port']
        self.user = db_config['user']
        self.password = db_config['password']
        self.database = db_config['database']
        # Convert charset to aiomysql compatible format
        charset_map = {"UTF8": "utf8", "UTF8MB4": "utf8mb4"}
        self.charset = charset_map.get(db_config['charset'].upper(), db_config['charset'].lower())
    
    def _is_config_empty(self, config_value) -> bool:
        """Check if a config value is empty (None, empty string, or 'null')"""
        return config_value is None or config_value == '' or str(config_value).lower() == 'null'
    
    def _has_valid_global_config(self) -> bool:
        """Check if global database configuration is valid and non-empty"""
        return (not self._is_config_empty(self.original_db_config['host']) and
                not self._is_config_empty(self.original_db_config['user']))

    async def _recreate_pool(self):
        try:
            # Create new pool with current config
            await self._recover_pool_with_lock()
        except Exception as e:
            self.logger.error(f"Failed to recreate connection pool: {e}")
            raise

    def validate_database_configuration(self) -> tuple[bool, str]:
        """Validate database configuration completeness
        
        Returns:
            (is_valid, error_message): Configuration validation result
        """
        
        
        # Validate .env database configuration
        env_config_valid = self._has_valid_global_config()
        
        # tokens.json does not exist - must have valid .env config
        if env_config_valid:
            return True, "Configuration valid"
        else:
            return False, (
                "Valid database configuration is required "
                "in .env file (DB_HOST, DB_USER, etc.)"
            )

    async def _initialize_connection_pool(self, timeout: float, mode: str, strict: bool = False) -> bool:
        """
        Internal method to initialize connection pool with configurable parameters
        
        Args:
            timeout: Maximum time to wait for connection establishment
            mode: Mode identifier for logging ("stdio" or "http")
            strict: If True, raises exceptions on failure; if False, returns False on failure
            
        Returns:
            bool: True if initialization succeeded, False otherwise
            
        Raises:
            RuntimeError: If strict=True and initialization fails
        """
        try:
            # Validate that we have valid global configuration
            if not self._has_valid_global_config():
                error_msg = (
                    f"{mode} mode requires valid global database configuration. "
                    "Please set DORIS_HOST and DORIS_USER in environment variables or .env file. "
                    f"Current config: host='{self.host}', user='{self.user}'"
                )
                if strict:
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
                self.logger.info("No valid global database config found")
                return False
            
            self.logger.info(f"{mode} mode database config validated: {self.host}:{self.port}")
            
            # Validate configuration format
            is_valid, error_message = self.validate_database_configuration()
            if not is_valid:
                error_msg = f"Database configuration validation failed: {error_message}"
                if strict:
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
                self.logger.warning(error_msg)
                return False
            
            # Test connectivity with timeout
            self.logger.info(f"Testing database connectivity for {mode} mode...")
            if not await self._test_connectivity_with_timeout(timeout):
                error_msg = (
                    f"Failed to connect to Doris database within {timeout} seconds. "
                    f"Please check if Doris is running at {self.host}:{self.port} "
                    f"and verify network connectivity."
                )
                if strict:
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
                self.logger.warning("Global database connection test failed")
                return False
            
            # Initialize the connection pool
            
            self.pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.database,
                charset=self.charset,
                minsize=self.minsize,
                maxsize=self.maxsize,
                pool_recycle=self.pool_recycle,
                connect_timeout=self.connect_timeout,
                autocommit=True
            )
            
            # Test pool health

            if self.pool:
                if not await self._test_pool_health():
                    # Clean up the pool if health test fails
                    if self.pool:
                        self.pool.close()
                        await self.pool.wait_closed()
                        self.pool = None
                    error_msg = "Database connection pool was not created successfully."
                    if strict:
                        self.logger.error(error_msg)
                        raise RuntimeError(error_msg)
                    self.logger.warning("Database connection pool creation failed")
                    return False
            else:
                error_msg = "Database connection pool was not created successfully."
                if strict:
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
                self.logger.warning("Database connection pool creation failed")
                return False
            
            # Perform initial pool warmup
            await self._warmup_pool()

            # Start background monitoring tasks
            self.pool_health_check_task = asyncio.create_task(self._pool_health_monitor())
            
            
            self.logger.info(f"Database connection established successfully for {mode} mode")
            return True
            
        except Exception as e:
            if strict:
                self.logger.error(f"{mode} mode database initialization failed: {e}")
                raise
            self.logger.warning(f"{mode} mode database initialization encountered error: {e}")
            return False
    
    async def initialize_for_stdio_mode(self, timeout: float = 30.0) -> None:
        """
        Initialize connection pool for stdio mode with strict validation
        
        stdio mode requires a working database connection because:
        - All database operations depend on the global connection pool
        
        Args:
            timeout: Maximum time to wait for connection establishment
            
        Raises:
            RuntimeError: If configuration is invalid or connection fails
        """
        success = await self._initialize_connection_pool(timeout, "stdio", strict=True)
    
    async def initialize_for_http_mode(self) -> bool:
        success = await self._initialize_connection_pool(10.0, "HTTP", strict=True)
        if not success:
            self.logger.info("Init global connection pool failed")
        return success
    
    async def _test_connectivity_with_timeout(self, timeout: float) -> bool:
        """
        Test database connectivity with timeout
        
        Args:
            timeout: Maximum time to wait for connection test
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            await asyncio.wait_for(self._test_basic_connectivity(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            self.logger.error(f"Database connectivity test timed out after {timeout} seconds")
            return False
        except Exception as e:
            self.logger.error(f"Database connectivity test failed: {e}")
            return False
    
    async def _test_basic_connectivity(self) -> None:
        """
        Test basic database connectivity without connection pool
        
        Raises:
            Exception: If connection fails
        """
        import aiomysql
        
        conn = None
        try:
            conn = await aiomysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.database,
                charset=self.charset,
                connect_timeout=self.connect_timeout,
                autocommit=True
            )
            
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1")
                result = await cursor.fetchone()
                if not result or result[0] != 1:
                    raise RuntimeError("Database connectivity test query failed")
                    
        except Exception as e:
            raise RuntimeError(f"Database connectivity test failed: {e}")
        finally:
            if conn:
                conn.close()

    async def _test_pool_health(self) -> bool:
        """Enhanced connection pool health test with timeout and multiple checks"""
        self._health_check_in_progress = True
        try:
            # Check 1: Pool exists and is not closed
            if not self.pool or self.pool.closed:
                self.logger.error("Pool health test failed: Pool not available or closed")
                self.log_connection_error('pool_unavailable', 'Pool not available or closed')
                return False

            # Get pool statistics for debugging
            pool_stats = {
                'size': self.pool.size if hasattr(self.pool, 'size') else 'unknown',
                'freesize': self.pool.freesize if hasattr(self.pool, 'freesize') else 'unknown',
                'closed': self.pool.closed if hasattr(self.pool, 'closed') else 'unknown'
            }
            self.logger.debug(f"Pool health check starting with stats: {pool_stats}")

            conn = None
            connection_healthy = False
            
            # Check 2: Try to acquire a connection with timeout
            try:
                async with asyncio.timeout(8.0):  # Increased timeout from 5 to 8 seconds
                    self.logger.debug("Attempting to acquire connection for health check...")
                    conn = await self.pool.acquire()
                    self.logger.debug("Successfully acquired connection for health check")
            except asyncio.TimeoutError:
                self.logger.error(f"Pool health test failed: Connection acquisition timeout. Pool stats: {pool_stats}")
                self.log_connection_error('acquisition_timeout', f'Connection acquisition timeout during health check. Pool stats: {pool_stats}')
                return False
            except Exception as acquire_error:
                self.logger.error(f"Pool health test failed: Connection acquisition error: {acquire_error}. Pool stats: {pool_stats}")
                self.log_connection_error('connection_error', f'Connection acquisition error during health check: {acquire_error}. Pool stats: {pool_stats}')
                return False

            # If we got a connection, test it properly
            try:
                # Check connection state
                conn_state = {
                    'closed': conn.closed if hasattr(conn, 'closed') else 'unknown',
                    'valid': not (hasattr(conn, 'closed') and conn.closed)
                }
                self.logger.debug(f"Connection state: {conn_state}")

                # Check 3: Test connection with actual query
                try:
                    async with asyncio.timeout(5.0):  # Increased timeout from 3 to 5 seconds
                        async with conn.cursor() as cursor:
                            self.logger.debug("Executing health check query: SELECT 1")
                            await cursor.execute("SELECT 1")
                            self.logger.debug("Successfully executed health check query")
                            result = await cursor.fetchone()
                            self.logger.debug(f"Health check query result: {result}")
                            
                            if not result or result[0] != 1:
                                self.logger.error(f"Pool health test failed: Unexpected query result: {result}")
                                self.log_connection_error('validation_error', f'Unexpected query result during health check: {result}')
                                # Close unhealthy connection
                                await conn.ensure_closed()
                                self.logger.debug("Closed unhealthy connection due to unexpected query result")
                                return False
                except asyncio.TimeoutError:
                    self.logger.error("Pool health test failed: Query execution timeout")
                    self.log_connection_error('query_timeout', 'Query execution timeout during health check')
                    # Close unhealthy connection
                    await conn.ensure_closed()
                    self.logger.debug("Closed unhealthy connection due to query timeout")
                    return False
                except Exception as query_error:
                    self.logger.error(f"Pool health test failed: Query execution error: {query_error}")
                    self.log_connection_error('query_error', f'Query execution error during health check: {query_error}')
                    # Close unhealthy connection
                    await conn.ensure_closed()
                    self.logger.debug(f"Closed unhealthy connection due to query error: {query_error}")
                    return False

                # Check 4: Verify connection properties
                if hasattr(conn, 'closed') and conn.closed:
                    self.logger.error("Pool health test failed: Connection is closed")
                    self.log_connection_error('validation_error', 'Connection is closed during health check')
                    # Close unhealthy connection (already closed, but be safe)
                    try:
                        await conn.ensure_closed()
                    except Exception:
                        pass
                    self.logger.debug("Connection already closed")
                    return False

                # All checks passed - connection is healthy
                connection_healthy = True
                self.logger.debug("✅ All health check tests passed")
                return True
                
            finally:
                # Only release healthy connections back to the pool
                if conn:
                    try:
                        if connection_healthy:
                            self.pool.release(conn)
                            self.logger.debug("Successfully released healthy connection back to pool")
                        else:
                            # Connection was marked unhealthy during tests
                            try:
                                await conn.ensure_closed()
                                self.logger.debug("Closed unhealthy connection in finally block")
                            except Exception as close_error:
                                self.logger.error(f"Error closing unhealthy connection: {close_error}")
                                self.log_connection_error('connection_error', f'Error closing unhealthy connection: {close_error}')
                    except Exception as release_error:
                        self.logger.error(f"Error handling connection in finally block: {release_error}")
                        self.log_connection_error('connection_error', f'Error handling connection in finally block: {release_error}')
                        # If any error, ensure connection is closed
                        try:
                            await conn.ensure_closed()
                        except Exception:
                            pass

        except Exception as e:
            self.logger.error(f"Pool health test failed with unexpected error: {e}")
            self.log_connection_error('unknown_error', f'Unknown error during health check: {e}')
            return False
        finally:
            self._health_check_in_progress = False

    async def _warmup_pool(self):
        """Warm up connection pool by creating initial connections"""
        self.logger.info(f"🔥 Warming up connection pool with {self.pool_warmup_size} connections")
        
        warmup_connections = []
        try:
            # Acquire connections to force pool to create them
            for i in range(self.pool_warmup_size):
                try:
                    self.logger.debug(f"Attempting to warm up connection {i+1}/{self.pool_warmup_size}")
                    conn = await asyncio.wait_for(self.pool.acquire(), timeout=10.0)
                    warmup_connections.append(conn)
                    self.logger.debug(f"Successfully warmed up connection {i+1}/{self.pool_warmup_size}")
                except asyncio.TimeoutError:
                    self.logger.warning(f"Timeout warming up connection {i+1}: Connection acquisition timed out")
                    break
                except Exception as e:
                    self.logger.warning(f"Failed to warm up connection {i+1}: {e}")
                    break
            
            self.logger.debug(f"Successfully acquired {len(warmup_connections)} warmup connections")
            
            # Release all warmup connections back to pool
            released_count = 0
            for i, conn in enumerate(warmup_connections):
                try:
                    # Check connection state before release
                    if conn and not conn.closed:
                        self.pool.release(conn)
                        released_count += 1
                        self.logger.debug(f"Successfully released warmup connection {i+1}")
                    else:
                        self.logger.warning(f"Skipping release of connection {i+1} - already closed")
                except Exception as e:
                    self.logger.warning(f"Failed to release warmup connection {i+1}: {e}")
                    try:
                        if conn and hasattr(conn, 'ensure_closed'):
                            await conn.ensure_closed()
                    except Exception:
                        pass
            
            self.logger.info(f"✅ Pool warmup completed: {len(warmup_connections)} connections created, {released_count} released back to pool")

        except Exception as e:
            self.logger.error(f"Pool warmup failed: {e}")
            # Clean up any remaining connections
            for i, conn in enumerate(warmup_connections):
                try:
                    if conn and hasattr(conn, 'ensure_closed'):
                        await conn.ensure_closed()
                        self.logger.debug(f"Cleaned up warmup connection {i+1} during error handling")
                except Exception:
                    pass

    async def _pool_health_monitor(self):
        """Background task to monitor pool health"""
        self.logger.info("🩺 Starting pool health monitor")
        
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                # Skip health check if cleanup or another health check is in progress
                if hasattr(self, '_health_check_in_progress') and self._health_check_in_progress:
                    self.logger.debug("Another health check in progress, skipping")
                    continue
                await self._check_pool_health()
            except asyncio.CancelledError:
                self.logger.info("Pool health monitor stopped")
                break
            except Exception as e:
                self.logger.error(f"Pool health monitor error: {e}")

    async def _check_pool_health(self):
        """Check and maintain pool health"""
        try:
            # Skip health check if already recovering
            if self.pool_recovering:
                self.logger.debug("Pool recovery in progress, skipping health check")
                return
            
            # Skip cleanup if no pool or pool is closed
            if not self.pool or self.pool.closed:
                self.logger.debug("No active pool, skipping stale connection cleanup")
                return
            
            # Get pool statistics
            pool_size = getattr(self.pool, 'size', 0)
            pool_free = getattr(self.pool, 'freesize', 0)
            
            self.logger.debug(f"Pool stats before cleanup: size={pool_size}, freesize={pool_free}")
            
            # If pool has idle connections, test some of them
            test_count = max(pool_free, 1)  # Test up to idle connections
            for i in range(test_count):
                # Test pool with a simple query
                health_ok = await self._test_pool_health()
                
                if health_ok:
                    self.logger.debug("✅ Pool health check passed")
                    self.metrics.last_health_check = datetime.utcnow()
                else:
                    self.logger.warning("❌ Pool health check failed, attempting recovery")
                    await self._recover_pool_with_lock()
                    break
                
        except Exception as e:
            self.logger.error(f"Pool health check error: {e}")
            await self._recover_pool_with_lock()

    async def _recover_pool(self):
        """Recover connection pool when health check fails"""
        # Check if another recovery is already in progress
        if self.pool_recovering:
            self.logger.debug("Pool recovery already in progress, waiting...")
            return
            
        try:
            self.pool_recovering = True
            max_retries = 3
            retry_delay = 5  # seconds
            
            for attempt in range(max_retries):
                try:
                    self.logger.info(f"🔄 Attempting pool recovery (attempt {attempt + 1}/{max_retries})")
                    
                    # Try to close existing pool with timeout
                    if self.pool:
                        try:
                            if not self.pool.closed:
                                self.pool.close()
                                await asyncio.wait_for(self.pool.wait_closed(), timeout=3.0)
                            self.logger.debug("Old pool closed successfully")
                        except asyncio.TimeoutError:
                            self.logger.warning("Pool close timeout, forcing cleanup")
                        except Exception as e:
                            self.logger.warning(f"Error closing old pool: {e}")
                        finally:
                            self.pool = None
                    
                    # Wait before creating new pool (reduced delay)
                    if attempt > 0:
                        await asyncio.sleep(2)  # Reduced from 5 to 2 seconds
                    
                    # Recreate pool with timeout
                    self.logger.debug("Creating new connection pool...")
                    self.pool = await asyncio.wait_for(
                        aiomysql.create_pool(
                            host=self.host,
                            port=self.port,
                            user=self.user,
                            password=self.password,
                            db=self.database,
                            charset=self.charset,
                            minsize=self.minsize,
                            maxsize=self.maxsize,
                            pool_recycle=self.pool_recycle,
                            connect_timeout=self.connect_timeout,
                            autocommit=True
                        ),
                        timeout=10.0
                    )
                    
                    # Test recovered pool with timeout
                    if await asyncio.wait_for(self._test_pool_health(), timeout=5.0):
                        self.logger.info(f"✅ Pool recovery successful on attempt {attempt + 1}")
                        # Re-warm the pool with timeout
                        try:
                            await asyncio.wait_for(self._warmup_pool(), timeout=5.0)
                        except asyncio.TimeoutError:
                            self.logger.warning("Pool warmup timeout, but recovery successful")
                        return
                    else:
                        self.logger.warning(f"❌ Pool recovery health check failed on attempt {attempt + 1}")
                        
                except asyncio.TimeoutError:
                    self.logger.error(f"Pool recovery attempt {attempt + 1} timed out")
                    if self.pool:
                        try:
                            self.pool.close()
                        except:
                            pass
                        self.pool = None
                except Exception as e:
                    self.logger.error(f"Pool recovery error on attempt {attempt + 1}: {e}")
                    
                    # Clean up failed pool
                    if self.pool:
                        try:
                            self.pool.close()
                            await asyncio.wait_for(self.pool.wait_closed(), timeout=2.0)
                        except Exception:
                            pass
                        finally:
                            self.pool = None
            
            # All recovery attempts failed
            self.logger.error("❌ Pool recovery failed after all attempts")
            self.pool = None
            
        finally:
            self.pool_recovering = False
    
    async def _recover_pool_with_lock(self):
        """🔧 FIX: Recovery method that uses the new recovery lock to prevent races"""
        async with self._recovery_lock:
            if not self.pool_recovering:  # Only recover if not already in progress
                await self._recover_pool()

    async def get_connection(self, session_id: str) -> DorisConnection:
        """🔧 FIX: Simplified connection acquisition without double locking
        
        Uses only semaphore to prevent too many concurrent acquisitions.
        If the connection is successfully obtained, it will be added to the connection pool cache.
        """
        # # 🔧 TEST: Add mock error log for testing diagnosis UI
        # self.log_connection_error(
        #     'test_error',
        #     f"Mock connection error for session {session_id} (test only)",
        #     Exception("This is a test exception")
        # )
        
        cached_conn = self.session_cache.get(session_id)
        if cached_conn:
            return cached_conn

        # 🔧 FIX: Use only semaphore to limit concurrent acquisitions (remove double locking)
        async with self._connection_semaphore:
            try:
                # Wait for any ongoing recovery to complete
                if self.pool_recovering:
                    self.logger.debug(f"Pool recovery in progress, waiting for completion...")
                    # Wait for recovery to complete (max 10 seconds)
                    start_wait = time.time()
                    while self.pool_recovering and (time.time() - start_wait) < 10:
                        await asyncio.sleep(0.1)  # More frequent checks
                    
                    if self.pool_recovering:
                        self.logger.error("Pool recovery is taking too long, proceeding anyway")
                        # Continue but log the issue
                
                # Check if pool is available
                if not self.pool:
                    self.logger.warning("Connection pool is not available, attempting recovery...")
                    
                    await self._recover_pool_with_lock()
                    
                    if not self.pool:
                        raise RuntimeError("Connection pool is not available and recovery failed")
                
                # Check if pool is closed
                if self.pool.closed:
                    self.logger.warning("Connection pool is closed, attempting recovery...")
                    await self._recover_pool_with_lock()
                    
                    if not self.pool or self.pool.closed:
                        raise RuntimeError("Connection pool is closed and recovery failed")
                
                # 🔧 FIX: Increased timeout to prevent hanging
                try:
                    raw_conn = await asyncio.wait_for(self.pool.acquire(), timeout=10.0)
                except asyncio.TimeoutError:
                    self.log_connection_error(
                        'acquisition_timeout',
                        f"Connection acquisition timed out for session {session_id}"
                    )
                    # Try one recovery attempt
                    await self._recover_pool_with_lock()
                    if self.pool and not self.pool.closed:
                        try:
                            raw_conn = await asyncio.wait_for(self.pool.acquire(), timeout=5.0)
                        except asyncio.TimeoutError:
                            self.log_connection_error(
                                'acquisition_timeout',
                                "Connection acquisition timed out after recovery"
                            )
                            raise RuntimeError("Connection acquisition timed out after recovery")
                    else:
                        self.log_connection_error(
                            'acquisition_timeout',
                            "Connection acquisition timed out"
                        )
                        raise RuntimeError("Connection acquisition timed out")
                
                # Use connection's own thread_id as unique identifier if available
                # This prevents _all_connections from growing indefinitely
                connection_id = None
                if hasattr(raw_conn, 'connection_id'):
                    connection_id = f"conn_{raw_conn.connection_id}"
                elif hasattr(raw_conn, 'thread_id'):
                    try:
                        # aiomysql.Connection has a thread_id() method, not attribute
                        thread_id = raw_conn.thread_id()
                        connection_id = f"conn_{thread_id}"
                    except Exception:
                        # Fallback if thread_id() method fails
                        pass
                elif hasattr(raw_conn, 'server_thread_id'):
                    # Direct access to server_thread_id tuple if thread_id() method fails
                    try:
                        connection_id = f"conn_{raw_conn.server_thread_id[0]}"
                    except Exception:
                        pass
                
                if not connection_id:
                    # Fallback to counter if no unique identifier available
                    connection_id = f"conn_{self._connection_counter}"
                    self._connection_counter += 1
                
                # Wrap in DorisConnection
                doris_conn = DorisConnection(raw_conn, session_id, self.security_manager)
                doris_conn.connection_id = connection_id  # Add connection_id to DorisConnection
                
                # Add to all connections tracking
                async with self._connections_lock:
                    # Check if connection already exists (same connection_id)
                    if connection_id in self._all_connections:
                        # Update existing connection information
                        conn_info = self._all_connections[connection_id]
                        # Add previous duration if it was active
                        if conn_info.get('status') == 'active' and conn_info.get('acquired_at'):
                            duration = datetime.utcnow() - conn_info['acquired_at']
                            conn_info['total_duration'] += duration.total_seconds()
                        # Update connection details
                        conn_info.update({
                            'session_id': session_id,
                            'acquired_at': datetime.utcnow(),
                            'last_activity': datetime.utcnow(),
                            'connection_object': raw_conn,
                            'doris_connection': doris_conn,
                            'status': 'active',
                        })
                    else:
                        # Create new connection details
                        conn_details = {
                            'connection_id': connection_id,
                            'session_id': session_id,
                            'acquired_at': datetime.utcnow(),
                            'last_activity': datetime.utcnow(),
                            'connection_object': raw_conn,
                            'doris_connection': doris_conn,
                            'status': 'active',
                            'release_count': 0,
                            'total_duration': 0.0,
                            'last_release_time': None
                        }
                        self._all_connections[connection_id] = conn_details
                
                # Basic validation - check if connection is open
                if raw_conn.closed:
                    # Return connection and raise error
                    try:
                        #即使连接标记为关闭，但底层资源可能没有完全释放， ensure_closed() 会确保所有资源都被正确清理
                        #防御性编程 ：避免因连接状态判断不准确导致的资源泄漏
                        await raw_conn.ensure_closed()
                        # Update connection status to idle
                        async with self._connections_lock:
                            if connection_id in self._all_connections:
                                self._all_connections[connection_id]['status'] = 'idle'
                                self._all_connections[connection_id]['last_release_time'] = datetime.utcnow()
                                self._all_connections[connection_id]['session_id'] = None
                    except Exception:
                        pass
                    raise RuntimeError("Acquired connection is already closed")
                
                self.logger.debug(f"✅ Acquired fresh connection {connection_id} for session {session_id}")

                self.session_cache.save(doris_conn)
                return doris_conn
                
            except Exception as e:
                self.logger.error(f"Failed to get connection for session {session_id}: {e}")
                raise

    async def release_connection(self, session_id: str, connection: DorisConnection):
        """🔧 FIX: Release connection back to pool with proper error handling"""
        cached_conn = self.session_cache.get(session_id)
        if cached_conn:
            self.session_cache.remove(session_id)
            if not (cached_conn is connection):
                self.logger.warning("Invalid connection")
                connection = cached_conn

        if not connection or not connection.connection:
            self.logger.debug(f"No connection to release for session {session_id}")
            return
            
        try:
            # Check pool availability before attempting release
            if not self.pool or self.pool.closed:
                self.logger.warning(f"Pool unavailable during release for session {session_id}, force closing connection")
                try:
                    await connection.connection.ensure_closed()
                except Exception:
                    pass
                return
            
            # Check connection state before release
            if connection.connection.closed:
                self.logger.debug(f"Connection already closed for session {session_id}")
                return
            
            # 🔧 FIX: Simplified release operation without thread wrapper
            try:
                self.pool.release(connection.connection)
                
                # Update connection status in tracking
                if hasattr(connection, 'connection_id') and connection.connection_id:
                    async with self._connections_lock:
                        if connection.connection_id in self._all_connections:
                            conn_info = self._all_connections[connection.connection_id]
                            # Calculate connection duration
                            if conn_info.get('acquired_at'):
                                duration = datetime.utcnow() - conn_info['acquired_at']
                                conn_info['total_duration'] += duration.total_seconds()
                            # Update connection status
                            conn_info['status'] = 'idle'
                            conn_info['last_release_time'] = datetime.utcnow()
                            conn_info['release_count'] += 1
                            conn_info['session_id'] = None  # Clear session ID when released
                            conn_info['last_activity'] = datetime.utcnow()
                            
                    self.logger.debug(f"✅ Released connection {connection.connection_id} for session {session_id}")
                else:
                    self.logger.debug(f"✅ Released connection for session {session_id}")
            except Exception as release_error:
                self.logger.warning(f"Connection release failed for session {session_id}: {release_error}, force closing")
                await connection.connection.ensure_closed()
                # Update connection status to closed if release fails
                if hasattr(connection, 'connection_id') and connection.connection_id:
                    async with self._connections_lock:
                        if connection.connection_id in self._all_connections:
                            self._all_connections[connection.connection_id]['status'] = 'closed'
                            self._all_connections[connection.connection_id]['last_release_time'] = datetime.utcnow()
                            self._all_connections[connection.connection_id]['session_id'] = None

        except Exception as e:
            self.logger.error(f"Error releasing connection for session {session_id}: {e}")
            # Force close if release fails
            try:
                await connection.connection.ensure_closed()
            except Exception as close_error:
                self.logger.debug(f"Error force closing connection: {close_error}")

    async def _cleanup_inactive_connections(self):
        """Clean up inactive connections that haven't been used for a long time"""
        try:
            self.logger.debug("Starting connection cleanup...")
            now = datetime.utcnow()
            connections_to_remove = []
            
            async with self._connections_lock:
                for conn_id, conn_info in self._all_connections.items():
                    # Remove connections that are closed or inactive for a long time
                    if conn_info.get('status') == 'closed':
                        connections_to_remove.append(conn_id)
                    elif conn_info.get('last_release_time'):
                        # Remove idle connections that haven't been used in the last hour
                        last_release = datetime.fromisoformat(conn_info['last_release_time'])
                        if (now - last_release).total_seconds() > 3600:  # 1 hour
                            connections_to_remove.append(conn_id)
                    elif conn_info.get('last_activity'):
                        # Remove connections with no release time but inactive for a long time
                        last_activity = datetime.fromisoformat(conn_info['last_activity'])
                        if (now - last_activity).total_seconds() > 3600:  # 1 hour
                            connections_to_remove.append(conn_id)
                    
                    # Remove connections that have exceeded maxsize + buffer
                    if len(self._all_connections) > self.maxsize * 2:
                        connections_to_remove.append(conn_id)
                
                # Remove identified connections
                for conn_id in connections_to_remove:
                    if conn_id in self._all_connections:
                        del self._all_connections[conn_id]
                
            if connections_to_remove:
                self.logger.debug(f"Cleaned up {len(connections_to_remove)} inactive connections")
        except Exception as e:
            self.logger.error(f"Error cleaning up inactive connections: {e}")
    
    async def _start_connection_cleanup(self):
        """Start the connection cleanup task"""
        try:
            while True:
                await asyncio.sleep(self.connection_cleanup_interval)
                await self._cleanup_inactive_connections()
        except asyncio.CancelledError:
            self.logger.info("Connection cleanup task cancelled")
        except Exception as e:
            self.logger.error(f"Connection cleanup task error: {e}")
    
    async def close(self):
        """Close connection manager"""
        try:
            # Cancel background tasks
            if self.pool_health_check_task:
                self.pool_health_check_task.cancel()
                try:
                    await self.pool_health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel connection cleanup task
            if self.connection_cleanup_task:
                self.connection_cleanup_task.cancel()
                try:
                    await self.connection_cleanup_task
                except asyncio.CancelledError:
                    pass

            # Close connection pool
            if self.pool:
                self.pool.close()
                await self.pool.wait_closed()

            self.logger.info("Connection manager closed successfully")

        except Exception as e:
            self.logger.error(f"Error closing connection manager: {e}")

    async def test_connection(self) -> bool:
        """Test database connection using robust connection test"""
        return await self._test_pool_health()

    async def get_metrics(self) -> ConnectionMetrics:
        """Get connection pool metrics - Simplified Strategy"""
        try:
            if self.pool:
                self.metrics.idle_connections = self.pool.freesize
                self.metrics.active_connections = self.pool.size - self.pool.freesize
            else:
                self.metrics.idle_connections = 0
                self.metrics.active_connections = 0
            
            return self.metrics
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}")
            return self.metrics

    async def execute_query(
        self, session_id: str, sql: str, params: tuple | None = None, auth_context=None
    ) -> QueryResult:
        """Execute query - Simplified Strategy with automatic connection management

        FIX for Issue #62 Bug 1: Configure token-bound database before query execution
        """
        connection = None
        try:
            # Always get fresh connection from pool (with configured database)
            connection = await self.get_connection(session_id)

            # Execute query
            result = await connection.execute(sql, params, auth_context)

            return result

        except Exception as e:
            self.log_connection_error(
                'query_error',
                f"Query execution failed for session {session_id}: {e}",
                e
            )
            raise
        finally:
            # Always release connection back to pool
            if connection:
                await self.release_connection(session_id, connection)

    @asynccontextmanager
    async def get_connection_context(self, session_id: str):
        """Get connection context manager - Simplified Strategy"""
        connection = None
        try:
            connection = await self.get_connection(session_id)
            yield connection
        finally:
            if connection:
                await self.release_connection(session_id, connection)

    async def get_all_connections(self) -> list[dict[str, Any]]:
        """Get all connections (active and idle) with details"""
        try:
            all_connections = []
            async with self._connections_lock:
                for conn_info in self._all_connections.values():
                    safe_conn_info = {k: v for k, v in conn_info.items() if k not in ['connection_object', 'doris_connection']}
                    # Add additional info from DorisConnection
                    if 'doris_connection' in conn_info and conn_info['doris_connection']:
                        doris_conn = conn_info['doris_connection']
                        safe_conn_info['created_at'] = doris_conn.created_at.isoformat() if doris_conn.created_at else None
                        safe_conn_info['last_used'] = doris_conn.last_used.isoformat() if doris_conn.last_used else None
                        safe_conn_info['query_count'] = doris_conn.query_count
                        safe_conn_info['is_healthy'] = doris_conn.is_healthy
                        safe_conn_info['last_sql'] = doris_conn.last_sql
                    
                    # Convert datetime objects to strings
                    for key, value in safe_conn_info.items():
                        if isinstance(value, datetime):
                            safe_conn_info[key] = value.isoformat()
                    
                    # Calculate current duration if connection is active
                    if safe_conn_info.get('status') == 'active' and safe_conn_info.get('acquired_at'):
                        acquired_at = datetime.fromisoformat(safe_conn_info['acquired_at'])
                        duration = datetime.utcnow() - acquired_at
                        safe_conn_info['current_duration'] = round(duration.total_seconds(), 2)
                    else:
                        safe_conn_info['current_duration'] = None
                    
                    all_connections.append(safe_conn_info)
            return all_connections
        except Exception as e:
            self.logger.error(f"Error getting all connections: {e}")
            return []
            
    def log_connection_error(self, error_type: str, error_message: str, error: Exception = None):
        """Log connection-related error and update metrics"""
        # Update error counters based on error type
        if error_type == 'acquisition_timeout':
            self.metrics.acquisition_timeouts += 1
        elif error_type == 'query_timeout':
            self.metrics.query_timeouts += 1
        elif error_type == 'validation_error':
            self.metrics.validation_errors += 1
        else:
            self.metrics.connection_errors += 1
            self.metrics.failed_connections += 1
            
        # Update last error time
        self.metrics.last_error_time = datetime.utcnow()
        
        # Create error log entry
        error_entry = {
            "timestamp": self.metrics.last_error_time.isoformat(),
            "type": error_type,
            "message": error_message,
            "exception": str(error) if error else None
        }
        
        # Add to error log (keep last 100 errors)
        self.metrics.error_log.append(error_entry)
        if len(self.metrics.error_log) > 100:
            self.metrics.error_log.pop(0)
        
        # Log to system logger
        self.logger.error(f"Connection error ({error_type}): {error_message}", exc_info=error)
    
    async def diagnose_connection_health(self) -> Dict[str, Any]:
        """Enhanced connection pool health diagnosis with error analysis"""
        diagnosis = {
            "timestamp": datetime.utcnow().isoformat(),
            "pool_status": "unknown",
            "pool_info": {},
            "recommendations": [],
            "error_analysis": {
                "error_count": 0,
                "last_error_time": None,
                "error_types": {},
                "recent_errors": []
            }
        }
        
        try:
            # Check pool status
            if not self.pool:
                diagnosis["pool_status"] = "not_initialized"
                diagnosis["recommendations"].append("Initialize connection pool")
                return diagnosis
            
            if self.pool.closed:
                diagnosis["pool_status"] = "closed"
                diagnosis["recommendations"].append("Recreate connection pool")
                return diagnosis
            
            # Get pool information
            diagnosis["pool_info"] = {
                "size": self.pool.size,
                "free_size": self.pool.freesize,
                "min_size": self.pool.minsize,
                "max_size": self.pool.maxsize
            }
            
            # Calculate pool utilization
            utilization = 0
            if self.pool.size > 0:
                utilization = 100 - (self.pool.freesize / self.pool.size * 100)
                diagnosis["pool_info"]["utilization"] = round(utilization, 2)
            
            # Generate recommendations based on pool status
            if self.pool.freesize == 0 and self.pool.size >= self.pool.maxsize:
                diagnosis["recommendations"].append("Connection pool exhausted - consider increasing max_connections")
            elif utilization > 90:
                diagnosis["recommendations"].append(f"High pool utilization ({utilization:.1f}%) - consider optimizing queries or increasing max_connections")
            elif utilization > 75:
                diagnosis["recommendations"].append(f"Moderate pool utilization ({utilization:.1f}%) - monitor closely")
            
            # Test pool health
            if await self._test_pool_health():
                diagnosis["pool_health"] = "healthy"
            else:
                diagnosis["pool_health"] = "unhealthy"
                diagnosis["recommendations"].append("Pool health check failed - may need recovery")
            
            # Analyze error history
            if self.metrics.error_log:
                # Count errors by type
                error_types = {}
                for error in self.metrics.error_log:
                    error_type = error["type"]
                    error_types[error_type] = error_types.get(error_type, 0) + 1
                
                # Get recent errors (last 5)
                recent_errors = sorted(self.metrics.error_log, 
                                      key=lambda x: x["timestamp"], 
                                      reverse=True)[:5]
                
                # Update diagnosis with error analysis
                diagnosis["error_analysis"] = {
                    "error_count": len(self.metrics.error_log),
                    "last_error_time": self.metrics.last_error_time.isoformat() if self.metrics.last_error_time else None,
                    "error_types": error_types,
                    "recent_errors": recent_errors
                }
                
                # Add recommendations based on error types
                if error_types.get("acquisition_timeout"):
                    diagnosis["recommendations"].append("Connection acquisition timeouts detected - check database server load or increase connection timeout")
                
                if error_types.get("query_timeout"):
                    diagnosis["recommendations"].append("Query timeouts detected - optimize slow queries or increase query timeout")
                
                if error_types.get("validation_error"):
                    diagnosis["recommendations"].append("Connection validation errors detected - check database connectivity")
                
                if error_types.get("connection_error") > 3:
                    diagnosis["recommendations"].append("Multiple connection errors detected - check database server status and network connectivity")
            
            # Update overall status based on health check and errors
            if diagnosis["pool_health"] == "healthy" and not self.metrics.error_log:
                diagnosis["pool_status"] = "healthy"
            elif diagnosis["pool_health"] == "healthy" and self.metrics.error_log:
                diagnosis["pool_status"] = "warning"
            else:
                diagnosis["pool_status"] = "unhealthy"
            
            return diagnosis
            
        except Exception as e:
            diagnosis["error"] = str(e)
            diagnosis["recommendations"].append("Manual intervention required")
            diagnosis["pool_status"] = "unhealthy"
            return diagnosis


class ConnectionPoolMonitor:
    """Connection pool monitor

    Provides detailed monitoring and reporting capabilities for connection pool status
    """

    def __init__(self, connection_manager: DorisConnectionManager):
        self.connection_manager = connection_manager
        self.logger = get_logger(__name__)

    async def get_pool_status(self) -> dict[str, Any]:
        """Get connection pool status"""
        metrics = await self.connection_manager.get_metrics()
        
        status = {
            "pool_size": self.connection_manager.pool.size if self.connection_manager.pool else 0,
            "free_connections": self.connection_manager.pool.freesize if self.connection_manager.pool else 0,
            "active_connections": metrics.active_connections,
            "idle_connections": metrics.idle_connections,
            "total_connections": metrics.total_connections,
            "failed_connections": metrics.failed_connections,
            "connection_errors": metrics.connection_errors,
            "avg_connection_time": metrics.avg_connection_time,
            "last_health_check": metrics.last_health_check.isoformat() if metrics.last_health_check else None,
        }
        
        return status

    async def get_session_details(self) -> list[dict[str, Any]]:
        """Get session connection details - Simplified Strategy (No session caching)"""
        # In simplified strategy, we don't maintain session connections
        # Return empty list as connections are managed by the pool directly
        return []

    async def generate_health_report(self) -> dict[str, Any]:
        """Generate connection health report - Simplified Strategy"""
        pool_status = await self.get_pool_status()
        
        # Calculate pool utilization
        pool_utilization = 1.0 - (pool_status["free_connections"] / pool_status["pool_size"]) if pool_status["pool_size"] > 0 else 0.0
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "pool_status": pool_status,
            "pool_utilization": pool_utilization,
            "recommendations": [],
        }
        
        # Add recommendations based on pool status
        if pool_status["connection_errors"] > 10:
            report["recommendations"].append("High connection error rate detected, review connection configuration")
        
        if pool_utilization > 0.9:
            report["recommendations"].append("Connection pool utilization is high, consider increasing pool size")
        
        if pool_status["free_connections"] == 0:
            report["recommendations"].append("No free connections available, consider increasing pool size")
        
        return report
