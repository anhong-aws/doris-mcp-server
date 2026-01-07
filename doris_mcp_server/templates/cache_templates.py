CACHE_MANAGEMENT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cache Management</title>
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
        
        .status-badge {
            display: inline-block;
            padding: 8px 20px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .status-enabled {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        
        .status-disabled {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
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
        
        .btn-warning {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        .btn-info {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
            color: white;
        }
        
        .btn-sm {
            padding: 8px 15px;
            font-size: 0.85em;
            margin: 0 3px;
        }
        
        .btn-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
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
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .cache-type-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 500;
        }
        
        .type-schema { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .type-table { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; }
        .type-column { background: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%); color: white; }
        .type-metadata { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }
        .type-other { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333; }
        
        .valid { color: #11998e; font-weight: 600; }
        .expired { color: #eb3349; font-weight: 600; }
        
        .recommendation {
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            font-size: 0.95em;
        }
        
        .recommendation.info {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        
        .recommendation.success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        
        .recommendation.warning {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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
        
        .filter-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .filter-tab {
            padding: 10px 20px;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            background: #f0f0f0;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .filter-tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .filter-tab:hover:not(.active) {
            background: #e0e0e0;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .perf-stat {
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .perf-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
        }
        
        .perf-label {
            font-size: 0.85em;
            color: #666;
            margin-top: 5px;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .loading::after {
            content: '';
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid #667eea;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
            vertical-align: middle;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
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
        
        .table-container {
            max-height: 500px;
            overflow-y: auto;
            border-radius: 10px;
            border: 1px solid #eee;
        }
        
        .table-container thead {
            position: sticky;
            top: 0;
            background: white;
            z-index: 1;
        }
        
        .table-container th {
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Cache Management</h1>
            <p class="subtitle">Monitor and manage your Doris metadata cache</p>
        </header>
        
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Cache Status</h2>
                <span class="status-badge {enable_cache_status}">{enable_cache_status}</span>
            </div>
            <div class="grid">
                <div class="stat-item">
                    <div class="stat-value">{cache_ttl}</div>
                    <div class="stat-label">Cache TTL (seconds)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{cache_ttl_minutes}</div>
                    <div class="stat-label">Cache TTL (minutes)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{valid_entries}</div>
                    <div class="stat-label">Valid Entries</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{expired_entries}</div>
                    <div class="stat-label">Expired Entries</div>
                </div>
            </div>
            <div style="margin-top: 25px;">
                <h3 style="margin-bottom: 15px; color: #555;">Cache Types Distribution</h3>
                <div class="grid">
                    {cache_types_html}
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Cache Operations</h2>
            </div>
            <div class="btn-group">
                <button class="btn btn-primary" onclick="clearAllCache()">Clear All Cache</button>
                <button class="btn btn-info" onclick="window.location.reload()">Refresh Page</button>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Cache Entries</h2>
                <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 10px;">
                     <input type="text" class="search-box" id="searchBox" placeholder="Search cache entries..." onkeyup="filterTable()">
                 </div>
            </div>
            <div class="filter-tabs">
                <button class="filter-tab active" onclick="filterByType('all')">All</button>
                <button class="filter-tab" onclick="filterByType('database_tables')">Table List</button>
                <button class="filter-tab" onclick="filterByType('table_schema')">Table Schema</button>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Cache Key</th>
                            <th>Type</th>
                            <th>Age</th>
                            <th>Status</th>
                            <th>Size</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="cacheTableBody">
                        {entries_html}
                    </tbody>
                </table>
            </div>
            <p style="margin-top: 15px; color: #888; font-size: 0.9em;">Showing up to 100 entries</p>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Performance Analysis</h2>
            </div>
            <div class="stats-grid">
                <div class="perf-stat">
                    <div class="perf-value">{cache_efficiency}</div>
                    <div class="perf-label">Cache Efficiency</div>
                </div>
                <div class="perf-stat">
                    <div class="perf-value">{total_memory}</div>
                    <div class="perf-label">Total Memory</div>
                </div>
                <div class="perf-stat">
                    <div class="perf-value">{avg_entry_size}</div>
                    <div class="perf-label">Avg Entry Size</div>
                </div>
                <div class="perf-stat">
                    <div class="perf-value">{oldest_entry_age}</div>
                    <div class="perf-label">Oldest Entry (hrs)</div>
                </div>
                <div class="perf-stat">
                    <div class="perf-value">{newest_entry_age}</div>
                    <div class="perf-label">Newest Entry (hrs)</div>
                </div>
                <div class="perf-stat">
                    <div class="perf-value">{hit_potential}</div>
                    <div class="perf-label">Hit Potential</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Recommendations</h2>
            </div>
            {recommendations_html}
        </div>
        
        <footer>
            <p>Generated at: {generated_at}</p>
        </footer>
    </div>
    
    <div id="detailModal" class="modal" style="display: none;">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Cache Entry Details</h3>
                <span class="close" onclick="closeModal()">&times;</span>
            </div>
            <div class="modal-body">
                <div class="detail-section">
                    <h4>Basic Information</h4>
                    <div class="detail-row">
                        <span class="detail-label">Key:</span>
                        <span class="detail-value" id="detailKey"></span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Type:</span>
                        <span class="detail-value" id="detailType"></span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Status:</span>
                        <span class="detail-value" id="detailStatus"></span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Age:</span>
                        <span class="detail-value" id="detailAge"></span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Size:</span>
                        <span class="detail-value" id="detailSize"></span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Created:</span>
                        <span class="detail-value" id="detailCreated"></span>
                    </div>
                </div>
                <div class="detail-section">
                    <h4>Value Content</h4>
                    <pre id="detailValue" class="value-content"></pre>
                </div>
            </div>
        </div>
    </div>
    
    <style>
        .modal {
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.6);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background-color: white;
            border-radius: 15px;
            width: 90%;
            max-width: 800px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 25px;
            border-bottom: 1px solid #eee;
        }
        
        .modal-header h3 {
            color: #333;
            margin: 0;
        }
        
        .close {
            font-size: 28px;
            font-weight: bold;
            color: #aaa;
            cursor: pointer;
            transition: color 0.3s;
        }
        
        .close:hover {
            color: #333;
        }
        
        .modal-body {
            padding: 25px;
        }
        
        .detail-section {
            margin-bottom: 25px;
        }
        
        .detail-section h4 {
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .detail-row {
            display: flex;
            margin-bottom: 12px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .detail-label {
            font-weight: bold;
            color: #555;
            width: 120px;
            flex-shrink: 0;
        }
        
        .detail-value {
            color: #333;
            word-break: break-all;
            font-family: monospace;
        }
        
        .value-content {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 10px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.5;
            max-height: 400px;
            overflow-y: auto;
        }
    </style>
    
    <script>
        let currentFilter = 'all';
        
        function filterByType(type) {
            currentFilter = type;
            document.querySelectorAll('.filter-tab').forEach(tab => {
                tab.classList.remove('active');
                if (tab.textContent.toLowerCase() === type || (type === 'all' && tab.textContent === 'All')) {
                    tab.classList.add('active');
                }
            });
            filterTable();
        }
        
        function filterTable() {
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const rows = document.querySelectorAll('#cacheTableBody tr');
            
            rows.forEach(row => {
                const key = row.querySelector('td:first-child').textContent.toLowerCase();
                const type = row.getAttribute('data-type');
                const matchesSearch = key.includes(searchTerm);
                const matchesType = currentFilter === 'all' || type === currentFilter;
                
                if (matchesSearch && matchesType) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
        
        async function clearAllCache() {
            if (!confirm('Are you sure you want to clear all cache entries? This action cannot be undone.')) {
                return;
            }
            
            try {
                const response = await fetch('/cache/clear?cache_type=all', {
                    method: 'POST'
                });
                const result = await response.json();
                
                if (result.success) {
                    showNotification('Cache cleared successfully!', 'success');
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    showNotification('Failed to clear cache: ' + result.message, 'error');
                }
            } catch (error) {
                showNotification('Error: ' + error.message, 'error');
            }
        }
        
        async function deleteEntry(key) {
            if (!confirm('Are you sure you want to delete this cache entry?')) {
                return;
            }
            
            try {
                const response = await fetch('/cache/clear?specific_keys=' + encodeURIComponent(key), {
                    method: 'POST'
                });
                const result = await response.json();
                
                if (result.success) {
                    showNotification('Cache entry deleted!', 'success');
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    showNotification('Failed to delete entry: ' + result.message, 'error');
                }
            } catch (error) {
                showNotification('Error: ' + error.message, 'error');
            }
        }
        
        async function viewEntry(key) {
            try {
                const response = await fetch('/cache/entry?key=' + encodeURIComponent(key));
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('detailKey').textContent = result.key;
                    document.getElementById('detailType').textContent = result.cache_type;
                    document.getElementById('detailStatus').textContent = result.is_expired ? 'Expired' : 'Valid';
                    document.getElementById('detailAge').textContent = result.age_human + ' (' + result.age_seconds + ' seconds)';
                    document.getElementById('detailSize').textContent = result.value_size + ' bytes';
                    document.getElementById('detailCreated').textContent = result.created_at || 'N/A';
                    document.getElementById('detailValue').textContent = result.value || '(No value)';
                    document.getElementById('detailModal').style.display = 'flex';
                } else {
                    showNotification('Failed to load entry: ' + result.error, 'error');
                }
            } catch (error) {
                showNotification('Error: ' + error.message, 'error');
            }
        }
        
        function closeModal() {
            document.getElementById('detailModal').style.display = 'none';
        }
        
        function showNotification(message, type) {
            const notification = document.createElement('div');
            notification.className = 'notification ' + type;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }
    </script>
</body>
</html>
"""
