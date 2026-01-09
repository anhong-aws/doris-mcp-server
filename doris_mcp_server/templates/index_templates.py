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
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }}
        
        body::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                radial-gradient(circle at 25% 25%, rgba(255,255,255,0.1) 0%, transparent 50%),
                radial-gradient(circle at 75% 75%, rgba(255,255,255,0.1) 0%, transparent 50%);
            z-index: -1;
        }}
        
        .container {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }}
        
        .cards-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #0066cc 0%, #004a99 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 6px 20px rgba(0, 102, 204, 0.3);
        }}
        
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }}
        
        .header p {{
            margin: 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .card {{
            background-color: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 1px solid #f0f0f0;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            border-color: #0066cc;
        }}
        
        .card h2 {{
            margin-top: 0;
            color: #333;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .status {{
            display: inline-block;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-left: 10px;
        }}
        
        .status-healthy {{
            background-color: #e6ffe6;
            color: #00cc00;
            border: 1px solid #c8f7c5;
        }}
        
        .warning {{
            background-color: #fff3e6;
            padding: 20px;
            border-left: 5px solid #cc6600;
            margin: 25px 0;
            border-radius: 8px;
        }}
        
        .nav-links {{
            margin-top: 30px;
            background-color: #ffffff;
            padding: 20px 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
            justify-content: center;
        }}
        
        .nav-links a {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 25px;
            background-color: #f8f9fa;
            color: #0066cc;
            text-decoration: none;
            border-radius: 8px;
            border: 2px solid transparent;
            font-weight: 600;
            transition: all 0.3s ease;
            font-size: 14px;
        }}
        
        .nav-links a:hover {{
            background-color: #e9f2ff;
            border-color: #0066cc;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,102,204,0.2);
        }}
        
        .nav-links a i {{
            font-size: 16px;
        }}
        
        .footer {{
            background-color: #f8f9fa;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            margin-top: 40px;
            color: #666;
            border-top: 2px solid #e9ecef;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        .server-info p {{
            margin: 12px 0;
            display: flex;
            align-items: center;
            gap: 10px;
            color: #555;
        }}
        
        .server-info i {{
            color: #0066cc;
            width: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
    <div class="header">
        <h1><i class="fas fa-server"></i> Anhong Doris MCP Server</h1>
        <p>Enterprise Database Service - Dashboard</p>
    </div>
    
    <div class="nav-links">
        <a href="/token/management"><i class="fas fa-key"></i> Token Management</a>
        <a href="/cache/management"><i class="fas fa-database"></i> Cache Management</a>
        <a href="/logs/management"><i class="fas fa-file-alt"></i> MCP Log Management</a>
    </div>
    
    <div class="cards-container">
        <div class="card">
            <h2><i class="fas fa-tachometer-alt"></i> Server Status</h2>
            <div class="server-info">
                <p><i class="fas fa-heartbeat"></i> <strong>Status:</strong> <span class="status status-healthy">Running</span></p>
                <p><i class="fas fa-desktop"></i> <strong>Server Name:</strong> doris-mcp-server</p>
                <p><i class="fas fa-code-branch"></i> <strong>Version:</strong> {version}</p>
                <p><i class="fas fa-network-wired"></i> <strong>Transport:</strong> HTTP (Streamable)</p>
            </div>
        </div>
        
        <div class="card">
            <h2><i class="fas fa-lock"></i> Authentication</h2>
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
    </div>
    
    <div class="footer">
        <p><i class="fas fa-info-circle"></i> Anhong Doris MCP Server - Enterprise Database Management</p>
        <p><i class="fas fa-copyright"></i> 2024 Anhong Software Foundation. All rights reserved.</p>
        <p><small>Version {version} • Built with <i class="fas fa-heart"></i> for enterprise reliability</small></p>
    </div>
    
    </div>
</body>
</html>
"""

INDEX_PAGE_ENABLED_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Doris MCP Server - Dashboard</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }}
        
        body::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                radial-gradient(circle at 25% 25%, rgba(255,255,255,0.1) 0%, transparent 50%),
                radial-gradient(circle at 75% 75%, rgba(255,255,255,0.1) 0%, transparent 50%);
            z-index: -1;
        }}
        
        .container {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }}
        
        .header {{
            background: linear-gradient(135deg, #0066cc 0%, #004a99 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 6px 20px rgba(0, 102, 204, 0.3);
        }}
        
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }}
        
        .header p {{
            margin: 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .card {{
            background-color: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 1px solid #f0f0f0;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            border-color: #0066cc;
        }}
        
        .card h2 {{
            margin-top: 0;
            color: #333;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .status {{
            display: inline-block;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-left: 10px;
        }}
        
        .status-healthy {{
            background-color: #e6ffe6;
            color: #00cc00;
            border: 1px solid #c8f7c5;
        }}
        
        .nav-links {{
            margin-top: 30px;
            background-color: #ffffff;
            padding: 20px 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
            justify-content: center;
        }}
        
        .nav-links a {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 25px;
            background-color: #f8f9fa;
            color: #0066cc;
            text-decoration: none;
            border-radius: 8px;
            border: 2px solid transparent;
            font-weight: 600;
            transition: all 0.3s ease;
            font-size: 14px;
        }}
        
        .nav-links a:hover {{
            background-color: #e9f2ff;
            border-color: #0066cc;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,102,204,0.2);
        }}
        
        .logout-btn {{
            background-color: #fff5f5 !important;
            color: #dc3545 !important;
            border-color: #ffd7da !important;
            margin-left: auto;
        }}
        
        .logout-btn:hover {{
            background-color: #ffebee !important;
            border-color: #dc3545 !important;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(220,53,69,0.15);
        }}
        
        .cards-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .server-info p {{
            margin: 12px 0;
            display: flex;
            align-items: center;
            gap: 10px;
            color: #555;
        }}
        
        .server-info i {{
            color: #0066cc;
            width: 20px;
            text-align: center;
        }}
        
        .footer {{
            background-color: #f8f9fa;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            margin-top: 40px;
            color: #666;
            border-top: 2px solid #e9ecef;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
    <div class="header">
        <h1><i class="fas fa-server"></i> Anhong Doris MCP Server</h1>
        <p>Enterprise Database Service - Dashboard</p>
    </div>
    
    <div class="nav-links">
        <a href="/token/management"><i class="fas fa-key"></i> Token Management</a>
        <a href="/cache/management"><i class="fas fa-database"></i> Cache Management</a>
        <a href="/logs/management"><i class="fas fa-file-alt"></i> MCP Log Management</a>
        <a href="/ui/logout" class="logout-btn"><i class="fas fa-sign-out-alt"></i> Logout</a>
    </div>
    
    <div class="cards-container">
        <div class="card">
            <h2><i class="fas fa-tachometer-alt"></i> Server Status</h2>
            <div class="server-info">
                <p><i class="fas fa-heartbeat"></i> <strong>Status:</strong> <span class="status status-healthy">Healthy</span></p>
                <p><i class="fas fa-desktop"></i> <strong>Server Name:</strong> doris-mcp-server</p>
                <p><i class="fas fa-code-branch"></i> <strong>Version:</strong> {version}</p>
                <p><i class="fas fa-network-wired"></i> <strong>Transport:</strong> HTTP (Streamable)</p>
            </div>
        </div>
        
        <div class="card">
            <h2><i class="fas fa-user-circle"></i> Authentication Info</h2>
            <div class="server-info">
                <p><i class="fas fa-user"></i> <strong>Username:</strong> {username}</p>
                <p><i class="fas fa-check-circle"></i> <strong>Session Status:</strong> <span class="status status-healthy">Active</span></p>
            </div>
        </div>
        
        <div class="card">
            <h2><i class="fas fa-link"></i> Quick Links</h2>
            <div class="server-info">
                <p><i class="fas fa-key"></i> <strong>Token Management:</strong> <a href="/token/management">Manage Tokens</a></p>
                <p><i class="fas fa-database"></i> <strong>Cache Management:</strong> <a href="/cache/management">Manage Cache</a></p>
                <p><i class="fas fa-file-alt"></i> <strong>MCP Log Management:</strong> <a href="/logs/management">View MCP Logs</a></p>
                <p><i class="fas fa-terminal"></i> <strong>API Endpoints:</strong> /mcp (MCP Protocol)</p>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p><i class="fas fa-info-circle"></i> Anhong Doris MCP Server - Enterprise Database Management</p>
        <p><i class="fas fa-copyright"></i> 2024 Anhong Software Foundation. All rights reserved.</p>
        <p><small>Version {version} • Built with <i class="fas fa-heart"></i> for enterprise reliability</small></p>
    </div>
    
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
                <input type="text" id="username" name="username" value="admin" required autofocus>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" value="123" required>
            </div>
            
            <button type="submit" class="submit-btn">Sign In</button>
        </form>
        
        <div class="server-info">
            Anhong Doris MCP Server
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
