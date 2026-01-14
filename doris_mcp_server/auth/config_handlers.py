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
Configuration Management Handlers
Provides configuration viewing and editing functionality
"""

import json
import logging
from datetime import datetime
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from ..templates.config_templates import CONFIG_MANAGEMENT_HTML
from ..utils.config import DorisConfig
from .token_security_middleware import TokenSecurityMiddleware

logger = logging.getLogger(__name__)


class ConfigHandlers:
    """Configuration management handlers"""

    def __init__(self, config: DorisConfig, basic_auth_handlers: Any):
        """Initialize config handlers

        Args:
            config: DorisConfig instance
            basic_auth_handlers: BasicAuthHandlers instance for authentication
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Create security middleware for authentication
        self.security_middleware = TokenSecurityMiddleware(config, basic_auth_handlers)
        self.logger.info("Config handlers initialized with security middleware")

    async def handle_config_management_page(self, request: Request) -> Response:
        """Handle configuration management page request

        Args:
            request: Starlette Request object

        Returns:
            HTML response with configuration management page
        """
        self.logger.info("Handling configuration management page request")

        # Check authentication using security middleware
        security_response = await self.security_middleware.check_token_management_access(request)
        if security_response:
            return security_response

        # Get current configuration
        config_details = self.config.to_dict()

        # Generate HTML for basic configuration
        basic_config_html = self._generate_config_html_section(config_details, [
            ("server_name", "Server Name"),
            ("server_version", "Server Version"),
            ("server_port", "Server Port"),
            ("temp_files_dir", "Temporary Files Directory"),
        ])

        # Generate HTML for database configuration
        database_config_html = self._generate_config_html_section(config_details["database"], [
            ("host", "Host"),
            ("port", "Port"),
            ("user", "User"),
            ("password", "Password", True),
            ("database", "Database"),
            ("charset", "Charset"),
            ("fe_http_port", "FE HTTP Port"),
            ("be_hosts", "BE Hosts"),
            ("fe_arrow_flight_sql_port", "FE Arrow Flight SQL Port"),
            ("be_arrow_flight_sql_port", "BE Arrow Flight SQL Port"),
            ("max_connections", "Max Connections"),
            ("connection_timeout", "Connection Timeout"),
            ("health_check_interval", "Health Check Interval"),
            ("max_connection_age", "Max Connection Age"),
        ])

        # Generate HTML for security configuration
        security_config_html = self._generate_config_html_section(config_details["security"], [
            ("auth_type", "Authentication Type"),
            ("enable_token_auth", "Enable Token Auth"),
            ("enable_jwt_auth", "Enable JWT Auth"),
            ("enable_oauth_auth", "Enable OAuth Auth"),
            ("enable_basic_auth", "Enable Basic Auth"),
            ("enable_security_check", "Enable Security Check"),
            ("enable_masking", "Enable Masking"),
            ("max_result_rows", "Max Result Rows"),
            ("max_query_complexity", "Max Query Complexity"),
            ("blocked_keywords", "Blocked Keywords"),
        ])

        # Generate HTML for performance configuration
        performance_config_html = self._generate_config_html_section(config_details["performance"], [
            ("enable_query_cache", "Enable Query Cache"),
            ("enable_metadata_cache", "Enable Metadata Cache"),
            ("cache_ttl", "Cache TTL"),
            ("max_cache_size", "Max Cache Size"),
            ("max_concurrent_queries", "Max Concurrent Queries"),
            ("query_timeout", "Query Timeout"),
            ("max_response_content_size", "Max Response Content Size"),
            ("table_filter_include", "Table Filter Include"),
            ("table_filter_exclude", "Table Filter Exclude"),
            ("column_filter_exclude", "Column Filter Exclude"),
        ])

        # Generate HTML for logging configuration
        logging_config_html = self._generate_config_html_section(config_details["logging"], [
            ("level", "Log Level"),
            ("file_path", "Log File Path"),
            ("enable_audit", "Enable Audit"),
            ("audit_file_path", "Audit File Path"),
            ("enable_cleanup", "Enable Log Cleanup"),
            ("max_age_days", "Max Log Age (days)"),
            ("cleanup_interval_hours", "Cleanup Interval (hours)"),
        ])

        # Generate HTML for monitoring configuration
        monitoring_config_html = self._generate_config_html_section(config_details["monitoring"], [
            ("enable_metrics", "Enable Metrics"),
            ("metrics_port", "Metrics Port"),
            ("metrics_path", "Metrics Path"),
            ("health_check_port", "Health Check Port"),
            ("health_check_path", "Health Check Path"),
            ("enable_alerts", "Enable Alerts"),
            ("alert_webhook_url", "Alert Webhook URL"),
        ])

        # Generate HTML for ADBC configuration
        adbc_config_html = self._generate_config_html_section(config_details["adbc"], [
            ("default_max_rows", "Default Max Rows"),
            ("default_timeout", "Default Timeout"),
            ("default_return_format", "Default Return Format"),
            ("connection_timeout", "Connection Timeout"),
            ("enabled", "ADBC Enabled"),
        ])

        # Generate HTML for data quality configuration
        data_quality_config_html = self._generate_config_html_section(config_details["data_quality"], [
            ("max_columns_per_batch", "Max Columns Per Batch"),
            ("default_sample_size", "Default Sample Size"),
            ("small_table_threshold", "Small Table Threshold"),
            ("medium_table_threshold", "Medium Table Threshold"),
            ("enable_batch_analysis", "Enable Batch Analysis"),
            ("batch_timeout", "Batch Timeout"),
            ("enable_fast_mode", "Enable Fast Mode"),
            ("fast_mode_sample_size", "Fast Mode Sample Size"),
            ("enable_distribution_analysis", "Enable Distribution Analysis"),
            ("histogram_bins", "Histogram Bins"),
        ])

        # Get .env file content and path
        env_file_content = self.config.load_env_file_content()
        env_file_path = self.config.get_env_file_path()

        # Generate HTML response
        html = CONFIG_MANAGEMENT_HTML
        html = html.replace('{basic_config_html}', basic_config_html)
        html = html.replace('{database_config_html}', database_config_html)
        html = html.replace('{security_config_html}', security_config_html)
        html = html.replace('{performance_config_html}', performance_config_html)
        html = html.replace('{logging_config_html}', logging_config_html)
        html = html.replace('{monitoring_config_html}', monitoring_config_html)
        html = html.replace('{adbc_config_html}', adbc_config_html)
        html = html.replace('{data_quality_config_html}', data_quality_config_html)
        html = html.replace('{env_file_content}', env_file_content)
        html = html.replace('{env_file_path}', env_file_path)
        html = html.replace('{generated_at}', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        return Response(html, media_type="text/html")

    async def handle_get_config_details(self, request: Request) -> JSONResponse:
        """Handle get configuration details request

        Args:
            request: Starlette Request object

        Returns:
            JSON response with configuration details
        """
        self.logger.info("Handling get configuration details request")

        # Check authentication using security middleware
        security_response = await self.security_middleware.check_token_management_access(request)
        if security_response:
            return security_response

        # Get current configuration
        config_details = self.config.to_dict()

        return JSONResponse({
            "success": True,
            "config": config_details
        })

    async def handle_get_env_content(self, request: Request) -> JSONResponse:
        """Handle get .env file content request

        Args:
            request: Starlette Request object

        Returns:
            JSON response with .env file content
        """
        self.logger.info("Handling get .env file content request")

        # Check authentication using security middleware
        security_response = await self.security_middleware.check_token_management_access(request)
        if security_response:
            return security_response

        # Get .env file content and path
        env_file_content = self.config.load_env_file_content()
        env_file_path = self.config.get_env_file_path()

        return JSONResponse({
            "success": True,
            "content": env_file_content,
            "path": env_file_path
        })

    async def handle_save_env_file(self, request: Request) -> JSONResponse:
        """Handle save .env file request

        Args:
            request: Starlette Request object

        Returns:
            JSON response with save result
        """
        self.logger.info("Handling save .env file request")

        # Check authentication using security middleware
        security_response = await self.security_middleware.check_token_management_access(request)
        if security_response:
            return security_response

        try:
            # Parse request body
            request_body = await request.json()
            new_content = request_body.get("content", "")

            if not isinstance(new_content, str):
                logger.error("Invalid content type received for .env file")
                return JSONResponse(
                    {"success": False, "message": "Invalid content type"},
                    status_code=400
                )

            # Save content to .env file
            save_result = self.config.save_to_env(new_content)

            if save_result:
                logger.info(".env file saved successfully")
                return JSONResponse({
                    "success": True,
                    "message": ".env file saved successfully",
                    "backup_created": True
                })
            else:
                logger.error("Failed to save .env file")
                return JSONResponse(
                    {"success": False, "message": "Failed to save .env file"},
                    status_code=500
                )
        except json.JSONDecodeError:
            logger.error("Invalid JSON received in request")
            return JSONResponse(
                {"success": False, "message": "Invalid JSON format"},
                status_code=400
            )
        except Exception as e:
            logger.error(f"Error saving .env file: {e}")
            return JSONResponse(
                {"success": False, "message": f"Error saving .env file: {str(e)}"},
                status_code=500
            )

    def _generate_config_html_section(self, config_dict: dict, fields: list) -> str:
        """Generate HTML for a configuration section

        Args:
            config_dict: Dictionary containing configuration values
            fields: List of tuples (key, label, is_sensitive=False)

        Returns:
            HTML string for the configuration section
        """
        html = ""
        for field_info in fields:
            key = field_info[0]
            label = field_info[1]
            is_sensitive = len(field_info) > 2 and field_info[2]

            value = config_dict.get(key, "")
            if is_sensitive:
                display_value = "***"
            else:
                display_value = value

            html += f"""
            <div class="config-item">
                <div class="config-label">{label}</div>
                <div class="config-value {is_sensitive and 'sensitive-value' or ''}">{display_value}</div>
            </div>
            """

        return html
