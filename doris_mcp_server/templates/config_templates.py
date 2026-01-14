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
Configuration Management Page Template
HTML template for configuration viewing and editing
"""

CONFIG_MANAGEMENT_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuration Management</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .card-title {
            font-size: 1.4em;
            color: #333;
        }
        
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .nav-tab {
            padding: 12px 25px;
            background: #f0f0f0;
            border: none;
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .nav-tab:hover {
            background: #e0e0e0;
        }
        
        .nav-tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .config-section {
            margin-bottom: 30px;
        }
        
        .config-section h3 {
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .config-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
        }
        
        .config-label {
            font-weight: 600;
            color: #555;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        
        .config-value {
            color: #333;
            word-break: break-all;
        }
        
        .sensitive-value {
            color: #dc3545;
            font-weight: bold;
        }
        
        .config-editor-container {
            margin-bottom: 20px;
        }
        
        .editor-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .editor-path {
            font-family: monospace;
            background: #f0f0f0;
            padding: 8px 15px;
            border-radius: 5px;
            font-size: 0.9em;
        }
        
        .config-editor {
            width: 100%;
            min-height: 500px;
            padding: 20px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-family: monospace;
            font-size: 14px;
            line-height: 1.6;
            resize: vertical;
            background: #fafafa;
            color: #333;
        }
        
        .config-editor:focus {
            outline: none;
            border-color: #667eea;
            background: white;
        }
        
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
            color: white;
        }
        
        .btn-group {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 10px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        }
        
        .notification.success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        
        .notification.error {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .status-message {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 0.95em;
        }
        
        .status-message.info {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        
        .status-message.warning {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        .backup-info {
            background: #fff3cd;
            color: #856404;
            padding: 12px;
            border-radius: 8px;
            margin: 15px 0;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div style="margin-bottom: 15px;"><a href="/" style="color: white; text-decoration: none; font-weight: 600; font-size: 1.1em;">← Back to Home</a></div>
            <h1>Configuration Management</h1>
            <p class="subtitle">View and edit your Doris MCP Server configuration</p>
        </header>
        
        <div class="card">
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="switchTab('view-config')">View Configuration</button>
                <button class="nav-tab" onclick="switchTab('edit-config')">Edit Configuration (.env file)</button>
            </div>
            
            <!-- View Configuration Tab -->
            <div id="view-config" class="tab-content active">
                
                <!-- Basic Configuration -->
                <div class="config-section">
                    <h3><i class="fas fa-cog"></i> Basic Configuration</h3>
                    <div class="config-grid">
                        {basic_config_html}
                    </div>
                </div>
                
                <!-- Database Configuration -->
                <div class="config-section">
                    <h3><i class="fas fa-database"></i> Database Configuration</h3>
                    <div class="config-grid">
                        {database_config_html}
                    </div>
                </div>
                
                <!-- Security Configuration -->
                <div class="config-section">
                    <h3><i class="fas fa-lock"></i> Security Configuration</h3>
                    <div class="config-grid">
                        {security_config_html}
                    </div>
                </div>
                
                <!-- Performance Configuration -->
                <div class="config-section">
                    <h3><i class="fas fa-tachometer-alt"></i> Performance Configuration</h3>
                    <div class="config-grid">
                        {performance_config_html}
                    </div>
                </div>
                
                <!-- Logging Configuration -->
                <div class="config-section">
                    <h3><i class="fas fa-file-alt"></i> Logging Configuration</h3>
                    <div class="config-grid">
                        {logging_config_html}
                    </div>
                </div>
                
                <!-- Monitoring Configuration -->
                <div class="config-section">
                    <h3><i class="fas fa-chart-line"></i> Monitoring Configuration</h3>
                    <div class="config-grid">
                        {monitoring_config_html}
                    </div>
                </div>
                
                <!-- ADBC Configuration -->
                <div class="config-section">
                    <h3><i class="fas fa-arrow-right"></i> ADBC Configuration</h3>
                    <div class="config-grid">
                        {adbc_config_html}
                    </div>
                </div>
                
                <!-- Data Quality Configuration -->
                <div class="config-section">
                    <h3><i class="fas fa-check-circle"></i> Data Quality Configuration</h3>
                    <div class="config-grid">
                        {data_quality_config_html}
                    </div>
                </div>
            </div>
            
            <!-- Edit Configuration Tab -->
            <div id="edit-config" class="tab-content">
                <div class="status-message info">
                    <strong>Warning:</strong> Editing the .env file directly can affect server functionality. Always create a backup before making changes.
                </div>
                
                <div class="editor-header">
                    <h3><i class="fas fa-edit"></i> Edit .env File</h3>
                    <div class="editor-path">
                        <i class="fas fa-file-code"></i> {env_file_path}
                    </div>
                </div>
                
                <div class="config-editor-container">
                    <textarea id="envEditor" class="config-editor" placeholder="# Edit your .env file here\n# Example:\n# DORIS_HOST=localhost\n# DORIS_PORT=9030\n# DORIS_USER=root\n">{env_file_content}</textarea>
                </div>
                
                <div class="backup-info">
                    <i class="fas fa-info-circle"></i> A backup of the .env file will be created automatically before saving changes.
                </div>
                
                <div class="btn-group">
                    <button class="btn btn-primary" onclick="saveEnvFile()">
                        <i class="fas fa-save"></i> Save Changes
                    </button>
                    <button class="btn btn-secondary" onclick="resetEnvFile()">
                        <i class="fas fa-undo"></i> Reset
                    </button>
                </div>
            </div>
        </div>
        
        <footer>
            <p style="text-align: center; color: white; opacity: 0.8; margin-top: 30px;">
                Generated at: {generated_at}
            </p>
        </footer>
    </div>
    
    <script>
        function switchTab(tabId) {
            // Remove active class from all tabs and content
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Add active class to selected tab and content
            document.querySelector(`[onclick="switchTab('${tabId}')"]`).classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }
        
        function showNotification(message, type) {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }
        
        let originalEnvContent = '';
        
        // Initialize original content when page loads
        document.addEventListener('DOMContentLoaded', () => {
            originalEnvContent = document.getElementById('envEditor').value;
        });
        
        function resetEnvFile() {
            document.getElementById('envEditor').value = originalEnvContent;
            showNotification('Configuration has been reset to original state', 'info');
        }
        
        async function saveEnvFile() {
            const content = document.getElementById('envEditor').value;
            
            try {
                const response = await fetch('/config/save-env', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        content: content
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    originalEnvContent = content;
                    showNotification('Configuration saved successfully!', 'success');
                } else {
                    showNotification('Failed to save configuration: ' + result.message, 'error');
                }
            } catch (error) {
                showNotification('Error saving configuration: ' + error.message, 'error');
            }
        }
    </script>
</body>
</html>
"""
