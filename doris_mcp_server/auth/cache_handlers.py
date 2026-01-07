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
Cache Management HTTP Handlers

Provides HTTP endpoints for cache management including viewing cache details,
clearing cache, statistics, and search functionality. All endpoints require
proper authentication and authorization.
"""

import json
from typing import Dict, Any

from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse

from ..utils.logger import get_logger
from ..utils.security import SecurityLevel
from ..utils.config import DorisConfig
from ..templates.cache_templates import CACHE_MANAGEMENT_HTML
from .token_security_middleware import TokenSecurityMiddleware


class CacheHandlers:
    """Cache Management HTTP Handlers"""
    
    def __init__(self, cache_manager, config: DorisConfig = None):
        self.cache_manager = cache_manager
        self.logger = get_logger(__name__)
        
        if config:
            self.security_middleware = TokenSecurityMiddleware(config)
        else:
            self.security_middleware = None
            self.logger.warning("Cache handlers initialized without security middleware - access control disabled")
    
    async def handle_get_cache_details(self, request: Request) -> JSONResponse:
        """Handle cache details request"""
        if self.security_middleware:
            security_response = await self.security_middleware.check_token_management_access(request)
            if security_response:
                return security_response
        
        try:
            include_values = request.query_params.get("include_values", "false").lower() == "true"
            cache_details = self.cache_manager.get_cache_details(include_values=include_values)
            return JSONResponse(cache_details)
            
        except Exception as e:
            self.logger.error(f"Error in handle_get_cache_details: {e}")
            return JSONResponse({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }, status_code=500)
    
    async def handle_get_cache_entry(self, request: Request) -> JSONResponse:
        """Handle single cache entry request"""
        if self.security_middleware:
            security_response = await self.security_middleware.check_token_management_access(request)
            if security_response:
                return security_response
        
        try:
            key = request.query_params.get("key")
            if not key:
                return JSONResponse({
                    "success": False,
                    "error": "key parameter is required"
                }, status_code=400)
            
            include_value = request.query_params.get("include_value", "true").lower() == "true"
            entry = self.cache_manager.get_cache_entry(key, include_value=include_value)
            return JSONResponse(entry)
            
        except Exception as e:
            self.logger.error(f"Error in handle_get_cache_entry: {e}")
            return JSONResponse({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }, status_code=500)
    
    async def handle_clear_cache(self, request: Request) -> JSONResponse:
        """Handle cache clearing request"""
        if self.security_middleware:
            security_response = await self.security_middleware.check_token_management_access(request)
            if security_response:
                return security_response
        
        try:
            if request.method == "GET":
                cache_type = request.query_params.get("cache_type")
                key = request.query_params.get("key")
                keys_param = request.query_params.get("keys")
                specific_keys = request.query_params.get("specific_keys")
                
                if key:
                    specific_keys = [key]
                elif specific_keys:
                    try:
                        specific_keys = json.loads(specific_keys)
                    except:
                        specific_keys = [specific_keys]
                elif keys_param:
                    try:
                        specific_keys = json.loads(keys_param)
                    except:
                        specific_keys = None
            else:
                cache_type = request.query_params.get("cache_type")
                key = request.query_params.get("key")
                keys_param = request.query_params.get("keys")
                specific_keys = request.query_params.get("specific_keys")
                
                body = None
                content_type = request.headers.get("content-type", "")
                
                if "application/json" in content_type:
                    try:
                        body = await request.json()
                        cache_type = body.get("cache_type")
                        specific_keys = body.get("specific_keys")
                    except:
                        pass
                
                if key:
                    specific_keys = [key]
                elif specific_keys:
                    try:
                        specific_keys = json.loads(specific_keys)
                    except:
                        specific_keys = [specific_keys]
                elif keys_param:
                    try:
                        specific_keys = json.loads(keys_param)
                    except:
                        specific_keys = None
            
            result = self.cache_manager.clear_cache(cache_type=cache_type, specific_keys=specific_keys)
            return JSONResponse(result)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return JSONResponse({
                "success": False,
                "error": f"Invalid JSON format for keys parameter: {str(e)}"
            }, status_code=400)
        except Exception as e:
            self.logger.error(f"Error in handle_clear_cache: {e}")
            return JSONResponse({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }, status_code=500)
    
    async def handle_get_cache_statistics(self, request: Request) -> JSONResponse:
        """Handle cache statistics request"""
        if self.security_middleware:
            security_response = await self.security_middleware.check_token_management_access(request)
            if security_response:
                return security_response
        
        try:
            stats = self.cache_manager.get_cache_statistics()
            return JSONResponse(stats)
            
        except Exception as e:
            self.logger.error(f"Error in handle_get_cache_statistics: {e}")
            return JSONResponse({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }, status_code=500)
    
    async def handle_search_cache(self, request: Request) -> JSONResponse:
        """Handle cache search request"""
        if self.security_middleware:
            security_response = await self.security_middleware.check_token_management_access(request)
            if security_response:
                return security_response
        
        try:
            pattern = request.query_params.get("pattern")
            if not pattern:
                return JSONResponse({
                    "success": False,
                    "error": "pattern parameter is required"
                }, status_code=400)
            
            result = self.cache_manager.search_cache_keys(pattern)
            return JSONResponse(result)
            
        except Exception as e:
            self.logger.error(f"Error in handle_search_cache: {e}")
            return JSONResponse({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }, status_code=500)
    
    async def handle_management_page(self, request: Request = None) -> HTMLResponse:
        """Handle cache management demo page"""
        if self.security_middleware:
            security_response = await self.security_middleware.check_token_management_access(request)
            if security_response:
                error_data = security_response.body.decode('utf-8') if hasattr(security_response, 'body') else '{"error": "Access denied"}'
                try:
                    error_info = json.loads(error_data)
                except:
                    error_info = {"error": "Access denied"}
                
                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Cache Management - Access Denied</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                        .container {{ background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); max-width: 600px; margin: 50px auto; }}
                        h1 {{ color: #333; }}
                        .error {{ color: #e74c3c; font-size: 18px; margin: 20px 0; }}
                        .btn {{ display: inline-block; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Cache Management - Access Denied</h1>
                        <div class="error">{error_info.get('error', 'You do not have permission to access this resource.')}</div>
                        <p>Please log in to access the cache management page.</p>
                        <a href="/auth/login" class="btn">Go to Login</a>
                    </div>
                </body>
                </html>
                """
                return HTMLResponse(error_html, status_code=security_response.status_code if hasattr(security_response, 'status_code') else 403)
        
        try:
            cache_details = self.cache_manager.get_cache_details(include_values=False)
            cache_stats = self.cache_manager.get_cache_statistics()
            
            if not cache_details.get("success"):
                error_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Cache Management - Not Available</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 50px; }
                        .error { color: red; font-size: 18px; }
                    </style>
                </head>
                <body>
                    <h1>Cache Management</h1>
                    <div class="error">Cache system is not available on this server.</div>
                </body>
                </html>
                """
                return HTMLResponse(error_html)
            
            stats = cache_details.get("statistics", {})
            summary = cache_details.get("cache_summary", {})
            entries = cache_details.get("cache_entries", [])
            
            enable_cache = getattr(self.cache_manager, 'enable_metadata_cache', True)
            cache_ttl = getattr(self.cache_manager, 'cache_ttl', 3600)
            recommendations = cache_stats.get('statistics', {}).get('recommendations', [])
            
            html_content = CACHE_MANAGEMENT_HTML
            html_content = html_content.replace('{enable_cache_status}', 'Enabled' if enable_cache else 'Disabled')
            html_content = html_content.replace('{enable_cache_class}', 'status-enabled' if enable_cache else 'status-disabled')
            html_content = html_content.replace('{cache_ttl}', str(cache_ttl))
            html_content = html_content.replace('{cache_ttl_minutes}', str(cache_ttl // 60))
            html_content = html_content.replace('{generated_at}', summary.get('generated_at', 'N/A'))
            html_content = html_content.replace('{valid_entries}', str(stats.get('valid_entries', 0)))
            html_content = html_content.replace('{expired_entries}', str(stats.get('expired_entries', 0)))
            html_content = html_content.replace('{total_entries}', str(summary.get('total_entries', 0)))
            html_content = html_content.replace('{cache_efficiency}', str(stats.get('cache_efficiency', 'N/A')))
            html_content = html_content.replace('{oldest_entry_age}', str(stats.get('oldest_entry_age', 0)))
            html_content = html_content.replace('{newest_entry_age}', str(stats.get('newest_entry_age', 0)))
            
            cache_types_html = ""
            for cache_type, count in summary.get('cache_types', {}).items():
                cache_types_html += f"""
                <div class="stat-item">
                    <div class="stat-value">{count}</div>
                    <div class="stat-label">{cache_type}</div>
                </div>
                """
            html_content = html_content.replace('{cache_types_html}', cache_types_html)
            
            recommendations_html = ""
            for rec in recommendations:
                rec_type = 'info'
                if 'Good' in rec:
                    rec_type = 'success'
                elif 'High' in rec or 'Large' in rec:
                    rec_type = 'warning'
                recommendations_html += f'<div class="recommendation {rec_type}">{rec}</div>'
            html_content = html_content.replace('{recommendations_html}', recommendations_html)
            
            entries_html = ""
            for entry in entries[:100]:
                cache_type = entry.get('cache_type', 'other')
                type_class = f'type-{cache_type}'
                status_class = 'expired' if entry.get('is_expired') else 'valid'
                status_text = 'Expired' if entry.get('is_expired') else 'Valid'
                key = entry.get('key', '')
                escaped_key = key.replace('"', '&quot;').replace("'", "\\'")
                key_display = key[:60] + '...' if len(key) > 60 else key
                
                entries_html += f"""
                <tr data-type="{cache_type}" data-status="{status_class}">
                    <td title="{escaped_key}">{key_display}</td>
                    <td><span class="cache-type-badge {type_class}">{cache_type}</span></td>
                    <td>{entry.get('hits', 0)}</td>
                    <td>{entry.get('age_human', 'N/A')}</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{entry.get('value_size', 0)} bytes</td>
                    <td>
                        <button class="btn-info btn-sm" onclick="viewEntry('{escaped_key}')" style="padding: 5px 10px; font-size: 12px;">Detail</button>
                        <button class="btn-danger btn-sm" onclick="deleteEntry('{escaped_key}')" style="padding: 5px 10px; font-size: 12px;">Delete</button>
                    </td>
                </tr>
                """
            html_content = html_content.replace('{entries_html}', entries_html)
            
            perf = cache_stats.get('statistics', {}).get('cache_performance', {})
            memory = perf.get('memory_usage', {})
            html_content = html_content.replace('{total_memory}', str(memory.get('total_size_human', 'N/A')))
            html_content = html_content.replace('{avg_entry_size}', str(memory.get('average_entry_size', 0)))
            html_content = html_content.replace('{hit_potential}', str(perf.get('hit_potential', 'N/A')))
            
            return HTMLResponse(html_content)
            
        except Exception as e:
            self.logger.error(f"Error in handle_management_page: {e}")
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Cache Management - Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 50px; }}
                    .error {{ color: red; font-size: 18px; }}
                </style>
            </head>
            <body>
                <h1>Cache Management - Error</h1>
                <div class="error">Internal server error: {str(e)}</div>
            </body>
            </html>
            """
            return HTMLResponse(error_html, status_code=500)
