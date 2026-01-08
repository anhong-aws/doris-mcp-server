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
Index and Login Page Templates
HTML templates for dashboard and authentication pages
"""

INDEX_PAGE_DISABLED_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Doris MCP Server - Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #0066cc;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .header h1 {{ margin: 0; }}
        .card {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .card h2 {{ margin-top: 0; color: #333; }}
        .status {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 14px;
        }}
        .status-healthy {{
            background-color: #e6ffe6;
            color: #00cc00;
        }}
        .warning {{
            background-color: #fff3e6;
            padding: 15px;
            border-left: 4px solid #cc6600;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Apache Doris MCP Server</h1>
        <p>Enterprise Database Service - Dashboard</p>
    </div>
    
    <div class="card">
        <h2>Server Status</h2>
        <p><strong>Status:</strong> <span class="status status-healthy">Running</span></p>
        <p><strong>Server Name:</strong> doris-mcp-server</p>
        <p><strong>Version:</strong> {version}</p>
        <p><strong>Transport:</strong> HTTP (Streamable)</p>
    </div>
    
    <div class="card">
        <h2>Authentication</h2>
        <div class="warning">
            <strong>Warning:</strong> Basic authentication is not enabled.
            <br><br>
            To enable authentication, set the following environment variables:
            <ul>
                <li><code>ENABLE_BASIC_AUTH=true</code></li>
                <li><code>BASIC_AUTH_USERNAME=admin</code></li>
                <li><code>BASIC_AUTH_PASSWORD=your_password</code></li>
            </ul>
        </div>
    </div>
    
    <div class="card">
        <h2>Quick Links</h2>
        <p><a href="/token/management">Token Management</a></p>
        <p><a href="/cache/management">Cache Management</a></p>
        <p><a href="/logs/management">MCP Log Management</a></p>
        <p><a href="/auth/demo">OAuth Demo</a></p>
    </div>
</body>
</html>
"""

INDEX_PAGE_ENABLED_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Doris MCP Server - Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #0066cc;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .header h1 {{ margin: 0; }}
        .card {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .card h2 {{ margin-top: 0; color: #333; }}
        .info-item {{
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        .info-item:last-child {{ border-bottom: none; }}
        .label {{ font-weight: bold; color: #666; }}
        .status {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 14px;
        }}
        .status-healthy {{
            background-color: #e6ffe6;
            color: #00cc00;
        }}
        .nav-links {{ margin-top: 20px; }}
        .nav-links a {{
            display: inline-block;
            margin-right: 15px;
            padding: 10px 20px;
            background-color: #0066cc;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }}
        .nav-links a:hover {{ background-color: #0052a3; }}
        .logout-btn {{ background-color: #cc0000 !important; }}
        .logout-btn:hover {{ background-color: #a30000 !important; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Apache Doris MCP Server</h1>
        <p>Enterprise Database Service - Dashboard</p>
    </div>
    
    <div class="card">
        <h2>Server Status</h2>
        <div class="info-item">
            <span class="label">Status:</span>
            <span class="status status-healthy">Healthy</span>
        </div>
        <div class="info-item">
            <span class="label">Server Name:</span>
            <span class="value">doris-mcp-server</span>
        </div>
        <div class="info-item">
            <span class="label">Version:</span>
            <span class="value">{version}</span>
        </div>
        <div class="info-item">
            <span class="label">Transport:</span>
            <span class="value">HTTP (Streamable)</span>
        </div>
    </div>
    
    <div class="card">
        <h2>Authentication Info</h2>
        <div class="info-item">
            <span class="label">Username:</span>
            <span class="value">{username}</span>
        </div>
        <div class="info-item">
            <span class="label">Session Status:</span>
            <span class="status status-healthy">Active</span>
        </div>
    </div>
    
    <div class="card">
        <h2>Quick Links</h2>
        <div class="info-item">
            <span class="label">Token Management:</span>
            <span class="value"><a href="/token/management">Manage Tokens</a></span>
        </div>
        <div class="info-item">
            <span class="label">Cache Management:</span>
            <span class="value"><a href="/cache/management">Manage Cache</a></span>
        </div>
        <div class="info-item">
            <span class="label">MCP Log Management:</span>
            <span class="value"><a href="/logs/management">View MCP Logs</a></span>
        </div>
        <div class="info-item">
            <span class="label">API Endpoints:</span>
            <span class="value">/mcp (MCP Protocol)</span>
        </div>
    </div>
    
    <div class="nav-links">
        <a href="/token/management">Token Management</a>
        <a href="/cache/management">Cache Management</a>
        <a href="/logs/management">MCP Log Management</a>
        <a href="/auth/demo">OAuth Demo</a>
        <a href="/ui/logout" class="logout-btn">Logout</a>
    </div>
</body>
</html>
"""

LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - Doris MCP Server</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 400px;
            margin: 100px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .login-card {{
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .login-card h1 {{
            margin-top: 0;
            color: #333;
            text-align: center;
        }}
        .login-card p {{
            color: #666;
            text-align: center;
            margin-bottom: 30px;
        }}
        .form-group {{
            margin-bottom: 20px;
        }}
        .form-group label {{
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: bold;
        }}
        .form-group input {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            box-sizing: border-box;
        }}
        .form-group input:focus {{
            outline: none;
            border-color: #0066cc;
        }}
        .submit-btn {{
            width: 100%;
            padding: 12px;
            background-color: #0066cc;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
        }}
        .submit-btn:hover {{
            background-color: #0052a3;
        }}
        .error {{
            background-color: #ffe6e6;
            color: #cc0000;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .server-info {{
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="login-card">
        <h1>Doris MCP Server</h1>
        <p>Please sign in to continue</p>
        
        <div id="error" class="error" style="display: none;"></div>
        
        <form id="loginForm" method="POST" action="/ui/login">
            <input type="hidden" name="redirect" value="{redirect_url}">
            
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autofocus>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="submit-btn">Sign In</button>
        </form>
        
        <div class="server-info">
            Apache Doris MCP Server
        </div>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            const formData = new FormData(this);
            const errorDiv = document.getElementById('error');
            
            try {{
                const response = await fetch('/ui/login', {{
                    method: 'POST',
                    body: formData
                }});
                const data = await response.json();
                if (response.ok && data.success) {{
                    document.cookie = 'session_token=' + data.session_token + '; path=/; max-age=' + data.expires_in + '; SameSite=Lax';
                    window.location.href = data.redirect_url || '/';
                }} else {{
                    errorDiv.textContent = data.error || 'Login failed';
                    errorDiv.style.display = 'block';
                }}
            }} catch (error) {{
                errorDiv.textContent = 'Network error: ' + error.message;
                errorDiv.style.display = 'block';
            }}
        }});
        
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('error')) {{
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = urlParams.get('error');
            errorDiv.style.display = 'block';
        }}
    </script>
</body>
</html>
"""
