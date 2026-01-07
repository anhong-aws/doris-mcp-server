#!/bin/bash


echo "开始执行 Doris MCP Server 的关闭..."

# 查找占用 3000 端口的进程ID
echo "正在查找占用 3000 端口的进程..."
lsof -t -i:3000

# 强制终止占用 3000 端口的进程（如果存在），否则输出端口已清理的信息
echo "正在清理端口 3000..."
# kill $(lsof -t -i:3000 -nP -sTCP:LISTEN 2>/dev/null) 2>/dev/null || echo "3000 端口已干净"
pkill -f doris_mcp_server.main
echo "休眠一小段时间，再强制清理进程..."
sleep 25
pkill -9 -f doris_mcp_server.main
