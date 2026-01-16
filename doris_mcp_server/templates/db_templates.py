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
Database Connection Pool Management Templates
HTML templates for connection pool monitoring and management
"""

DB_MANAGEMENT_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Doris MCP Server - Connection Pool Management</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }
        
        body::before {
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
        }
        
        .container {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        .header {
            background: linear-gradient(135deg, #0066cc 0%, #004a99 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 6px 20px rgba(0, 102, 204, 0.3);
        }
        
        .header h1 {
            margin: 0 0 10px 0;
            font-size: 2.5em;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }
        
        .header p {
            margin: 0;
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .cards-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .card {
            background-color: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 1px solid #f0f0f0;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            border-color: #0066cc;
        }
        
        .card h2 {
            margin-top: 0;
            color: #333;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card h3 {
            margin-top: 20px;
            color: #555;
            font-size: 1.2em;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }
        
        .status {
            display: inline-block;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-left: 10px;
        }
        
        .status-healthy {
            background-color: #e6ffe6;
            color: #00cc00;
            border: 1px solid #c8f7c5;
        }
        
        .status-unhealthy {
            background-color: #ffe6e6;
            color: #cc0000;
            border: 1px solid #ffcccc;
        }
        
        .status-warning {
            background-color: #fff3e6;
            color: #cc6600;
            border: 1px solid #ffd7ba;
        }
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .metric-item {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e9ecef;
        }
        
        .metric-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            color: #0066cc;
        }
        
        .metric-unit {
            font-size: 12px;
            color: #999;
            margin-left: 5px;
        }
        
        .nav-links {
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
        }
        
        .nav-links a {
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
        }
        
        .nav-links a:hover {
            background-color: #e9f2ff;
            border-color: #0066cc;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,102,204,0.2);
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
            margin: 5px;
        }
        
        .btn-primary {
            background-color: #0066cc;
            color: white;
        }
        
        .btn-primary:hover {
            background-color: #0052a3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,102,204,0.2);
        }
        
        .btn-warning {
            background-color: #ff9800;
            color: white;
        }
        
        .btn-warning:hover {
            background-color: #f57c00;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255,152,0,0.2);
        }
        
        .btn-danger {
            background-color: #dc3545;
            color: white;
        }
        
        .btn-danger:hover {
            background-color: #c82333;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(220,53,69,0.2);
        }
        
        .btn-success {
            background-color: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background-color: #218838;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(40,167,69,0.2);
        }
        
        .table-container {
            overflow-x: auto;
            margin-top: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        
        tr:hover {
            background-color: #f8f9fa;
        }
        
        .actions {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        
        .status-indicator.healthy {
            background-color: #28a745;
        }
        
        .status-indicator.unhealthy {
            background-color: #dc3545;
        }
        
        .status-indicator.warning {
            background-color: #ffc107;
        }
        
        .diagnosis-item {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #0066cc;
        }
        
        .diagnosis-item.warning {
            border-left-color: #ffc107;
            background-color: #fff3cd;
        }
        
        .diagnosis-item.error {
            border-left-color: #dc3545;
            background-color: #f8d7da;
        }
        
        .diagnosis-item.success {
            border-left-color: #28a745;
            background-color: #d4edda;
        }
        
        .diagnosis-item.info {
            border-left-color: #17a2b8;
            background-color: #d1ecf1;
        }
        
        .update-time {
            font-size: 12px;
            color: #999;
            margin-top: 10px;
            text-align: right;
        }
        
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.5);
        }
        
        .modal-content {
            background-color: white;
            margin: 15% auto;
            padding: 30px;
            border-radius: 12px;
            width: 500px;
            max-width: 90%;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        
        .modal h2 {
            margin-top: 0;
            color: #333;
        }
        
        .modal-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 20px;
        }
        
        .btn-secondary {
            background-color: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background-color: #5a6268;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border: 1px solid transparent;
        }
        
        .alert-success {
            color: #155724;
            background-color: #d4edda;
            border-color: #c3e6cb;
        }
        
        .alert-error {
            color: #721c24;
            background-color: #f8d7da;
            border-color: #f5c6cb;
        }
        
        .alert-warning {
            color: #856404;
            background-color: #fff3cd;
            border-color: #ffeeba;
        }
    </style>
</head>
<body>
    <div class="container">
    <div class="header">
        <h1><i class="fas fa-database"></i> Connection Pool Management</h1>
        <p>Monitor and manage your database connection pool</p>
    </div>
    
    <div class="nav-links">
        <a href="/" class="btn-primary"><i class="fas fa-home"></i> Dashboard</a>
        <a href="/token/management"><i class="fas fa-key"></i> Token </a>
        <a href="/cache/management"><i class="fas fa-database"></i> Cache </a>
        <a href="/logs/management"><i class="fas fa-file-alt"></i> MCP Log </a>
        <a href="/config/management"><i class="fas fa-cog"></i> Config </a>
        <a href="/ui/logout" class="logout-btn"><i class="fas fa-sign-out-alt"></i> Logout</a>
    </div>
    
    <div id="alert" class="alert" style="display: none;"></div>
    
    <div class="cards-container">
        <div class="card">
            <h2><i class="fas fa-heartbeat"></i> Pool Status</h2>
            <div class="metric-grid">
                <div class="metric-item">
                    <div class="metric-label">Status</div>
                    <div class="metric-value"><span class="status-indicator" id="pool-status-indicator"></span><span id="pool-status-text">Loading...</span></div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Pool Size</div>
                    <div class="metric-value" id="pool-size">-</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Active Connections</div>
                    <div class="metric-value" id="active-connections">-</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Idle Connections</div>
                    <div class="metric-value" id="idle-connections">-</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Max Connections</div>
                    <div class="metric-value" id="max-connections">-</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Utilization</div>
                    <div class="metric-value" id="utilization">-</div>
                    <span class="metric-unit">%</span>
                </div>
            </div>
            <div class="update-time">Last updated: <span id="last-updated">-</span></div>
        </div>
        
        <div class="card">
            <h2><i class="fas fa-chart-line"></i> Pool Metrics</h2>
            <div class="metric-grid">
                <div class="metric-item">
                    <div class="metric-label">Failed Connections</div>
                    <div class="metric-value" id="failed-connections">-</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Connection Errors</div>
                    <div class="metric-value" id="connection-errors">-</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Avg Connection Time</div>
                    <div class="metric-value" id="avg-connection-time">-</div>
                    <span class="metric-unit">ms</span>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Conn Acquisition Timeouts</div>
                    <div class="metric-value" id="acquisition-timeouts">-</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Query Timeouts</div>
                    <div class="metric-value" id="query-timeouts">-</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2><i class="fas fa-tools"></i> Actions</h2>
            <div class="actions">
                <button class="btn btn-success" id="test-connection"><i class="fas fa-plug"></i> Test Connection</button>
                <button class="btn btn-primary" id="refresh-status"><i class="fas fa-sync-alt"></i> Refresh Status</button>
                <button class="btn btn-warning" id="release-idle"><i class="fas fa-sign-out-alt"></i> Release Idle</button>
                <button class="btn btn-danger" id="close-all"><i class="fas fa-times-circle"></i> Close All</button>
                <button class="btn btn-danger" id="recreate-pool"><i class="fas fa-redo"></i> Recreate Pool</button>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2><i class="fas fa-list-alt"></i> Sessions</h2>
        <div class="table-container">
            <table id="sessions-table">
                <thead>
                    <tr>
                        <th>Session ID</th>
                        <th>Status</th>
                        <th>Created At</th>
                        <th>Last Used</th>
                        <th>Query Count</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="sessions-body">
                    <tr><td colspan="6" style="text-align: center;">Loading sessions...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="card">
        <h2><i class="fas fa-database"></i> All Connections</h2>
        <div class="table-container">
            <table id="all-connections-table">
                <thead>
                      <tr>
                          <th>Connection ID</th>
                          <th>Status</th>
                          <th>Session ID</th>
                          <th>Created At</th>
                          <th>Acquired At</th>
                          <th>Last Release Time</th>
                          <th>Current Duration (s)</th>
                          <th>Total Duration (s)</th>
                          <th>Release Count</th>
                          <th>Query Count</th>
                          <th>Is Healthy</th>
                          <th>Last SQL</th>
                      </tr>
                  </thead>
                <tbody id="all-connections-body">
                    <tr><td colspan="12" style="text-align: center;">Loading connections...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="card">
        <h2><i class="fas fa-stethoscope"></i> Diagnosis</h2>
        <div id="diagnosis-container">
            <div class="diagnosis-item">Loading diagnosis...</div>
        </div>
    </div>
    </div>
    
    <!-- Confirmation Modal -->
    <div id="confirm-modal" class="modal">
        <div class="modal-content">
            <h2><i class="fas fa-exclamation-triangle"></i> Confirm Action</h2>
            <p id="modal-message">Are you sure you want to perform this action?</p>
            <div class="modal-actions">
                <button class="btn btn-secondary" id="modal-cancel">Cancel</button>
                <button class="btn btn-danger" id="modal-confirm">Confirm</button>
            </div>
        </div>
    </div>
    
    <script>
        // DOM Elements
        const testConnectionBtn = document.getElementById('test-connection');
        const refreshStatusBtn = document.getElementById('refresh-status');
        const releaseIdleBtn = document.getElementById('release-idle');
        const closeAllBtn = document.getElementById('close-all');
        const recreatePoolBtn = document.getElementById('recreate-pool');
        const confirmModal = document.getElementById('confirm-modal');
        const modalMessage = document.getElementById('modal-message');
        const modalCancel = document.getElementById('modal-cancel');
        const modalConfirm = document.getElementById('modal-confirm');
        const alertDiv = document.getElementById('alert');
        
        // Action variables
        let currentAction = null;
        
        // Show alert
        function showAlert(message, type = 'success') {
            alertDiv.textContent = message;
            alertDiv.className = `alert alert-${type}`;
            alertDiv.style.display = 'block';
            
            // Show success alerts for 10 seconds, other alerts for 20 seconds
            const timeout = type === 'success' ? 10000 : 20000;
            setTimeout(() => {
                alertDiv.style.display = 'none';
            }, timeout);
        }
        
        // Show confirmation modal
        function showConfirmModal(message, action) {
            modalMessage.textContent = message;
            currentAction = action;
            confirmModal.style.display = 'block';
        }
        
        // Hide confirmation modal
        function hideConfirmModal() {
            confirmModal.style.display = 'none';
            currentAction = null;
        }
        
        // Fetch pool status
        async function fetchPoolStatus() {
            try {
                const response = await fetch('/db/status');
                const data = await response.json();
                
                if (data.success) {
                    updatePoolStatus(data.data);
                    updateSessions(data.data.sessions);
                    updateDiagnosis(data.data.diagnosis);
                } else {
                    showAlert(data.error, 'error');
                }
            } catch (error) {
                showAlert('Failed to fetch pool status: ' + error.message, 'error');
            }
        }
        
        // Fetch all connections
        async function fetchAllConnections() {
            try {
                const response = await fetch('/db/connections');
                const data = await response.json();
                
                if (data.success) {
                    updateAllConnections(data.data);
                } else {
                    showAlert(data.error, 'error');
                }
            } catch (error) {
                showAlert('Failed to fetch connections: ' + error.message, 'error');
            }
        }
        
        // Update all connections table
        function updateAllConnections(connections) {
            const tbody = document.getElementById('all-connections-body');
            
            if (connections.length === 0) {
                tbody.innerHTML = '<tr><td colspan="11" style="text-align: center;">No connections found</td></tr>';
                return;
            }
            
            tbody.innerHTML = connections.map(conn => `
                <tr>
                    <td>${conn.connection_id}</td>
                    <td>
                        <span class="status-indicator ${conn.status === 'active' ? 'healthy' : conn.status === 'idle' ? 'warning' : 'unhealthy'}"></span>
                        ${conn.status.charAt(0).toUpperCase() + conn.status.slice(1)}
                    </td>
                    <td>${conn.session_id || '-'}</td>
                    <td>${conn.created_at ? new Date(conn.created_at).toLocaleString() : '-'}</td>
                    <td>${conn.acquired_at ? new Date(conn.acquired_at).toLocaleString() : '-'}</td>
                    <td>${conn.last_release_time ? new Date(conn.last_release_time).toLocaleString() : '-'}</td>
                    <td>${conn.current_duration !== null ? conn.current_duration : '-'}</td>
                    <td>${conn.total_duration ? conn.total_duration.toFixed(2) : '-'}</td>
                    <td>${conn.release_count || 0}</td>
                    <td>${conn.query_count || 0}</td>
                    <td>
                        <span class="status-indicator ${conn.is_healthy ? 'healthy' : 'unhealthy'}"></span>
                        ${conn.is_healthy ? 'Yes' : 'No'}
                    </td>
                    <td>
                        ${conn.last_sql ? 
                            `<i class="fas fa-file-code" style="color: #0066cc; cursor: help; font-size: 16px;" data-sql="${conn.last_sql.replace(/"/g, '&quot;')}" onmouseenter="showSqlTooltip(event)" onmouseleave="hideSqlTooltip()"></i>` : 
                            '<i class="fas fa-file-code" style="color: #999; cursor: help; font-size: 16px;" data-sql="None SQL" onmouseenter="showSqlTooltip(event)" onmouseleave="hideSqlTooltip()"></i>'}
                    </td>
                </tr>
            `).join('');
        }
        
        // Update pool status
        function updatePoolStatus(status) {
            // Update basic info
            document.getElementById('pool-size').textContent = status.pool_size;
            document.getElementById('active-connections').textContent = status.active_connections;
            document.getElementById('idle-connections').textContent = status.idle_connections;
            document.getElementById('max-connections').textContent = status.max_connections;
            
            // Calculate utilization
            const utilization = status.pool_size > 0 ? 
                Math.round((status.active_connections / status.pool_size) * 100) : 0;
            document.getElementById('utilization').textContent = utilization;
            
            // Update status indicator
            const statusIndicator = document.getElementById('pool-status-indicator');
            const statusText = document.getElementById('pool-status-text');
            
            if (status.pool_status === 'healthy') {
                statusIndicator.className = 'status-indicator healthy';
                statusText.textContent = 'Healthy';
            } else if (status.pool_status === 'warning') {
                statusIndicator.className = 'status-indicator warning';
                statusText.textContent = 'Warning';
            } else {
                statusIndicator.className = 'status-indicator unhealthy';
                statusText.textContent = 'Unhealthy';
            }
            
            // Update metrics
            document.getElementById('failed-connections').textContent = status.failed_connections;
            document.getElementById('connection-errors').textContent = status.connection_errors;
            document.getElementById('avg-connection-time').textContent = status.avg_connection_time.toFixed(2);
            document.getElementById('acquisition-timeouts').textContent = status.acquisition_timeouts;
            document.getElementById('query-timeouts').textContent = status.query_timeouts;
            
            // Update last updated time
            const now = new Date();
            document.getElementById('last-updated').textContent = now.toLocaleString();
        }
        
        // Update sessions
        function updateSessions(sessions) {
            const tbody = document.getElementById('sessions-body');
            
            if (sessions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No active sessions</td></tr>';
                return;
            }
            
            tbody.innerHTML = sessions.map(session => `
                <tr>
                    <td>${session.session_id}</td>
                    <td>
                        <span class="status-indicator ${session.status}"></span>
                        ${session.status.charAt(0).toUpperCase() + session.status.slice(1)}
                    </td>
                    <td>${new Date(session.created_at).toLocaleString()}</td>
                    <td>${new Date(session.last_used).toLocaleString()}</td>
                    <td>${session.query_count}</td>
                    <td>
                        <button class="btn btn-danger" onclick="releaseSession('${session.session_id}')" style="padding: 6px 12px; font-size: 12px;">
                            <i class="fas fa-times"></i> Release
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
        // Update diagnosis
        function updateDiagnosis(diagnosis) {
            const container = document.getElementById('diagnosis-container');
            
            if (!diagnosis || diagnosis.length === 0) {
                container.innerHTML = '<div class="diagnosis-item success">No issues detected</div>';
                return;
            }
            
            container.innerHTML = diagnosis.map(item => `
                <div class="diagnosis-item ${item.type}">
                    <strong>${item.title}:</strong> ${item.description}
                    ${item.recommendation ? `<br><strong>Recommendation:</strong> ${item.recommendation}` : ''}
                </div>
            `).join('');
        }
        
        // Release session
        async function releaseSession(sessionId) {
            if (!confirm(`Are you sure you want to release session ${sessionId}?`)) {
                return;
            }
            
            try {
                const response = await fetch(`/db/session/${sessionId}/release`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    showAlert(`Session ${sessionId} released successfully`);
                    fetchPoolStatus();
                } else {
                    showAlert(data.error, 'error');
                }
            } catch (error) {
                showAlert('Failed to release session: ' + error.message, 'error');
            }
        }
        
        // Test connection
        testConnectionBtn.addEventListener('click', async () => {
            // Store original text
            const originalText = testConnectionBtn.innerHTML;
            testConnectionBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing...';
            testConnectionBtn.disabled = true;
            
            try {
                const response = await fetch('/db/test');
                const data = await response.json();
                
                if (data.success) {
                    showAlert('Connection test successful!', 'success');
                    fetchPoolStatus();
                } else {
                    showAlert('Connection test failed: ' + data.error, 'error');
                }
            } catch (error) {
                showAlert('Failed to test connection: ' + error.message, 'error');
            } finally {
                // Restore original state
                testConnectionBtn.innerHTML = originalText;
                testConnectionBtn.disabled = false;
            }
        });
        
        // Refresh status
        refreshStatusBtn.addEventListener('click', async () => {
            // Store original text
            const originalText = refreshStatusBtn.innerHTML;
            refreshStatusBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
            refreshStatusBtn.disabled = true;
            
            try {
                await fetchPoolStatus();
                showAlert('Status refreshed successfully!');
            } catch (error) {
                showAlert('Failed to refresh status: ' + error.message, 'error');
            } finally {
                // Restore original state
                refreshStatusBtn.innerHTML = originalText;
                refreshStatusBtn.disabled = false;
            }
        });
        
        // Release idle connections
        releaseIdleBtn.addEventListener('click', () => {
            showConfirmModal(
                'Are you sure you want to release all idle connections? This will close connections that are not currently in use.',
                'release-idle'
            );
        });
        
        // Close all connections
        closeAllBtn.addEventListener('click', () => {
            showConfirmModal(
                'Are you sure you want to close all connections? This will terminate all active connections and may disrupt ongoing operations.',
                'close-all'
            );
        });
        
        // Recreate pool
        recreatePoolBtn.addEventListener('click', () => {
            showConfirmModal(
                'Are you sure you want to recreate the connection pool? This will terminate all connections and restart the pool. This operation may take several seconds.',
                'recreate-pool'
            );
        });
        
        // Modal cancel
        modalCancel.addEventListener('click', () => {
            hideConfirmModal();
        });
        
        // Modal confirm
        modalConfirm.addEventListener('click', async () => {
            const action = currentAction;
            hideConfirmModal();
            
            let btn;
            let endpoint;
            let successMessage;
            let loadingText;
            
            switch (action) {
                case 'release-idle':
                    btn = releaseIdleBtn;
                    endpoint = '/db/refresh';
                    successMessage = 'Idle connections released successfully!';
                    loadingText = '<i class="fas fa-spinner fa-spin"></i> Releasing...';
                    break;
                case 'close-all':
                    btn = closeAllBtn;
                    endpoint = '/db/close-all';
                    successMessage = 'All connections closed successfully!';
                    loadingText = '<i class="fas fa-spinner fa-spin"></i> Closing...';
                    break;
                case 'recreate-pool':
                    btn = recreatePoolBtn;
                    endpoint = '/db/recreate';
                    successMessage = 'Connection pool recreated successfully!';
                    loadingText = '<i class="fas fa-spinner fa-spin"></i> Recreating...';
                    break;
                default:
                    return;
            }
            
            // Show loading state
            const originalText = btn.innerHTML;
            btn.innerHTML = loadingText;
            btn.disabled = true;
            
            try {
                const response = await fetch(endpoint, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    showAlert(successMessage);
                    fetchPoolStatus();
                } else {
                    showAlert(data.error, 'error');
                }
            } catch (error) {
                showAlert('Failed to perform action: ' + error.message, 'error');
            } finally {
                // Restore original state
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        });
        

        
        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === confirmModal) {
                hideConfirmModal();
            }
        });
        
        // Initial load
        async function initialLoad() {
            await fetchPoolStatus();
            await fetchAllConnections();
        }
        
        initialLoad();

        // Custom tooltip functions for SQL display
        function showSqlTooltip(event) {
            const sql = event.target.getAttribute('data-sql');
            if (!sql) return;

            // Create tooltip element if it doesn't exist
            let tooltip = document.getElementById('sql-tooltip');
            if (!tooltip) {
                tooltip = document.createElement('div');
                tooltip.id = 'sql-tooltip';
                tooltip.style.cssText = `
                    position: absolute;
                    background-color: #333;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                    white-space: pre-wrap;
                    word-break: break-all;
                    max-width: 500px;
                    z-index: 10000;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                    pointer-events: none;
                `;
                document.body.appendChild(tooltip);
            }

            // Set tooltip content and position
            tooltip.textContent = sql;
            tooltip.style.left = `${event.pageX + 10}px`;
            tooltip.style.top = `${event.pageY + 10}px`;
            tooltip.style.display = 'block';
        }

        function hideSqlTooltip() {
            const tooltip = document.getElementById('sql-tooltip');
            if (tooltip) {
                tooltip.style.display = 'none';
            }
        }
        
        // Auto-refresh every 30 seconds - commented out
        /*
        setInterval(async () => {
            await fetchPoolStatus();
            await fetchAllConnections();
        }, 30000);
        */
    </script>
</body>
</html>
"""
