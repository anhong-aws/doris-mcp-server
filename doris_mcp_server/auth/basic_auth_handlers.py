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
Basic Authentication HTTP Handlers
Provides simple username/password authentication for web UI
"""

import hashlib
import secrets
import time
from typing import Optional
from urllib.parse import parse_qs, urlparse

from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse, Response
from starlette.requests import Request

from ..utils.logger import get_logger

logger = get_logger(__name__)


class BasicAuthHandlers:
    """Simple username/password authentication handlers"""
    
    def __init__(self, config):
        """Initialize basic auth handlers
        
        Args:
            config: DorisConfig instance
        """
        self.config = config
        self._session_tokens = {}
        self._session_expiry_seconds = config.security.token_expiry if hasattr(config.security, 'token_expiry') else 3600
        logger.info("Basic auth handlers initialized")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password) == password_hash
    
    def _generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    def _create_session(self, username: str) -> str:
        """Create a new session and return token"""
        token = self._generate_session_token()
        self._session_tokens[token] = {
            "username": username,
            "created_at": time.time(),
            "expires_at": time.time() + self._session_expiry_seconds
        }
        logger.info(f"Session created for user: {username}")
        return token
    
    def _validate_session(self, token: str) -> Optional[dict]:
        """Validate session token and return session info if valid"""
        if not token or token not in self._session_tokens:
            return None
        
        session = self._session_tokens[token]
        if time.time() > session["expires_at"]:
            # Session expired, remove it
            del self._session_tokens[token]
            logger.info(f"Session expired for user: {session['username']}")
            return None
        
        return session
    
    def _destroy_session(self, token: str):
        """Destroy a session"""
        if token in self._session_tokens:
            username = self._session_tokens[token]["username"]
            del self._session_tokens[token]
            logger.info(f"Session destroyed for user: {username}")
    
    def _extract_session_token(self, request: Request) -> Optional[str]:
        """Extract session token from request"""
        
        # Try session cookie
        session_cookie = request.cookies.get('session_token')
        if session_cookie:
            return session_cookie
        
        # Try query parameter
        session_token = request.query_params.get('session_token')
        if session_token:
            return session_token
        
        # Try Authorization header last
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        elif auth_header.startswith('Session '):
            return auth_header[8:]
        
        return None
    
    def _verify_credentials(self, username: str, password: str) -> bool:
        """Verify username and password"""
        if not self.config.security.enable_basic_auth:
            return False
        
        # Verify username
        if username != self.config.security.basic_auth_username:
            return False
        
        # Verify password - check plain password first
        if self.config.security.basic_auth_password and password == self.config.security.basic_auth_password:
            return True
        
        # Check password hash if configured
        if self.config.security.basic_auth_password_hash:
            return self._verify_password(password, self.config.security.basic_auth_password_hash)
        
        # Fall back to plain password comparison
        return password == self.config.security.basic_auth_password
    
    async def handle_login_page(self, request: Request) -> HTMLResponse:
        """Show login page"""
        # Check if already logged in
        session_token = self._extract_session_token(request)
        if session_token and self._validate_session(session_token):
            return RedirectResponse(url="/", status_code=302)
        
        # Get redirect URL
        query_params = dict(request.query_params)
        redirect_url = query_params.get('redirect', '/')
        
        # Import template
        from ..templates.index_templates import LOGIN_PAGE_HTML
        
        # Show login page using template
        html_content = LOGIN_PAGE_HTML.format(redirect_url=redirect_url)
        response = HTMLResponse(html_content)
        response.headers.update({
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        })
        return response
    
    async def handle_login(self, request: Request) -> JSONResponse:
        """Handle login POST request"""
        try:
            # Get form data
            form_data = await request.form()
            username = form_data.get('username', '')
            password = form_data.get('password', '')
            
            # Fix: Always use a valid redirect URL, ignoring any invalid value from form
            redirect_url = '/index'
            
            logger.info(f"Login attempt received: username={username}, using redirect_url={redirect_url}")
            
            if not username or not password:
                return JSONResponse({
                    "success": False,
                    "error": "Username and password are required"
                }, status_code=400)
            
            # Verify credentials
            if not self._verify_credentials(username, password):
                logger.warning(f"Failed login attempt for user: {username}")
                return JSONResponse({
                    "success": False,
                    "error": "Invalid username or password"
                }, status_code=401)
            
            # Create session
            session_token = self._create_session(username)
            
            logger.info(f"User {username} logged in successfully, redirecting to {redirect_url}")
            
            return JSONResponse({
                "success": True,
                "session_token": session_token,
                "username": username,
                "redirect_url": redirect_url,
                "expires_in": self._session_expiry_seconds
            })
            
        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            return JSONResponse({
                "success": False,
                "error": f"Login failed: {str(e)}"
            }, status_code=500)
    
    async def handle_logout(self, request: Request) -> Response:
        """Handle logout request"""
        session_token = self._extract_session_token(request)
        if session_token:
            self._destroy_session(session_token)
        
        # Clear session cookie
        response = RedirectResponse(url="/ui/login/page", status_code=302)
        response.set_cookie('session_token', '', max_age=0, path='/')
        
        response.headers.update({
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        })
        
        return response
    
    async def handle_session_status(self, request: Request) -> JSONResponse:
        """Check current session status"""
        session_token = self._extract_session_token(request)
        
        if session_token:
            session = self._validate_session(session_token)
            if session:
                return JSONResponse({
                    "authenticated": True,
                    "username": session["username"],
                    "expires_in": int(session["expires_at"] - time.time())
                })
        
        return JSONResponse({
            "authenticated": False
        })
    
    def get_auth_info(self) -> dict:
        """Get authentication configuration info"""
        return {
            "basic_auth_enabled": self.config.security.enable_basic_auth,
            "username_configured": bool(self.config.security.basic_auth_username)
        }
