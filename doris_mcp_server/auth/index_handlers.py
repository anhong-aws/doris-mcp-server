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
Index Page Handlers
Handles dashboard and authentication page requests
"""

import os
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request

from ..templates.index_templates import INDEX_PAGE_DISABLED_HTML, INDEX_PAGE_ENABLED_HTML, LOGIN_PAGE_HTML
from ..utils.logger import get_logger

logger = get_logger(__name__)


class IndexHandlers:
    """Handlers for index/dashboard pages"""
    
    def __init__(self, config, basic_auth_handlers):
        """Initialize index handlers
        
        Args:
            config: DorisConfig instance
            basic_auth_handlers: BasicAuthHandlers instance for session management
        """
        self.config = config
        self.basic_auth_handlers = basic_auth_handlers
        self._default_version = "0.4.1"
        logger.info("Index handlers initialized")
    
    def _get_version(self) -> str:
        """Get server version"""
        return os.getenv("SERVER_VERSION", self._default_version)
    
    async def handle_index_page(self, request: Request) -> HTMLResponse:
        """Handle index/dashboard page request"""
        if not self.config.security.enable_basic_auth:
            html_content = INDEX_PAGE_DISABLED_HTML.format(
                version=self._get_version()
            )
            return HTMLResponse(html_content)
        
        session_token = self.basic_auth_handlers._extract_session_token(request)
        
        if not session_token:
            return RedirectResponse(url="/ui/login/page", status_code=302)
        
        session = self.basic_auth_handlers._validate_session(session_token)
        
        if not session:
            return RedirectResponse(url="/ui/login/page", status_code=302)
        
        html_content = INDEX_PAGE_ENABLED_HTML.format(
            version=self._get_version(),
            username=session["username"]
        )
        return HTMLResponse(html_content)
    
    async def handle_login_page(self, request: Request) -> HTMLResponse:
        """Handle login page request"""
        session_token = self.basic_auth_handlers._extract_session_token(request)
        if session_token and self.basic_auth_handlers._validate_session(session_token):
            return RedirectResponse(url="/", status_code=302)
        
        query_params = dict(request.query_params)
        redirect_url = query_params.get('redirect', '/')
        
        html_content = LOGIN_PAGE_HTML.format(
            redirect_url=redirect_url
        )
        return HTMLResponse(html_content)
