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
Database Connection Pool Handlers
Handles connection pool monitoring and management requests
"""

from starlette.responses import HTMLResponse, JSONResponse
from starlette.requests import Request

from ..templates.db_templates import DB_MANAGEMENT_PAGE_HTML
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DBHandlers:
    """Handlers for database connection pool management"""
    
    def __init__(self, connection_manager, basic_auth_handlers):
        """Initialize DB handlers
        
        Args:
            connection_manager: DorisConnectionManager instance
            basic_auth_handlers: BasicAuthHandlers instance for session management
        """
        self.connection_manager = connection_manager
        self.basic_auth_handlers = basic_auth_handlers
        logger.info("DB handlers initialized")
    
    async def handle_db_management_page(self, request: Request) -> HTMLResponse:
        """Handle database management page request"""
        # Check authentication if basic auth is enabled
        if self.basic_auth_handlers and self.basic_auth_handlers.config.security.enable_basic_auth:
            session_token = self.basic_auth_handlers._extract_session_token(request)
            if not session_token:
                from starlette.responses import RedirectResponse
                return RedirectResponse(url="/ui/login/page", status_code=302)
            
            session = self.basic_auth_handlers._validate_session(session_token)
            if not session:
                from starlette.responses import RedirectResponse
                return RedirectResponse(url="/ui/login/page", status_code=302)
        
        return HTMLResponse(DB_MANAGEMENT_PAGE_HTML)
    
    async def handle_get_db_status(self, request: Request) -> JSONResponse:
        """Handle connection pool status request"""
        try:
            # Get connection pool status
            status = await self._get_db_status()
            return JSONResponse({"success": True, "data": status})
        except Exception as e:
            logger.error(f"Failed to get DB status: {e}")
            return JSONResponse({"success": False, "error": str(e)})
    
    async def handle_test_connection(self, request: Request) -> JSONResponse:
        """Handle connection test request"""
        try:
            result = await self.connection_manager.test_connection()
            if result:
                return JSONResponse({"success": True, "message": "Connection test successful"})
            else:
                return JSONResponse({"success": False, "error": "Connection test failed"})
        except Exception as e:
            logger.error(f"Failed to test connection: {e}")
            return JSONResponse({"success": False, "error": str(e)})
    
    async def handle_refresh_pool(self, request: Request) -> JSONResponse:
        """Handle refresh pool request"""
        try:
            # Refresh pool by recreating it
            await self.connection_manager._recreate_pool()
            return JSONResponse({"success": True, "message": "Connection pool refreshed successfully"})
        except Exception as e:
            logger.error(f"Failed to refresh pool: {e}")
            return JSONResponse({"success": False, "error": str(e)})
    
    async def handle_close_all_connections(self, request: Request) -> JSONResponse:
        """Handle close all connections request"""
        try:
            # Close all connections and recreate pool
            await self.connection_manager._recreate_pool()
            return JSONResponse({"success": True, "message": "All connections closed successfully"})
        except Exception as e:
            logger.error(f"Failed to close all connections: {e}")
            return JSONResponse({"success": False, "error": str(e)})
    
    async def handle_recreate_pool(self, request: Request) -> JSONResponse:
        """Handle recreate pool request"""
        try:
            # Recreate pool - this will close all existing connections and create new ones
            await self.connection_manager._recreate_pool()
            return JSONResponse({"success": True, "message": "Connection pool recreated successfully"})
        except Exception as e:
            logger.error(f"Failed to recreate pool: {e}")
            return JSONResponse({"success": False, "error": str(e)})
    
    async def handle_release_session(self, request: Request) -> JSONResponse:
        """Handle release session request"""
        try:
            session_id = request.path_params.get("session_id")
            if not session_id:
                return JSONResponse({"success": False, "error": "Session ID is required"})
            
            # Get session connection
            session_conn = self.connection_manager.session_cache.get(session_id)
            if session_conn:
                await self.connection_manager.release_connection(session_id, session_conn)
                return JSONResponse({"success": True, "message": f"Session {session_id} released successfully"})
            else:
                return JSONResponse({"success": False, "error": f"Session {session_id} not found"})
        except Exception as e:
            logger.error(f"Failed to release session: {e}")
            return JSONResponse({"success": False, "error": str(e)})
    
    async def handle_get_all_connections(self, request: Request) -> JSONResponse:
        """Handle get all connections request"""
        try:
            # Get all connections
            connections = await self.connection_manager.get_all_connections()
            return JSONResponse({"success": True, "data": connections})
        except Exception as e:
            logger.error(f"Failed to get all connections: {e}")
            return JSONResponse({"success": False, "error": str(e)})
    
    async def _get_db_status(self) -> dict:
        """Get detailed database connection pool status"""
        try:
            # Get pool metrics
            metrics = await self.connection_manager.get_metrics()
            
            # Get pool diagnosis
            diagnosis = await self.connection_manager.diagnose_connection_health()
            
            # Get session details
            sessions = self.connection_manager.session_cache.get_all_sessions()
            
            # Calculate pool status
            pool_status = "healthy"
            if not self.connection_manager.pool or self.connection_manager.pool.closed:
                pool_status = "unhealthy"
            elif diagnosis.get("pool_health") == "unhealthy":
                pool_status = "unhealthy"
            elif metrics.failed_connections > 0 or metrics.connection_errors > 0:
                pool_status = "warning"
            
            # Build diagnosis list
            diagnosis_list = []
            if not self.connection_manager.pool:
                diagnosis_list.append({
                    "title": "Pool Not Initialized",
                    "description": "Connection pool has not been initialized",
                    "type": "error",
                    "recommendation": "Initialize the connection pool"
                })
            elif self.connection_manager.pool.closed:
                diagnosis_list.append({
                    "title": "Pool Closed",
                    "description": "Connection pool is closed",
                    "type": "error",
                    "recommendation": "Recreate the connection pool"
                })
            
            # Add detailed pool status
            if self.connection_manager.pool:
                pool_size = self.connection_manager.pool.size
                free_size = self.connection_manager.pool.freesize
                utilization = 100 - (free_size / pool_size * 100) if pool_size > 0 else 0
                diagnosis_list.append({
                    "title": "Pool Status",
                    "description": f"Size: {pool_size}, Free: {free_size}, Utilization: {utilization:.1f}%",
                    "type": "info"
                })
            
            # Add recommendations from diagnosis
            if diagnosis.get("recommendations"):
                for rec in diagnosis["recommendations"]:
                    diagnosis_list.append({
                        "title": "Pool Recommendation",
                        "description": rec,
                        "type": "warning",
                        "recommendation": rec
                    })
            
            # Add error analysis if available
            error_analysis = diagnosis.get("error_analysis", {})
            if error_analysis.get("error_count", 0) > 0:
                error_count = error_analysis["error_count"]
                last_error_time = error_analysis.get("last_error_time")
                
                diagnosis_list.append({
                    "title": "Error Summary",
                    "description": f"Total errors: {error_count}. Last error: {last_error_time if last_error_time else 'Unknown'}",
                    "type": "error"
                })
                
                # Add error types
                error_types = error_analysis.get("error_types", {})
                if error_types:
                    error_type_desc = "; ".join([f"{t}: {c}" for t, c in error_types.items()])
                    diagnosis_list.append({
                        "title": "Error Types",
                        "description": error_type_desc,
                        "type": "warning"
                    })
                
                # Add recent errors
                recent_errors = error_analysis.get("recent_errors", [])
                if recent_errors:
                    for error in recent_errors[:3]:  # Show max 3 recent errors
                        diagnosis_list.append({
                            "title": f"Recent Error ({error['type']})",
                            "description": f"{error['message']}\nTimestamp: {error['timestamp']}",
                            "type": "error"
                        })
            
            # Build session list
            session_list = []
            for session_id, conn in sessions.items():
                session_list.append({
                    "session_id": session_id,
                    "status": "healthy" if conn.is_healthy else "unhealthy",
                    "created_at": conn.created_at.isoformat() if hasattr(conn, 'created_at') else "-" ,
                    "last_used": conn.last_used.isoformat() if hasattr(conn, 'last_used') else "-",
                    "query_count": conn.query_count if hasattr(conn, 'query_count') else 0
                })
            
            # Build status response
            status = {
                "pool_status": pool_status,
                "pool_size": self.connection_manager.pool.size if self.connection_manager.pool else 0,
                "active_connections": metrics.active_connections,
                "idle_connections": metrics.idle_connections,
                "max_connections": self.connection_manager.maxsize,
                "failed_connections": metrics.failed_connections,
                "connection_errors": metrics.connection_errors,
                "avg_connection_time": metrics.avg_connection_time * 1000,  # Convert to ms
                "acquisition_timeouts": metrics.acquisition_timeouts,  # Use actual acquisition timeouts
                "query_timeouts": metrics.query_timeouts,  # Use actual query timeouts
                "sessions": session_list,
                "diagnosis": diagnosis_list
            }
            
            return status
        except Exception as e:
            logger.error(f"Failed to get DB status: {e}")
            return {
                "pool_status": "unknown",
                "pool_size": 0,
                "active_connections": 0,
                "idle_connections": 0,
                "max_connections": self.connection_manager.maxsize,
                "failed_connections": 0,
                "connection_errors": 0,
                "avg_connection_time": 0,
                "acquisition_timeouts": 0,
                "query_timeouts": 0,
                "sessions": [],
                "diagnosis": [{"title": "Error", "description": str(e), "type": "error"}]
            }
