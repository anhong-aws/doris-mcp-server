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
MCP Log Management HTTP Handlers
Provides HTTP endpoints for MCP log management and visualization
"""

import json
from typing import Dict, Any
from datetime import datetime

from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse

from ..utils.logger import get_logger
from ..utils.mcp_log_reader import MCPLogReader
from ..templates.mcp_log_templates import MCP_LOG_MANAGEMENT_HTML
from .token_security_middleware import TokenSecurityMiddleware


class MCPLogHandlers:
    """MCP Log Management HTTP Handlers"""
    
    def __init__(self, config = None, basic_auth_handlers = None):
        """Initialize MCP Log Handlers"""
        self.logger = get_logger(__name__)
        self.log_reader = MCPLogReader()
        
        if config:
            self.security_middleware = TokenSecurityMiddleware(config, basic_auth_handlers)
        else:
            self.security_middleware = None
            self.logger.warning("MCP log handlers initialized without security middleware - access control disabled")
    
    async def handle_get_logs(self, request: Request) -> JSONResponse:
        """Handle logs list request
        
        Endpoint: GET /logs/content
        """
        # Check security middleware if available
        if self.security_middleware:
            security_response = await self.security_middleware.check_token_management_access(request)
            if security_response:
                return security_response
        
        try:
            # Parse query parameters
            days = int(request.query_params.get("days", "7"))
            limit = int(request.query_params.get("limit", "100"))
            method = request.query_params.get("method")
            search = request.query_params.get("search")
            
            # Get logs from reader
            logs_result = self.log_reader.get_logs(
                days=days,
                limit=limit,
                method=method,
                search=search
            )
            
            return JSONResponse(logs_result)
            
        except Exception as e:
            self.logger.error(f"Error in handle_get_logs: {e}")
            return JSONResponse({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }, status_code=500)
    
    async def handle_get_log_stats(self, request: Request) -> JSONResponse:
        """Handle log statistics request
        
        Endpoint: GET /mcp/logs/stats
        """
        # Check security middleware if available
        if self.security_middleware:
            security_response = await self.security_middleware.check_token_management_access(request)
            if security_response:
                return security_response
        
        try:
            # Parse query parameters
            days = int(request.query_params.get("days", "7"))
            
            # Get call statistics
            call_stats = self.log_reader.get_call_statistics(days=days)
            daily_stats = self.log_reader.get_daily_stats(days=days)
            
            return JSONResponse({
                "success": True,
                "call_stats": call_stats,
                "daily_stats": daily_stats
            })
            
        except Exception as e:
            self.logger.error(f"Error in handle_get_log_stats: {e}")
            return JSONResponse({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }, status_code=500)
    
    async def handle_log_management_page(self, request: Request) -> HTMLResponse:
        """Handle log management page request
        
        Endpoint: GET /mcp/logs/management
        """
        # Check security middleware if available
        if self.security_middleware:
            security_response = await self.security_middleware.check_token_management_access(request)
            if security_response:
                # Return access denied page
                error_data = security_response.body.decode('utf-8') if hasattr(security_response, 'body') else '{}'
                try:
                    error_info = json.loads(error_data)
                except:
                    error_info = {"error": "Access denied"}
                
                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>MCP Log Management - Access Denied</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; color: white; }}
                        .container {{ background: white; color: black; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); max-width: 600px; }}
                        h1 {{ color: #333; }}
                        .error {{ color: #e74c3c; font-size: 18px; margin: 20px 0; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>MCP Log Management - Access Denied</h1>
                        <div class="error">{error_info.get('error', 'You do not have permission to access this resource.')}</div>
                        <p>Please log in to access the log management page.</p>
                    </div>
                </body>
                </html>
                """
                return HTMLResponse(error_html, status_code=security_response.status_code if hasattr(security_response, 'status_code') else 403)
        
        try:
            # Parse query parameters
            days = int(request.query_params.get("days", "7"))
            limit = int(request.query_params.get("limit", "100"))
            method = request.query_params.get("method")
            search = request.query_params.get("search")
            
            # Get log data
            logs_result = self.log_reader.get_logs(
                days=days,
                limit=limit,
                method=method,
                search=search
            )
            
            if not logs_result["success"]:
                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>MCP Log Management - Error</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; color: white; }}
                        .container {{ background: white; color: black; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); max-width: 600px; }}
                        h1 {{ color: #333; }}
                        .error {{ color: #e74c3c; font-size: 18px; margin: 20px 0; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>MCP Log Management - Error</h1>
                        <div class="error">{logs_result['error']}</div>
                    </div>
                </body>
                </html>
                """
                return HTMLResponse(error_html, status_code=500)
            
            # Get statistics
            call_stats = self.log_reader.get_call_statistics(days=days)
            daily_stats = self.log_reader.get_daily_stats(days=days)
            log_file_info = self.log_reader.get_log_file_info()
            
            # Prepare template data
            logs = logs_result["logs"]
            total_logs = len(logs)
            displayed_logs = min(total_logs, limit)
            
            # Generate method options for filter
            method_options = []
            all_methods = set()
            for log in logs:
                all_methods.add(log["method"])
            for stat_method in call_stats.get("method_totals", {}).keys():
                all_methods.add(stat_method)
            for method_name in sorted(all_methods):
                selected = "selected" if method == method_name else ""
                method_options.append(f"<option value='{method_name}' {selected}>{method_name}</option>")
            method_options_html = "\n".join(method_options)
            
            # Generate log rows
            logs_rows = []
            for log in logs:
                session_id = log.get('mcp_session_id', '')
                logs_rows.append(f"""
                <tr data-method="{log['method']}">
                    <td>{log['timestamp']}</td>
                    <td><span class="method-badge">{log['method']}</span></td>
                    <td><div class="arguments">{json.dumps(log['arguments'], ensure_ascii=False)}</div></td>
                    <td>{session_id}</td>
                </tr>
                """)
            logs_rows_html = "\n".join(logs_rows)
            
            # Generate chart data
            method_stats_json = json.dumps(call_stats.get("method_totals", {}), ensure_ascii=False)
            daily_stats_json = json.dumps(daily_stats.get("daily_counts", {}), ensure_ascii=False)
            logs_json = json.dumps(logs[:100], ensure_ascii=False)  # Limit for initial load
            
            # Calculate total calls
            total_calls = sum(call_stats.get("method_totals", {}).values())
            
            # Get recent calls (last 24h)
            recent_calls = daily_stats.get("daily_counts", {}).get(datetime.now().strftime('%Y-%m-%d'), 0)
            
            # Format template
            html_content = MCP_LOG_MANAGEMENT_HTML
            html_content = html_content.replace('{log_file_path}', log_file_info.get('file_path', ''))
            html_content = html_content.replace('{log_file_size_human}', log_file_info.get('file_size_human', '0 KB'))
            html_content = html_content.replace('{log_created_at}', log_file_info.get('created_at', 'N/A'))
            html_content = html_content.replace('{log_modified_at}', log_file_info.get('modified_at', 'N/A'))
            html_content = html_content.replace('{total_methods}', str(len(all_methods)))
            html_content = html_content.replace('{total_calls}', str(total_calls))
            html_content = html_content.replace('{recent_calls}', str(recent_calls))
            html_content = html_content.replace('{method_options}', method_options_html)
            html_content = html_content.replace('{displayed_logs}', str(displayed_logs))
            html_content = html_content.replace('{total_logs}', str(total_logs))
            html_content = html_content.replace('{logs_rows}', logs_rows_html)
            html_content = html_content.replace('{method_stats_json}', method_stats_json)
            html_content = html_content.replace('{daily_stats_json}', daily_stats_json)
            html_content = html_content.replace('{logs_json}', logs_json)
            html_content = html_content.replace('{generated_at}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            return HTMLResponse(html_content)
            
        except Exception as e:
            self.logger.error(f"Error in handle_log_management_page: {e}")
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>MCP Log Management - Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; color: white; }}
                    .container {{ background: white; color: black; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); max-width: 600px; }}
                    h1 {{ color: #333; }}
                    .error {{ color: #e74c3c; font-size: 18px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>MCP Log Management - Error</h1>
                    <div class="error">Internal server error: {str(e)}</div>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(error_html, status_code=500)