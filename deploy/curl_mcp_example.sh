#!/bin/bash

# MCP server URL
MCP_URL="http://localhost:3000/mcp"

echo "=== Doris MCP Server Curl Example (text/event-stream) ==="
echo "Server URL: $MCP_URL"

# Step 1: Initialize MCP session
echo -e "\n1. Initializing MCP connection..."
INIT_RESPONSE=$(curl -s -i -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "curl-test", "version": "1.0.0"}}}'
)

# Print full response with headers
echo -e "\n=== Initialization Response (Headers + Body) ==="
echo "$INIT_RESPONSE"

# Extract session ID from response headers
SESSION_ID=$(echo "$INIT_RESPONSE" | grep -i 'mcp-session-id' | head -1 | awk '{print $2}' | tr -d '\r')

if [ -z "$SESSION_ID" ]; then
    echo "Failed to get session ID."
    exit 1
fi

echo -e "\nSession ID obtained: $SESSION_ID"

# Step 2: List available tools (using POST for JSON-RPC requests)
echo -e "\n2. Listing available tools..."
TOOLS_RESPONSE=$(curl -s -i -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}'
)

# Print full response with headers
echo -e "\n=== Tools List Response (Headers + Body) ==="
echo "$TOOLS_RESPONSE"

# Step 3: Call show tables list tool to run a SQL query
echo -e "\n3. Calling show tables list tool to run 'SHOW DATABASES'..."
QUERY_RESPONSE=$(curl -s -i -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_db_table_list", "arguments": {"db_name": "dw_power"}}}'
)

# Print full response with headers
echo -e "\n=== exec_query Response (Headers + Body) ==="
echo "$QUERY_RESPONSE"

# Step 4: Call exec_query tool to run a SQL query
echo -e "\n3. Calling exec_query tool to run 'SHOW DATABASES'..."
QUERY_RESPONSE=$(curl -s -i -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "exec_query", "arguments": {"sql": "SHOW DATABASES"}}}'
)

# Print full response with headers
echo -e "\n=== exec_query Response (Headers + Body) ==="
echo "$QUERY_RESPONSE"

# Step 4: Optional - Establish text/event-stream connection (for server notifications)
echo -e "\n4. Optional: Establishing text/event-stream connection..."
echo "To receive server notifications, run in a separate terminal:"
echo "curl -N -H 'Accept: text/event-stream' -H 'mcp-session-id: $SESSION_ID' $MCP_URL"

echo -e "\n=== Example completed ==="