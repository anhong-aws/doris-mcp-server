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
MCP Log Templates
HTML templates for displaying MCP logs and statistics
"""

MCP_LOG_MANAGEMENT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Log Management</title>
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
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .stat-item {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 10px;
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            margin-top: 5px;
            font-size: 0.9em;
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
        
        .btn-info {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        
        .search-box {
            padding: 12px 20px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            width: 100%;
            max-width: 400px;
            margin-right: 15px;
        }
        
        .search-box:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .filter-group {
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .filter-input {
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 0.9em;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #555;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .table-container {
            max-height: 500px;
            overflow-y: auto;
            border-radius: 10px;
            border: 1px solid #eee;
        }
        
        .method-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 500;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .arguments {
            font-family: monospace;
            background: #f0f0f0;
            padding: 8px 12px;
            border-radius: 5px;
            font-size: 0.9em;
            max-width: 300px;
            overflow-x: auto;
        }
        
        .chart-container {
            height: 300px;
            margin: 20px 0;
        }
        
        .chart-title {
            text-align: center;
            margin: 20px 0;
            color: #555;
            font-size: 1.2em;
        }
        
        footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .card-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }
            
            .filter-group {
                width: 100%;
                flex-direction: column;
                align-items: stretch;
            }
            
            .search-box {
                max-width: 100%;
                margin-right: 0;
            }
        }
    </style>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <div style="margin-bottom: 15px;"><a href="/" style="color: white; text-decoration: none; font-weight: 600; font-size: 1.1em;">← Back to Home</a></div>
            <h1>MCP Log Management</h1>
            <p class="subtitle">Monitor and analyze MCP method calls</p>
        </header>
        
        <!-- Log Overview -->
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Log Overview</h2>
            </div>
            <div class="grid">
                <div class="stat-item">
                    <div class="stat-value">{log_file_size_human}</div>
                    <div class="stat-label">Log File Size</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{total_methods}</div>
                    <div class="stat-label">Total Methods</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{total_calls}</div>
                    <div class="stat-label">Total Calls</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{recent_calls}</div>
                    <div class="stat-label">Last 24h Calls</div>
                </div>
            </div>
            <div style="margin-top: 20px; font-size: 0.9em; color: #666;">
                <p>Log File: {log_file_path}</p>
                <p>Created: {log_created_at} | Modified: {log_modified_at}</p>
            </div>
        </div>
        
        <!-- Log Filtering -->
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Log Filtering</h2>
            </div>
            <div class="filter-group">
                <input type="text" class="search-box" id="searchBox" placeholder="Search log messages..." onkeyup="filterLogs()">
                <select class="filter-input" id="methodFilter" onchange="filterLogs()">
                    <option value="">All Methods</option>
                    {method_options}
                </select>
                <select class="filter-input" id="daysFilter" onchange="filterLogs()">
                    <option value="1">Last 24h</option>
                    <option value="7" selected>Last 7 days</option>
                    <option value="30">Last 30 days</option>
                </select>
                <input type="number" class="filter-input" id="limitFilter" placeholder="Limit (100)" value="100" min="1" max="1000">
                <button class="btn btn-primary" onclick="refreshLogs()">Refresh</button>
            </div>
        </div>
        
        <!-- Method Call Statistics -->
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Method Call Statistics</h2>
            </div>
            <div class="chart-container">
                <canvas id="methodStatsChart"></canvas>
            </div>
        </div>
        
        <!-- Daily Call Statistics -->
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Daily Call Count</h2>
            </div>
            <div class="chart-container">
                <canvas id="dailyStatsChart"></canvas>
            </div>
        </div>
        
        <!-- Log List -->
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Recent Logs</h2>
                <div style="color: #888; font-size: 0.9em;">Showing {displayed_logs} of {total_logs} logs</div>
            </div>
            <div class="table-container">
                <table id="logsTable">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Method</th>
                            <th>Arguments</th>
                            <th>Message</th>
                        </tr>
                    </thead>
                    <tbody id="logsBody">
                        {logs_rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <footer>
            <p>Generated at: {generated_at}</p>
        </footer>
    </div>
    
    <script>
        // Log data from server
        const methodStats = {method_stats_json};
        const dailyStats = {daily_stats_json};
        const logsData = {logs_json};
        
        // Initialize charts
        document.addEventListener('DOMContentLoaded', function() {
            // Method Call Statistics Chart
            const methodCtx = document.getElementById('methodStatsChart').getContext('2d');
            new Chart(methodCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(methodStats),
                    datasets: [{
                        label: 'Call Count',
                        data: Object.values(methodStats),
                        backgroundColor: 'rgba(102, 126, 234, 0.7)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Method Call Distribution'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Number of Calls'
                            }
                        }
                    }
                }
            });
            
            // Daily Call Statistics Chart
            const dailyCtx = document.getElementById('dailyStatsChart').getContext('2d');
            new Chart(dailyCtx, {
                type: 'line',
                data: {
                    labels: Object.keys(dailyStats),
                    datasets: [{
                        label: 'Daily Calls',
                        data: Object.values(dailyStats),
                        borderColor: 'rgba(118, 75, 162, 1)',
                        backgroundColor: 'rgba(118, 75, 162, 0.2)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Daily Call Count'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Number of Calls'
                            }
                        }
                    }
                }
            });
        });
        
        // Filter logs based on search and filters
        function filterLogs() {
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const methodFilter = document.getElementById('methodFilter').value;
            const rows = document.querySelectorAll('#logsBody tr');
            
            let visibleCount = 0;
            
            rows.forEach(row => {
                const method = row.getAttribute('data-method');
                const message = row.querySelector('td:last-child').textContent.toLowerCase();
                
                const matchesSearch = message.includes(searchTerm);
                const matchesMethod = methodFilter === '' || method === methodFilter;
                
                if (matchesSearch && matchesMethod) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });
            
            // Update displayed count
            document.querySelector('.card-title + div').textContent = 
                `Showing ${visibleCount} of ${rows.length} logs`;
        }
        
        // Refresh logs from server
        function refreshLogs() {
            const days = document.getElementById('daysFilter').value;
            const limit = document.getElementById('limitFilter').value;
            const method = document.getElementById('methodFilter').value;
            const search = document.getElementById('searchBox').value;
            
            let url = `/logs/management?days=${days}&limit=${limit}`;
            if (method) url += `&method=${method}`;
            if (search) url += `&search=${encodeURIComponent(search)}`;
            
            window.location.href = url;
        }
    </script>
</body>
</html>
"""