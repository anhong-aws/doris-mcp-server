#!/bin/bash

# MCP Server URL
MCP_URL="http://localhost:3000/mcp"

# Step 1: Initialize MCP session
echo "Initializing MCP session..."
INIT_RESPONSE=$(curl -s -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "curl-test", "version": "1.0.0"}}, "id": 1}')

# Extract session ID from response headers
SESSION_ID=$(echo "$INIT_RESPONSE" | grep -o 'mcp-session-id: [^\r]*' | cut -d' ' -f2)

if [ -z "$SESSION_ID" ]; then
    echo "Failed to get session ID. Response: $INIT_RESPONSE"
    exit 1
fi

echo "Session ID obtained: $SESSION_ID"

# Step 2: List available tools
echo -e "\nListing available tools..."
TOOLS_RESPONSE=$(curl -s -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}')

echo "Tools response: $TOOLS_RESPONSE"

# Step 3: Call a simple tool (get_db_list)
echo -e "\nCalling get_db_list tool..."
TOOL_RESPONSE=$(curl -s -X POST $MCP_URL \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "get_db_list", "arguments": {}}, "id": 3}')

echo "Tool response: $TOOL_RESPONSE"